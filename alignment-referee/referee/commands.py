"""Reading commands out of issue comments.

A command is the first line of a comment that starts with a slash:

    /claim implement
    Taking the parser. [Ana / Codex]

The signature in square brackets names the person and the agent acting for them. GitHub only
knows the account that posted, so the signature is how two agents of one person stay apart.
Comments the referee wrote itself carry MARK and are never read as commands.
"""

import re
from dataclasses import dataclass

MARK = "<!-- referee-reply -->"
VERBS = {"claim", "renew", "done", "stuck", "release", "keep", "changes", "vote", "drop", "ready"}
SIGNATURE = re.compile(r"\[(?P<person>[^\[\]/]+?)\s*/\s*(?P<agent>[^\[\]]+?)\]")
ISSUE_NUMBER = re.compile(r"/issues/(\d+)$")


@dataclass
class Command:
    comment_id: int
    issue: int
    login: str
    created_at: str
    verb: str
    args: list[str]
    person: str
    agent: str

    @property
    def signature(self) -> str:
        return f"{self.person} / {self.agent}"


def parse(comment_id: int, issue: int, login: str, created_at: str, body: str) -> Command | None:
    if not body or MARK in body:
        return None
    line = next((ln.strip() for ln in body.splitlines() if ln.strip().startswith("/")), None)
    if line is None:
        return None
    words = SIGNATURE.sub(" ", line)[1:].split()
    if not words or words[0].lower() not in VERBS:
        return None
    sigs = list(SIGNATURE.finditer(body))
    if sigs:
        person, agent = sigs[-1]["person"].strip(), sigs[-1]["agent"].strip()
    else:
        person, agent = login, "human"
    return Command(comment_id=comment_id, issue=issue, login=login.lower(),
                   created_at=created_at, verb=words[0].lower(),
                   args=words[1:], person=person,
                   agent=agent)


def from_api(comment: dict) -> Command | None:
    m = ISSUE_NUMBER.search(comment.get("issue_url", ""))
    if not m:
        return None
    return parse(comment["id"], int(m[1]), comment["user"]["login"], comment["created_at"],
                 comment.get("body") or "")
