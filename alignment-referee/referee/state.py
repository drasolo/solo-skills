"""The board as the referee sees it: issues, their fields, and the referee's own state.

Every issue the referee cares about carries a label that says what it is:

    task       work someone claims
    decision   a question the team votes on
    alignment  the pinned issue: goal, Vision, people, glossary, settings
    review     a conflict or surprise a person has to clear

People write fields in the issue body as bold labels, one per line:

    **Paths:** src/model/, docs/plan.md
    **Decisions:** D-4, D-7

The referee keeps what it decides in a hidden block at the end of the body,
<!-- referee:{...} -->, so a clean clone of the code repo never holds any of it.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

FIELD = re.compile(r"^\*\*(?P<key>[^*\n]+?):\*\*[ \t]*(?P<value>.*)$", re.MULTILINE)
BLOCK = re.compile(r"\n*<!-- referee:(?P<json>\{.*?\}) -->", re.DOTALL)
PERSON = re.compile(r"@(?P<login>[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)(?P<manager>\s*\(manager\))?")
KINDS = ("task", "decision", "alignment", "review")

TASK_DEFAULT = {"status": "To do", "stage": 0, "owner": None, "agent": None,
                "lease_until": None, "waits_on": None, "recheck": False, "history": []}
DECISION_DEFAULT = {"state": "proposed", "votes": {}, "tie_noted": False,
                    "deadline_noted": False, "outcome": None}
PINNED_DEFAULT = {"ready": [], "revealed": False, "last_comment_id": 0,
                  "last_sweep": None, "last_commit_check": None}


def ref(kind: str, number: int) -> str:
    return f"{'D' if kind == 'decision' else 'T'}-{number}"


def parse_fields(body: str) -> dict[str, str]:
    body = BLOCK.sub("", body or "")
    return {m["key"].strip().lower(): m["value"].strip() for m in FIELD.finditer(body)}


def parse_state(body: str) -> dict:
    m = BLOCK.search(body or "")
    if not m:
        return {}
    try:
        return json.loads(m["json"])
    except json.JSONDecodeError:
        return {}


def render_body(body: str, state: dict) -> str:
    """The body with the referee block replaced. Text people wrote is kept as it was."""
    clean = BLOCK.sub("", body or "").rstrip()
    return f"{clean}\n\n<!-- referee:{json.dumps(state, sort_keys=True)} -->"


def parse_paths(value: str) -> list[str]:
    if not value or value.strip().lower() in ("none", "-"):
        return []
    out = []
    for raw in value.split(","):
        p = raw.strip().strip("`").replace("\\", "/")
        while p.startswith("./"):
            p = p[2:]
        p = p.rstrip("/")
        if p:
            out.append(p)
    return out


def paths_overlap(a: list[str], b: list[str]) -> list[str]:
    """Pairs where one path is the other, or a folder holding it."""
    hits = []
    for x in a:
        for y in b:
            if x == y or x.startswith(y + "/") or y.startswith(x + "/"):
                hits.append(x if len(x) >= len(y) else y)
    return sorted(set(hits))


def parse_refs(value: str, prefix: str) -> list[str]:
    return [f"{prefix}-{n}" for n in re.findall(rf"\b{prefix}-(\d+)\b", value or "")]


def normalise_title(title: str) -> str:
    t = re.sub(r"\b[TD]-\d+\b", " ", title.lower())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


def parse_duration(value: str, default: timedelta) -> timedelta:
    m = re.fullmatch(r"\s*(\d+)\s*([mhd])\w*\s*", value or "")
    if not m:
        return default
    n, unit = int(m[1]), m[2]
    return {"m": timedelta(minutes=n), "h": timedelta(hours=n), "d": timedelta(days=n)}[unit]


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso(t: datetime) -> str:
    return t.isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass
class Issue:
    number: int
    kind: str
    title: str
    body: str
    open: bool
    labels: set[str]
    url: str = ""
    fields: dict = field(default_factory=dict)
    state: dict = field(default_factory=dict)

    @property
    def ref(self) -> str:
        return ref(self.kind, self.number)

    # task fields
    @property
    def paths(self) -> list[str]:
        return parse_paths(self.fields.get("paths", ""))

    @property
    def decisions(self) -> list[str]:
        return parse_refs(self.fields.get("decisions", ""), "D")

    @property
    def stages(self) -> list[str]:
        raw = [s.strip().lower() for s in self.fields.get("stages", "").split(",")]
        return [s for s in raw if s] or ["implement"]

    @property
    def stage_name(self) -> str:
        i = self.state.get("stage", 0)
        return self.stages[min(i, len(self.stages) - 1)]

    # decision fields
    @property
    def people(self) -> list[str]:
        return [m["login"].lower() for m in PERSON.finditer(self.fields.get("people", ""))]

    @property
    def verbal(self) -> bool:
        return self.fields.get("source", "").lower().startswith("verbal")

    @property
    def goal_change(self) -> bool:
        return self.fields.get("goal change", "").lower() in ("yes", "true")

    @property
    def supersedes(self) -> list[str]:
        return parse_refs(self.fields.get("supersedes", ""), "D")


def issue_from_api(data: dict) -> Issue | None:
    """One issue from the GitHub REST shape, or None when the referee does not track it."""
    if "pull_request" in data:
        return None
    labels = {lab["name"] if isinstance(lab, dict) else lab for lab in data.get("labels", [])}
    kind = next((k for k in KINDS if k in labels), None)
    if kind is None:
        return None
    body = data.get("body") or ""
    default = {"task": TASK_DEFAULT, "decision": DECISION_DEFAULT,
               "alignment": PINNED_DEFAULT}.get(kind, {})
    state = json.loads(json.dumps(default)) | parse_state(body)
    return Issue(number=data["number"], kind=kind, title=data.get("title", ""), body=body,
                 open=data.get("state", "open") == "open", labels=labels,
                 url=data.get("html_url", ""), fields=parse_fields(body), state=state)


@dataclass
class World:
    issues: dict[int, Issue]
    pinned: Issue
    lease: timedelta

    @property
    def people(self) -> list[str]:
        return [m["login"].lower() for m in PERSON.finditer(self.pinned.fields.get("people", ""))]

    @property
    def manager(self) -> str | None:
        for m in PERSON.finditer(self.pinned.fields.get("people", "")):
            if m["manager"]:
                return m["login"].lower()
        return None

    def get(self, reference: str) -> Issue | None:
        m = re.fullmatch(r"([TD])-(\d+)", reference.strip().upper())
        if not m:
            return None
        issue = self.issues.get(int(m[2]))
        want = "decision" if m[1] == "D" else "task"
        return issue if issue and issue.kind == want else None

    def tasks(self) -> list[Issue]:
        return [i for i in self.issues.values() if i.kind == "task" and i.open]


def world_from_api(issues: list[dict]) -> World:
    tracked = [i for i in (issue_from_api(d) for d in issues) if i]
    pinned = [i for i in tracked if i.kind == "alignment" and i.open]
    if not pinned:
        raise LookupError("no open issue labelled 'alignment'; run the kickoff first")
    p = min(pinned, key=lambda i: i.number)
    lease = parse_duration(p.fields.get("lease", ""), timedelta(hours=2))
    return World(issues={i.number: i for i in tracked}, pinned=p, lease=lease)
