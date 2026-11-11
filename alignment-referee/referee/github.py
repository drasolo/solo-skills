"""Everything that talks to GitHub, through the gh CLI that every Actions runner has.

Two tokens: GH_TOKEN (the workflow's own token) reads and writes issues; PROJECT_TOKEN, when
the manager stored one, edits the GitHub Project, which the workflow's own token cannot do for
a Project owned by a user.
"""

import json
import os
import re
import shlex
import subprocess
from datetime import UTC, datetime

from referee.state import Issue, iso

PROJECT_URL = re.compile(r"github\.com/(?:users|orgs)/(?P<owner>[^/\s]+)/projects/(?P<number>\d+)")


def run_gh(args: list[str], token: str, payload: dict | None = None) -> str:
    env = os.environ | {"GH_TOKEN": token}
    done = subprocess.run([*shlex.split(os.environ.get("GH_BIN", "gh")), *args], env=env, capture_output=True, text=True,
                          input=json.dumps(payload) if payload is not None else None)
    if done.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {done.stderr.strip()[:500]}")
    return done.stdout


class GitHub:
    def __init__(self, repo: str, token: str):
        self.repo = repo
        self.token = token

    def get(self, path: str) -> list | dict:
        out = run_gh(["api", "--paginate", "--slurp", path], self.token)
        pages = json.loads(out)
        if pages and isinstance(pages[0], list):
            return [item for page in pages for item in page]
        return pages[0] if pages else {}

    def send(self, method: str, path: str, payload: dict | None = None) -> None:
        args = ["api", "--method", method, path]
        if payload is not None:
            args += ["--input", "-"]
        run_gh(args, self.token, payload)

    def load_issues(self) -> list[dict]:
        seen = {}
        for label in ("alignment", "task", "decision", "review"):
            for issue in self.get(f"repos/{self.repo}/issues?state=all&labels={label}&per_page=100"):
                seen[issue["number"]] = issue
        return list(seen.values())

    def comments_since(self, since: datetime) -> list[dict]:
        return self.get(f"repos/{self.repo}/issues/comments?since={iso(since)}"
                        "&sort=created&direction=asc&per_page=100")

    def commits_since(self, since: datetime) -> list[dict]:
        out = []
        for c in self.get(f"repos/{self.repo}/commits?since={iso(since)}&per_page=100"):
            full = self.get(f"repos/{self.repo}/commits/{c['sha']}")
            out.append({"sha": c["sha"], "message": c["commit"]["message"],
                        "login": ((c.get("author") or {}).get("login") or "").lower(),
                        "files": [f["filename"] for f in full.get("files", [])]})
        return out

    def apply(self, effects: list[dict]) -> None:
        r = f"repos/{self.repo}"
        for e in effects:
            n = e.get("issue")
            match e["do"]:
                case "comment":
                    self.send("POST", f"{r}/issues/{n}/comments", {"body": e["text"]})
                case "react":
                    self.send("POST", f"{r}/issues/comments/{e['comment_id']}/reactions",
                              {"content": e["content"]})
                case "labels_add":
                    self.send("POST", f"{r}/issues/{n}/labels", {"labels": e["labels"]})
                case "label_remove":
                    self.send("DELETE", f"{r}/issues/{n}/labels/{e['label']}")
                case "assign":
                    self.send("POST", f"{r}/issues/{n}/assignees", {"assignees": [e["login"]]})
                case "unassign":
                    self.send("DELETE", f"{r}/issues/{n}/assignees", {"assignees": [e["login"]]})
                case "close":
                    self.send("PATCH", f"{r}/issues/{n}",
                              {"state": "closed", "state_reason": "completed"})
                case "body":
                    self.send("PATCH", f"{r}/issues/{n}", {"body": e["body"]})
                case "create_issue":
                    self.send("POST", f"{r}/issues", {"title": e["title"], "body": e["body"],
                                                      "labels": e["labels"]})


class Project:
    """Mirrors task state into a GitHub Project. Fields it does not find are skipped."""

    def __init__(self, url_text: str, token: str):
        m = PROJECT_URL.search(url_text or "")
        self.ok = bool(m and token)
        if not self.ok:
            return
        self.owner, self.number, self.token = m["owner"], m["number"], token
        view = json.loads(self.gh("view", self.number))
        self.id = view["id"]
        self.fields = {f["name"].lower(): f
                       for f in json.loads(self.gh("field-list", self.number))["fields"]}

    def gh(self, *args: str) -> str:
        return run_gh(["project", *args, "--owner", self.owner, "--format", "json"], self.token)

    def mirror(self, t: Issue) -> None:
        item = json.loads(self.gh("item-add", self.number, "--url", t.url))["id"]
        owner = t.state.get("owner")
        values = {
            "task status": t.state.get("status"),
            "status": t.state.get("status"),
            "owner": owner["signature"] if owner else "",
            "stage": t.stage_name,
            "lease": t.state.get("lease_until") or "",
            "waits on": t.state.get("waits_on") or "",
            "last updated": iso(datetime.now(UTC)),
            "criterion": t.fields.get("criterion", ""),
            "scope": ", ".join(t.paths + t.decisions),
            "agent / model": t.fields.get("agent / model", ""),
        }
        for name, value in values.items():
            f = self.fields.get(name)
            if f is None or value is None:
                continue
            args = ["project", "item-edit", "--id", item, "--project-id", self.id,
                    "--field-id", f["id"]]
            options = {o["name"].lower(): o["id"] for o in f.get("options", [])}
            if options:
                if value.lower() not in options:
                    continue
                args += ["--single-select-option-id", options[value.lower()]]
            else:
                args += ["--text", value]
            run_gh(args, self.token)
