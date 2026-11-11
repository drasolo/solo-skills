"""One referee run: load the board, read new commands and commits, apply the rules, write back.

Runs on every issue comment, every push and once an hour. GitHub keeps at most one run waiting,
so a run never assumes it was started for one comment: it reads everything posted since the
last run, oldest first.
"""

import json
import os
import sys
from datetime import UTC, datetime, timedelta

from referee import commands, rules
from referee.github import GitHub, Project
from referee.state import iso, parse_time, render_body, world_from_api


def main() -> int:
    repo, token = os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"]
    project_token = os.environ.get("PROJECT_TOKEN", "")
    now = datetime.now(UTC)
    gh = GitHub(repo, token)

    try:
        world = world_from_api(gh.load_issues())
    except LookupError as e:
        print(f"referee: {e}")
        return 0
    before = {n: json.dumps(i.state, sort_keys=True) for n, i in world.issues.items()}
    p = world.pinned.state

    last_sweep = parse_time(p.get("last_sweep")) or now - timedelta(days=30)
    comments = [c for c in gh.comments_since(last_sweep - timedelta(hours=1))
                if c["id"] > p.get("last_comment_id", 0)]
    cmds = [c for c in map(commands.from_api, comments) if c]
    last_commits = parse_time(p.get("last_commit_check")) or now - timedelta(days=1)
    commits = gh.commits_since(last_commits)

    effects = rules.sweep(world, cmds, commits, now)
    if comments:
        p["last_comment_id"] = max(c["id"] for c in comments)
    p["last_commit_check"] = iso(now)

    project = Project(world.pinned.fields.get("project", ""), project_token)
    if not project.ok and world.pinned.fields.get("project") and not p.get("project_off_noted"):
        p["project_off_noted"] = True
        effects.append({"do": "comment", "issue": world.pinned.number, "text":
                        "The referee has no PROJECT_TOKEN secret, so it assigns and labels issues "
                        "but cannot update the Project's fields. The manager adds the token as "
                        f"described in the setup.\n\n{commands.MARK}"})

    changed = [i for n, i in world.issues.items()
               if json.dumps(i.state, sort_keys=True) != before[n]]
    effects += [{"do": "body", "issue": i.number, "body": render_body(i.body, i.state)}
                for i in changed]
    gh.apply(effects)

    if project.ok:
        for t in (i for i in changed if i.kind == "task"):
            project.mirror(t)

    print(f"referee: {len(cmds)} commands, {len(commits)} commits, {len(effects)} effects")
    return 0


if __name__ == "__main__":
    sys.exit(main())
