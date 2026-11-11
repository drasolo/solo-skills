---
name: alignment-grill
description: Keep a team of people and AI agents aligned on goal, decisions, facts and words, with a GitHub issue board that stops two agents doing the same work.
disable-model-invocation: true
---

Align the people and agents on one project through a **record** that lives on GitHub, never in the code: a pinned issue (goal, Vision, people, glossary, stack defaults, rules for agents), `task` issues, `decision` issues and `review` issues, mirrored into a GitHub Project. A **referee** Action is the only writer of task state. People and agents talk to it with comment commands.

Agents act only on **decided** lines and cite their IDs (`D-n` for decisions, `T-n` for tasks). A `proposed` decision is a question, never an instruction.

## Before any mode

1. Confirm the project is a GitHub repo and `gh` is logged in: `gh repo view --json nameWithOwner` and `gh auth status`. If either fails, or the project lives on another host, say plainly that v1 of this skill works on GitHub only, and stop.
2. Find the pinned issue: `gh issue list --label alignment --state open`. None means the project has not had a kickoff.
3. Work out who you act for: the person in this session, and the agent name of the harness you run in (Claude, Codex, Antigravity, ...). Sign every command comment `[Person / Agent]`.

Done when you know the repo, whether a kickoff happened, and your signature.

## Pick the mode

| The person wants to | Mode | Read |
|---|---|---|
| Start alignment on a project, join a kickoff, or start a new phase after the goal was met | kickoff | [references/modes/kickoff.md](references/modes/kickoff.md) |
| Settle a question, record a verbal agreement, or change the goal | decide | [references/modes/decide.md](references/modes/decide.md) |
| Check that work matches the record, before a claim or before done | check | [references/modes/check.md](references/modes/check.md) |
| Defend a decision or a result they own | defend | [references/modes/defend.md](references/modes/defend.md) |
| Add a task, log work done without one, or claim | (board work) | [references/board.md](references/board.md) |

If it is unclear, ask which one, with your recommendation. Read [references/board.md](references/board.md) in every mode that writes to GitHub: it holds the command grammar and the issue formats.

## The profile

Every project has one context, named in the pinned issue's **Context:** field: hackathon, solo-many-agents, uni-group, work-long, research-thesis, client, open-source, incident. Read its file in [references/profiles/](references/profiles/) before asking any question. It sets the lease length, extra task fields, the default grouping, extra kickoff questions, who votes and the default decision deadline.

## Who decides what

- An agent decides alone only inside its own task. Anything another person or task depends on (shared files, interfaces, data formats, names, the goal) is a team decision a human owns.
- Agents that conflict: the manager's line wins.
- People who conflict: majority vote of the people involved. A tie stays open, and agents follow the manager's Vision meanwhile.
- Every conflict an agent resolves by falling back on the Vision becomes a `review` issue, which a person clears.

## Grill format

Grill people in **rounds**. The frontier is every question whose prerequisites are settled; ask the whole frontier in one round, numbered, each with your recommendation, worded so "yes" accepts it:

```
**Q1. <title>.** <question, with the concrete choices and what each costs>

Recommended: <your answer and the reason>
```

Then wait. Facts are your job: find them yourself or with sub-agents, from the repo, the issues and the commit history. Decisions belong to people: put each one to them. Write to GitHub only what a person agreed to in this session, and show the text before posting it.
