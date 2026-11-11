"""The referee's rules against a board in GitHub's REST shape (tests/fixtures/board.json).

Run from the repo root: python -m unittest
"""

import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from referee import commands, rules
from referee.state import parse_state, render_body, world_from_api

BOARD = json.loads((Path(__file__).parent / "fixtures" / "board.json").read_text("utf-8"))
NOW = datetime(2026, 11, 12, 10, 0, tzinfo=UTC)


def comment(cid: int, issue: int, login: str, body: str) -> dict:
    """A comment as GET /repos/{repo}/issues/comments returns it."""
    return {"id": cid, "issue_url": f"https://api.github.com/repos/acme/demo/issues/{issue}",
            "user": {"login": login}, "created_at": "2026-11-12T09:00:00Z", "body": body}


class Board:
    def __init__(self):
        self.world = world_from_api(json.loads(json.dumps(BOARD["issues"])))
        self.effects = []
        self.next_id = 100

    def run(self, *posts, commits=(), now=NOW):
        cmds = []
        for issue, login, body in posts:
            self.next_id += 1
            cmds.append(commands.from_api(comment(self.next_id, issue, login, body)))
        self.effects = rules.sweep(self.world, [c for c in cmds if c], list(commits), now)
        return self.effects

    def task(self, n):
        return self.world.issues[n].state

    def said(self, issue, text):
        return any(e["do"] == "comment" and e["issue"] == issue and text in e["text"]
                   for e in self.effects)

    def reactions(self):
        return [e["content"] for e in self.effects if e["do"] == "react"]


class Parsing(unittest.TestCase):
    def test_board_keeps_only_tracked_issues(self):
        w = world_from_api(BOARD["issues"])
        self.assertNotIn(30, w.issues)  # pull request
        self.assertNotIn(31, w.issues)  # no tracking label
        self.assertEqual(w.manager, "ana")
        self.assertEqual(w.people, ["ana", "bo", "cy"])
        self.assertEqual(w.lease, timedelta(hours=2))
        self.assertEqual(w.issues[11].paths, ["src/parse/fast.py"])
        self.assertEqual(w.issues[12].stages, ["implement", "review"])

    def test_signature_on_the_command_line(self):
        c = commands.from_api(comment(1, 10, "Bo", "/claim implement [Bo / Codex]"))
        self.assertEqual((c.verb, c.args, c.person, c.agent, c.login),
                         ("claim", ["implement"], "Bo", "Codex", "bo"))

    def test_referee_replies_and_chat_are_not_commands(self):
        self.assertIsNone(commands.parse(1, 10, "ana", "", f"/claim\n{commands.MARK}"))
        self.assertIsNone(commands.parse(1, 10, "ana", "", "I'll /claim this later"))
        self.assertIsNone(commands.parse(1, 10, "ana", "", "/deploy now"))

    def test_state_block_round_trip_keeps_human_text(self):
        body = "**Paths:** a.py\n\nNotes by a person."
        out = render_body(render_body(body, {"status": "Done"}), {"status": "To do"})
        self.assertEqual(parse_state(out), {"status": "To do"})
        self.assertTrue(out.startswith(body))
        self.assertEqual(out.count("referee:"), 1)


class Claims(unittest.TestCase):
    def test_two_claims_on_one_file(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"), (11, "bo", "/claim [Bo / Codex]"))
        self.assertEqual(b.task(10)["status"], rules.WORKING)
        self.assertEqual(b.task(11)["status"], rules.TODO)
        self.assertEqual(b.reactions(), ["+1", "-1"])
        self.assertTrue(b.said(11, "overlaps T-10 (owned by [Ana / Claude]): paths src/parse/fast.py"))

    def test_same_title_is_refused(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"), (13, "bo", "/claim [Bo / Codex]"))
        self.assertTrue(b.said(13, "same title"))

    def test_sweep_takes_queued_comments_oldest_first(self):
        b = Board()
        posts = [comment(303, 10, "ana", "/claim [Ana / Claude]"),
                 comment(301, 11, "bo", "/claim [Bo / Codex]"),
                 comment(302, 11, "bo", "/renew [Bo / Codex]")]
        cmds = [commands.from_api(c) for c in posts]
        rules.sweep(b.world, cmds, [], NOW)
        self.assertEqual(b.task(11)["owner"]["signature"], "Bo / Codex")
        self.assertEqual(b.task(10)["status"], rules.TODO)

    def test_another_agent_of_the_same_person_is_not_the_owner(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"), (10, "ana", "/done [Ana / Codex]"))
        self.assertEqual(b.task(10)["status"], rules.WORKING)
        self.assertEqual(b.reactions(), ["+1", "-1"])

    def test_expired_lease_goes_back_to_to_do(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"))
        b.run(now=NOW + timedelta(hours=1))
        self.assertEqual(b.task(10)["status"], rules.WORKING)
        b.run(now=NOW + timedelta(hours=3))
        self.assertEqual(b.task(10)["status"], rules.TODO)
        self.assertIsNone(b.task(10)["owner"])
        self.assertTrue(b.said(10, "The lease of [Ana / Claude] ran out"))
        self.assertIn({"do": "unassign", "issue": 10, "login": "ana"}, b.effects)

    def test_renew_extends_the_lease(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"))
        b.run((10, "ana", "/renew [Ana / Claude]"), now=NOW + timedelta(hours=1, minutes=50))
        b.run(now=NOW + timedelta(hours=3))
        self.assertEqual(b.task(10)["status"], rules.WORKING)

    def test_done_closes_and_frees_the_paths(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"), (10, "ana", "/done [Ana / Claude]"),
              (11, "bo", "/claim [Bo / Codex]"))
        self.assertEqual(b.task(10)["status"], rules.DONE)
        self.assertIn({"do": "close", "issue": 10}, b.effects)
        self.assertEqual(b.task(11)["status"], rules.WORKING)


class Stuck(unittest.TestCase):
    def test_stuck_on_a_missing_decision_is_refused(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"), (10, "ana", "/stuck D-99 [Ana / Claude]"))
        self.assertEqual(b.task(10)["status"], rules.WORKING)
        self.assertTrue(b.said(10, "`D-99` is not one"))

    def test_stuck_task_resumes_when_the_decision_is_made(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"), (10, "ana", "/stuck D-20 [Ana / Claude]"))
        self.assertEqual(b.task(10)["status"], rules.STUCK)
        self.assertIn("stuck", b.world.issues[10].labels)
        b.run((20, "ana", "/vote B"), (20, "bo", "/vote b"))
        self.assertEqual(b.world.issues[20].state["state"], "decided")
        self.assertEqual(b.task(10)["status"], rules.WORKING)
        self.assertTrue(b.said(10, "D-20 is settled"))


class Votes(unittest.TestCase):
    def test_tie_stays_open(self):
        b = Board()
        b.run((20, "ana", "/vote A"), (20, "bo", "/vote B"))
        self.assertEqual(b.world.issues[20].state["state"], "proposed")
        self.assertTrue(b.said(20, "no option has a majority"))

    def test_majority_decides_and_supersedes(self):
        b = Board()
        b.run((20, "ana", "/vote A"), (20, "bo", "/vote A"))
        b.run((21, "ana", "/vote yes"), (21, "cy", "/vote yes"))
        self.assertEqual(b.world.issues[21].state["state"], "decided")
        self.assertEqual(b.world.issues[20].state["state"], "superseded")
        self.assertIn("superseded", b.world.issues[20].labels)

    def test_outsider_cannot_vote(self):
        b = Board()
        b.run((20, "cy", "/vote A"))
        self.assertTrue(b.said(20, "@cy is not one of the people in D-20"))

    def test_verbal_decision_needs_every_named_person(self):
        b = Board()
        b.run((22, "ana", "/vote yes"))
        self.assertEqual(b.world.issues[22].state["state"], "proposed")
        b.run((22, "bo", "/vote yes"))
        self.assertEqual(b.world.issues[22].state["state"], "decided")

    def test_deadline_noted_once(self):
        b = Board()
        b.run(now=datetime(2026, 11, 16, tzinfo=UTC))
        self.assertTrue(b.said(20, "deadline (2026-11-15) passed"))
        b.run(now=datetime(2026, 11, 17, tzinfo=UTC))
        self.assertFalse(b.said(20, "deadline"))

    def test_only_the_manager_drops(self):
        b = Board()
        b.run((20, "bo", "/drop"), (21, "ana", "/drop"))
        self.assertEqual(b.world.issues[20].state["state"], "proposed")
        self.assertEqual(b.world.issues[21].state["state"], "dropped")


class GoalChange(unittest.TestCase):
    def test_goal_change_marks_open_tasks_recheck(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"))
        b.run((23, "ana", "/vote yes"), (23, "bo", "/vote yes"))
        self.assertTrue(b.task(10)["recheck"])
        self.assertTrue(b.task(11)["recheck"])
        self.assertTrue(b.said(1, "The goal changed with D-23"))
        b.run((11, "bo", "/claim [Bo / Codex]"), (10, "ana", "/done [Ana / Claude]"))
        self.assertEqual(b.reactions(), ["-1", "-1"])
        b.run((10, "ana", "/keep [Ana / Claude]"), (11, "bo", "/keep"), (11, "ana", "/keep"))
        self.assertEqual(b.reactions(), ["+1", "-1", "+1"])  # bo owns nothing; ana manages
        self.assertFalse(b.task(10)["recheck"])
        self.assertFalse(b.task(11)["recheck"])


class Stages(unittest.TestCase):
    def test_review_must_be_another_agent(self):
        b = Board()
        b.run((12, "bo", "/claim implement [Bo / Codex]"), (12, "bo", "/done [Bo / Codex]"))
        self.assertEqual(b.task(12)["status"], rules.TODO)
        self.assertEqual(b.world.issues[12].stage_name, "review")
        b.run((12, "ana", "/claim review [Ana / Codex]"))
        self.assertTrue(b.said(12, "another agent"))
        self.assertEqual(b.reactions(), ["-1"])
        self.assertEqual(b.task(12)["status"], rules.TODO)
        b.run((12, "ana", "/claim review [Ana / Claude]"))
        self.assertEqual(b.task(12)["status"], rules.WORKING)

    def test_changes_reopen_implement(self):
        b = Board()
        b.run((12, "bo", "/claim [Bo / Codex]"), (12, "bo", "/done [Bo / Codex]"),
              (12, "ana", "/claim review [Ana / Claude]"), (12, "ana", "/changes [Ana / Claude]"))
        self.assertEqual(b.world.issues[12].stage_name, "implement")
        self.assertEqual(b.task(12)["status"], rules.TODO)
        b.run((12, "bo", "/claim review [Bo / Codex]"))
        self.assertTrue(b.said(12, "the next stage of T-12 is `implement`"))


class Kickoff(unittest.TestCase):
    def test_reveal_when_everyone_is_ready(self):
        b = Board()
        b.run((1, "ana", "/ready"), (1, "bo", "/ready"))
        self.assertFalse(b.world.pinned.state["revealed"])
        b.run((1, "zed", "/ready"), (1, "cy", "/ready"))
        self.assertTrue(b.said(1, "@zed is not in the People list"))
        self.assertTrue(b.world.pinned.state["revealed"])
        self.assertTrue(b.said(1, "Reveal: everyone is ready"))


class Pushes(unittest.TestCase):
    def commit(self, message, login="bo", files=("src/parse/reader.py",)):
        return {"sha": "abc1234def", "message": message, "login": login, "files": list(files)}

    def test_untracked_commit_on_claimed_paths_opens_a_review(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"))
        b.run(commits=[self.commit("quick fix")])
        made = [e for e in b.effects if e["do"] == "create_issue"]
        self.assertEqual(len(made), 1)
        self.assertEqual(made[0]["labels"], ["review"])
        self.assertIn("T-10, owned by [Ana / Claude] (@ana): src/parse/reader.py", made[0]["body"])

    def test_commits_that_are_fine(self):
        b = Board()
        b.run((10, "ana", "/claim [Ana / Claude]"))
        b.run(commits=[self.commit("T-10 quick fix"), self.commit("mine", login="ana"),
                       self.commit("docs", files=["docs/other.md"])])
        self.assertFalse([e for e in b.effects if e["do"] == "create_issue"])


if __name__ == "__main__":
    unittest.main()
