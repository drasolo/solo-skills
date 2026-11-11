# The board

Everything the referee reads. Fields are bold labels in an issue body, one per line. The
referee keeps its own state in a hidden `<!-- referee:{...} -->` block at the end of each body:
leave that block as it is when you edit a body.

IDs: a task is `T-<issue number>`, a decision is `D-<issue number>`.

## Commands

A command is the first line of a comment that starts with `/`, ending with the signature.

| Command | On | Who | Effect |
|---|---|---|---|
| `/claim [stage]` | task | anyone | Refused when another active task has the same title, overlapping paths or a shared decision. Otherwise you own it, with a lease |
| `/renew` | task | owner | Extends the lease. Renew whenever you make progress |
| `/done` | task | owner | Finishes the current stage: the next stage opens, or the task closes |
| `/stuck D-n` (or `T-n`) | task | owner | Stuck until that is settled, then back to working |
| `/release` | task | owner or manager | Back to To do |
| `/keep` | task | owner or manager | Clears `recheck` after a goal change |
| `/changes` | task in review | reviewer | Reopens the implement stage; give the reasons in the same comment |
| `/vote X` | decision | the decision's people | Majority decides; a tie stays open; a verbal decision needs every named person |
| `/drop` | decision | manager | Marks it dropped |
| `/ready` | pinned issue | people | Blind kickoff: when everyone is ready, the referee posts "Reveal" |

After posting, wait for the referee's reaction: 👍 accepted, 👎 refused with a reply giving the reason. Read it with `gh api repos/{owner}/{repo}/issues/comments/{id}/reactions` or `gh issue view N --comments`. A refused claim means other work: pick another task or open a decision.

## Pinned issue

Title `Alignment`, label `alignment`, pinned with `gh issue pin`.

```
## Goal
<one paragraph>

## Done when
- <checkable criterion>

## Risks
- <risk>

## Vision
Ranked. Agents fall back on it when a decision is missing or tied.
1. <most important>
2. ...

## Glossary
- **<term>**: <meaning in this project>

**Context:** <profile name>
**People:** @<login> (manager), @<login>, ...
**Lease:** <e.g. 2h>
**Grouping:** <field name>
**Stack defaults:** <e.g. Python with uv and pytest>
**Project:** <GitHub Project URL>

## For agents
You work for one person on this team. Sign every command comment [Person / Agent].
1. Act only on decisions labelled `decided`, and cite their IDs in commits and comments. A `proposed` decision is a question, not an instruction.
2. Before /claim and before /done, run the check: read this issue and the decisions labelled decided, superseded or dropped, then answer three questions. Does my task or diff act on anything still proposed? Does it touch a superseded or dropped decision? Does it go against the Vision? Any yes: open an issue labelled `review` that names the conflict and the IDs, follow the Vision meanwhile, and link the review issue from the task.
3. Claim before you work (/claim on the task issue) and wait for the referee's thumbs up. Renew the lease (<lease>) as you make progress.
4. Start every commit message with the task ID (T-n).
5. Decide alone only inside your own task. Anything others depend on (shared files, interfaces, data formats, names, the goal) is a decision: open a `decision` issue with options, costs and your recommendation, and wait.
6. Work no task covers: create the task first. Work already done without one: create it with label `logged-after` and close it.
7. Use the stack defaults above unless a decision says otherwise.
Commands: /claim [stage], /renew, /done, /stuck D-n, /release, /keep, /changes, /vote X.
```

## Task issue

Label `task`. Title: what gets done, short and specific.

```
**Criterion:** <a check anyone can run or read, e.g. "tests/test_parse.py passes">
**Paths:** <files or folders it changes, comma separated, or none>
**Decisions:** <D-n it relies on, or none>
**Stages:** <plan, implement, review | implement, review | implement>
**Agent / model:** <from agent-router, e.g. "implement: Codex gpt-x high; review: Claude">
**<Grouping field>:** <value>
<profile's extra fields>

<context: why, links>
```

To fill **Stages** and **Agent / model**, call the Skill tool with `agent-router` when it is installed, and give it the task text. Otherwise use `implement` and leave the agent blank.

- **Work with no files** (talking to a client, research, reading): `**Paths:** none`, scoped by its decisions. It is still claimed, so others see who is on it.
- **Work already done without a task**: create the task with labels `task` and `logged-after`, a criterion that it meets, and the commit SHAs in the body, then close it with `gh issue close N --reason completed`.

Create with `gh issue create --title ... --label task --body-file <file>`, then add it to the Project: `gh project item-add <number> --owner <owner> --url <issue url>`.

## Decision issue

Labels `decision` and `proposed`.

```
**Question:** <one question>
**Options:** A <option>, cost <cost>; B <option>, cost <cost>
**Recommendation:** <option and reason>
**People:** @<login>, @<login>
**Deadline:** <YYYY-MM-DD>
**Source:** <verbal (names), when it records a spoken agreement>
**Supersedes:** <D-n, when it replaces a decision>
**Goal change:** <yes, when it changes the goal>
```

## Review issue

Label `review`. Names the conflict, the IDs on each side, and what the agent did meanwhile. A person clears it by commenting what was decided and closing it; a lasting answer becomes a decision.
