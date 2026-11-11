"""The referee's rules. Pure: reads the world and commands, changes the world, lists effects.

Nothing in this file talks to GitHub, so every rule can be tested with recorded payloads.
`sweep` is the whole run: commands oldest first, then the timed checks, then the push check.
"""

import re
from collections import Counter
from datetime import datetime

from referee.commands import MARK, Command
from referee.state import Issue, World, iso, normalise_title, parse_time, paths_overlap

WORKING, STUCK, TODO, DONE = "Working on it", "Stuck", "To do", "Done"
TASK_VERBS = {"claim", "renew", "done", "stuck", "release", "keep", "changes"}
STATUS_LABELS = {WORKING: "working", STUCK: "stuck"}


class Referee:
    def __init__(self, world: World, now: datetime):
        self.w = world
        self.now = now
        self.effects: list[dict] = []

    # effects -----------------------------------------------------------------------------

    def say(self, issue: int, text: str) -> None:
        self.effects.append({"do": "comment", "issue": issue, "text": f"{text}\n\n{MARK}"})

    def labels(self, issue: Issue, add=(), remove=()) -> None:
        add = [x for x in add if x not in issue.labels]
        remove = [x for x in remove if x in issue.labels]
        issue.labels |= set(add)
        issue.labels -= set(remove)
        if add:
            self.effects.append({"do": "labels_add", "issue": issue.number, "labels": add})
        for lab in remove:
            self.effects.append({"do": "label_remove", "issue": issue.number, "label": lab})

    def accept(self, cmd: Command) -> None:
        self.effects.append({"do": "react", "issue": cmd.issue, "comment_id": cmd.comment_id,
                             "content": "+1"})

    def refuse(self, cmd: Command, why: str) -> None:
        self.effects.append({"do": "react", "issue": cmd.issue, "comment_id": cmd.comment_id,
                             "content": "-1"})
        self.say(cmd.issue, f"Refused `/{cmd.verb}` from [{cmd.signature}]: {why}")

    def set_status(self, t: Issue, status: str) -> None:
        t.state["status"] = status
        self.labels(t, add=[STATUS_LABELS[status]] if status in STATUS_LABELS else [],
                    remove=[v for k, v in STATUS_LABELS.items() if k != status])

    def free(self, t: Issue) -> None:
        """Back to To do with nobody on it."""
        owner = t.state.get("owner")
        if owner:
            self.effects.append({"do": "unassign", "issue": t.number, "login": owner["login"]})
        t.state.update(owner=None, agent=None, lease_until=None, waits_on=None)
        self.set_status(t, TODO)

    # the run -----------------------------------------------------------------------------

    def sweep(self, commands: list[Command], commits: list[dict] = ()) -> list[dict]:
        for cmd in sorted(commands, key=lambda c: c.comment_id):
            self.handle(cmd)
        self.expire_leases()
        self.note_deadlines()
        for c in commits:
            self.check_commit(c)
        self.w.pinned.state["last_sweep"] = iso(self.now)
        return self.effects

    def handle(self, cmd: Command) -> None:
        issue = self.w.issues.get(cmd.issue)
        if issue is None:
            return
        if issue.kind == "task" and cmd.verb in TASK_VERBS:
            getattr(self, cmd.verb)(issue, cmd)
        elif issue.kind == "decision" and cmd.verb in ("vote", "drop"):
            getattr(self, cmd.verb)(issue, cmd)
        elif issue.kind == "alignment" and cmd.verb == "ready":
            self.ready(issue, cmd)
        else:
            self.refuse(cmd, f"`/{cmd.verb}` does not apply to a {issue.kind} issue.")

    # task commands -----------------------------------------------------------------------

    def is_owner(self, t: Issue, cmd: Command) -> bool:
        owner = t.state.get("owner")
        if not owner or owner["login"] != cmd.login:
            return False
        return cmd.agent == "human" or cmd.signature.lower() == owner["signature"].lower()

    def owner_name(self, t: Issue) -> str:
        owner = t.state.get("owner")
        return f"[{owner['signature']}]" if owner else "nobody"

    def overlaps(self, t: Issue) -> list[str]:
        found = []
        title = normalise_title(t.title)
        for o in self.w.tasks():
            if o.number == t.number or o.state.get("status") not in (WORKING, STUCK):
                continue
            why = []
            if title and normalise_title(o.title) == title:
                why.append("same title")
            if hit := paths_overlap(t.paths, o.paths):
                why.append("paths " + ", ".join(hit))
            if shared := sorted(set(t.decisions) & set(o.decisions)):
                why.append("decisions " + ", ".join(shared))
            if why:
                found.append(f"{o.ref} (owned by {self.owner_name(o)}): {'; '.join(why)}")
        return found

    def claim(self, t: Issue, cmd: Command) -> None:
        status = t.state["status"]
        if not t.open:
            return self.refuse(cmd, f"{t.ref} is closed.")
        if t.state.get("recheck"):
            return self.refuse(cmd, f"the goal changed. The owner or the manager answers "
                                    f"`/keep` or `/release` on {t.ref} first.")
        if status != TODO:
            return self.refuse(cmd, f"{t.ref} is {status}, owned by {self.owner_name(t)}.")
        stage = t.stage_name
        if cmd.args and cmd.args[0].lower() != stage:
            return self.refuse(cmd, f"the next stage of {t.ref} is `{stage}`.")
        if stage == "review":
            builders = {h["agent"].lower() for h in t.state["history"] if h["stage"] == "implement"}
            if cmd.agent.lower() in builders - {"human"}:
                return self.refuse(cmd, f"review must come from another agent than the one that "
                                        f"implemented it ({cmd.agent}).")
        if found := self.overlaps(t):
            return self.refuse(cmd, "overlaps " + " | ".join(found))
        self.accept(cmd)
        t.state.update(owner={"login": cmd.login, "signature": cmd.signature}, agent=cmd.agent,
                       lease_until=iso(self.now + self.w.lease))
        t.state["history"].append({"stage": stage, "login": cmd.login, "agent": cmd.agent,
                                   "signature": cmd.signature, "at": cmd.created_at})
        self.effects.append({"do": "assign", "issue": t.number, "login": cmd.login})
        self.set_status(t, WORKING)

    def renew(self, t: Issue, cmd: Command) -> None:
        if not self.is_owner(t, cmd) or t.state["status"] != WORKING:
            return self.refuse(cmd, f"only the owner of a task in progress renews it; {t.ref} is "
                                    f"{t.state['status']}, owned by {self.owner_name(t)}.")
        self.accept(cmd)
        t.state["lease_until"] = iso(self.now + self.w.lease)

    def done(self, t: Issue, cmd: Command) -> None:
        if not self.is_owner(t, cmd) or t.state["status"] != WORKING:
            return self.refuse(cmd, f"only the owner of a task in progress finishes it; {t.ref} "
                                    f"is {t.state['status']}, owned by {self.owner_name(t)}.")
        if t.state.get("recheck"):
            return self.refuse(cmd, f"the goal changed. Answer `/keep` or `/release` first.")
        self.accept(cmd)
        stage, nxt = t.state["stage"], t.state["stage"] + 1
        if nxt < len(t.stages):
            self.free(t)
            t.state["stage"] = nxt
            self.say(t.number, f"Stage `{t.stages[stage]}` of {t.ref} is done. Next stage: "
                               f"`{t.stages[nxt]}`, free to claim.")
            return
        owner = t.state["owner"]
        self.effects.append({"do": "unassign", "issue": t.number, "login": owner["login"]})
        t.state.update(lease_until=None)
        self.set_status(t, DONE)
        t.open = False
        self.effects.append({"do": "close", "issue": t.number})
        self.resume_waiting(t.ref)

    def stuck(self, t: Issue, cmd: Command) -> None:
        if not self.is_owner(t, cmd) or t.state["status"] != WORKING:
            return self.refuse(cmd, f"only the owner of a task in progress marks it stuck.")
        target = self.w.get(cmd.args[0]) if cmd.args else None
        if target is None:
            return self.refuse(cmd, "name the decision or task it waits on, like `/stuck D-12`. "
                                    f"`{' '.join(cmd.args) or 'nothing'}` is not one.")
        if self.settled(target):
            return self.refuse(cmd, f"{target.ref} is already settled.")
        self.accept(cmd)
        t.state.update(waits_on=target.ref, lease_until=None)
        self.set_status(t, STUCK)

    def release(self, t: Issue, cmd: Command) -> None:
        if not (self.is_owner(t, cmd) or cmd.login == self.w.manager):
            return self.refuse(cmd, f"only the owner or the manager releases {t.ref}.")
        self.accept(cmd)
        self.free(t)
        self.clear_recheck(t)

    def keep(self, t: Issue, cmd: Command) -> None:
        if not t.state.get("recheck"):
            return self.refuse(cmd, f"{t.ref} is not marked recheck.")
        if not (self.is_owner(t, cmd) or cmd.login == self.w.manager):
            return self.refuse(cmd, f"only the owner or the manager keeps {t.ref}.")
        self.accept(cmd)
        self.clear_recheck(t)

    def changes(self, t: Issue, cmd: Command) -> None:
        if t.stage_name != "review" or not self.is_owner(t, cmd) or t.state["status"] != WORKING:
            return self.refuse(cmd, "only the reviewer of a task in review asks for changes.")
        if "implement" not in t.stages:
            return self.refuse(cmd, f"{t.ref} has no implement stage to reopen.")
        self.accept(cmd)
        self.free(t)
        t.state["stage"] = t.stages.index("implement")
        self.say(t.number, f"Changes requested on {t.ref}. The implement stage is open again; "
                           "the reasons are in the comment above.")

    def clear_recheck(self, t: Issue) -> None:
        t.state["recheck"] = False
        self.labels(t, remove=["recheck"])

    # decisions ---------------------------------------------------------------------------

    def settled(self, issue: Issue) -> bool:
        if issue.kind == "decision":
            return issue.state["state"] != "proposed"
        return issue.state.get("status") == DONE or not issue.open

    def voters(self, d: Issue) -> list[str]:
        return d.people or self.w.people

    def vote(self, d: Issue, cmd: Command) -> None:
        if d.state["state"] != "proposed":
            return self.refuse(cmd, f"{d.ref} is {d.state['state']}. To change it, open a new "
                                    f"decision that supersedes it.")
        if cmd.login not in self.voters(d):
            return self.refuse(cmd, f"@{cmd.login} is not one of the people in {d.ref}.")
        if not cmd.args:
            return self.refuse(cmd, "say which option, like `/vote B`.")
        self.accept(cmd)
        d.state["votes"][cmd.login] = cmd.args[0].lower()
        self.evaluate(d)

    def evaluate(self, d: Issue) -> None:
        voters = self.voters(d)
        votes = {k: v for k, v in d.state["votes"].items() if k in voters}
        counts = Counter(votes.values())
        tally = ", ".join(f"{opt}: {n}" for opt, n in counts.most_common())
        if d.verbal:
            if len(votes) == len(voters) and len(counts) == 1:
                return self.decide(d, next(iter(counts)), tally)
            return
        top = counts.most_common(1)
        if top and top[0][1] > len(voters) / 2:
            return self.decide(d, top[0][0], tally)
        if len(votes) == len(voters) and not d.state["tie_noted"]:
            d.state["tie_noted"] = True
            self.say(d.number, f"Everyone voted and no option has a majority ({tally}). {d.ref} "
                               "stays open. Agents follow the manager's Vision meanwhile.")

    def decide(self, d: Issue, option: str, tally: str) -> None:
        d.state.update(state="decided", outcome=option)
        self.labels(d, add=["decided"], remove=["proposed"])
        self.say(d.number, f"Decided: `{option}` ({tally}). Agents may act on {d.ref}.")
        for old_ref in d.supersedes:
            old = self.w.get(old_ref)
            if old and old.state["state"] != "superseded":
                old.state["state"] = "superseded"
                self.labels(old, add=["superseded"], remove=["decided", "proposed"])
                self.say(old.number, f"Superseded by {d.ref}. Agents stop acting on {old.ref}.")
        if d.goal_change:
            marked = []
            for t in self.w.tasks():
                if t.state.get("status") != DONE:
                    t.state["recheck"] = True
                    self.labels(t, add=["recheck"])
                    marked.append(t.ref)
            self.say(self.w.pinned.number,
                     f"The goal changed with {d.ref}. Marked recheck: {', '.join(marked) or 'none'}."
                     " Each owner answers `/keep` or `/release`; unowned ones go to the manager.")
        self.resume_waiting(d.ref)

    def drop(self, d: Issue, cmd: Command) -> None:
        if cmd.login != self.w.manager:
            return self.refuse(cmd, "only the manager drops a decision.")
        if d.state["state"] != "proposed":
            return self.refuse(cmd, f"{d.ref} is already {d.state['state']}.")
        self.accept(cmd)
        d.state["state"] = "dropped"
        self.labels(d, add=["dropped"], remove=["proposed"])
        self.resume_waiting(d.ref)

    def resume_waiting(self, reference: str) -> None:
        for t in self.w.tasks():
            if t.state.get("status") == STUCK and t.state.get("waits_on") == reference:
                t.state.update(waits_on=None, lease_until=iso(self.now + self.w.lease))
                self.set_status(t, WORKING)
                self.say(t.number, f"{reference} is settled, so {t.ref} is back to Working on it "
                                   f"with a fresh lease, owned by {self.owner_name(t)}.")

    # kickoff -----------------------------------------------------------------------------

    def ready(self, p: Issue, cmd: Command) -> None:
        people = self.w.people
        if cmd.login not in people:
            return self.refuse(cmd, f"@{cmd.login} is not in the People list.")
        if p.state["revealed"]:
            return self.refuse(cmd, "the answers were already revealed.")
        self.accept(cmd)
        if cmd.login not in p.state["ready"]:
            p.state["ready"].append(cmd.login)
        if set(people) <= set(p.state["ready"]):
            p.state["revealed"] = True
            self.say(p.number, "Reveal: everyone is ready. Post your kickoff answers now.")

    # timed checks ------------------------------------------------------------------------

    def expire_leases(self) -> None:
        for t in self.w.tasks():
            until = parse_time(t.state.get("lease_until"))
            if t.state.get("status") == WORKING and until and until < self.now:
                who = self.owner_name(t)
                self.free(t)
                self.say(t.number, f"The lease of {who} ran out at {iso(until)}. {t.ref} is back "
                                   "to To do.")

    def note_deadlines(self) -> None:
        today = self.now.date().isoformat()
        for d in self.w.issues.values():
            deadline = d.fields.get("deadline", "")[:10] if d.kind == "decision" else ""
            if (d.open and deadline and deadline < today and d.state["state"] == "proposed"
                    and not d.state["deadline_noted"]):
                d.state["deadline_noted"] = True
                self.say(d.number, f"The deadline ({deadline}) passed without a majority. "
                                   f"{d.ref} stays open; agents follow the manager's Vision.")

    def check_commit(self, c: dict) -> None:
        """A commit with no task ID that touches paths another person's task has claimed."""
        if re.search(r"\bT-\d+\b", c.get("message", "")):
            return
        hits = []
        for t in self.w.tasks():
            owner = t.state.get("owner")
            if t.state.get("status") in (WORKING, STUCK) and owner and owner["login"] != c["login"]:
                if found := paths_overlap(c.get("files", []), t.paths):
                    hits.append((t, owner, found))
        if not hits:
            return
        sha = c["sha"][:7]
        lines = [f"- {t.ref}, owned by [{o['signature']}] (@{o['login']}): {', '.join(f)}"
                 for t, o, f in hits]
        self.effects.append({
            "do": "create_issue", "labels": ["review"],
            "title": f"Commit {sha} has no task ID and touches claimed paths",
            "body": f"@{c['login']} pushed {sha} without a task ID. It touches paths these tasks "
                    "claimed:\n\n" + "\n".join(lines) + "\n\nA person clears this: link the "
                    "commit to a task, or agree who owns the change.\n\n" + MARK})


def sweep(world: World, commands: list[Command], commits: list[dict], now: datetime):
    return Referee(world, now).sweep(commands, commits)
