# alignment-referee

A GitHub Action that keeps a team board honest when people and AI agents share one repo. Tasks,
decisions and conflicts are issues. People and agents post short commands as comments, and the
referee is the only thing that changes a task's state. Two agents can't both take the same
work, because every claim goes through one queue and one process decides each in order.

It runs on every issue comment, every push and once an hour. GitHub keeps at most one run
waiting, so each run reads everything posted since the last one, oldest first.

## Commands

End a command with a signature, `[Person / Agent]`. GitHub only sees the account that posted,
so the signature is how two agents of one person stay apart. Without one, the commenter counts
as a human.

| Command | Where | Who | Effect |
|---|---|---|---|
| `/claim [stage]` | task | anyone | Refused if another active task has the same title, overlapping paths or a shared decision. Otherwise assigns you, sets Working on it, starts the lease |
| `/renew` | task | owner | Extends the lease |
| `/done` | task | owner | Finishes the stage. The next stage opens, or the task closes |
| `/stuck D-12` | task | owner | Stuck until D-12 (or a task T-n) is settled, then back to Working on it |
| `/release` | task | owner or manager | Back to To do |
| `/keep` | task | owner or manager | Clears `recheck` after a goal change |
| `/changes` | task in review | reviewer | Reopens the implement stage |
| `/vote X` | decision | the decision's people | A majority decides it. A tie stays open. A verbal decision needs every named person |
| `/drop` | decision | manager | Marks it dropped |
| `/ready` | pinned issue | people | Once everyone is ready, the referee posts "Reveal" |

The referee reacts 👍 to every command it accepts. When it refuses one, it reacts 👎 and replies
with the reason.

## What it also does on its own

- A lease that runs out puts the task back to To do.
- A decision past its deadline with no majority gets one comment.
- A decision that is decided marks the decisions it supersedes, and wakes the tasks stuck on it.
- A decided goal change marks every open task `recheck`. Those tasks can't be claimed or
  finished until the owner or the manager answers `/keep` or `/release`.
- A commit with no `T-n` in its message that touches paths someone else's task claimed opens a
  `review` issue.

## Issues it reads

Labels say what an issue is: `alignment` (the pinned issue), `task`, `decision`, `review`. Fields
are bold labels in the body, one per line:

```
Pinned:   **People:** @ana (manager), @bo    **Lease:** 2h    **Project:** <project URL>
Task:     **Criterion:** ...   **Paths:** src/parse/, docs/x.md   **Decisions:** D-4
          **Stages:** plan, implement, review   **Agent / model:** ...
Decision: **Question:** ...   **Options:** ...   **People:** @ana, @bo   **Deadline:** 2026-12-01
          **Source:** verbal (ana, bo)   **Supersedes:** D-4   **Goal change:** yes
```

Task IDs are `T-<issue number>` and decision IDs are `D-<issue number>`. The referee stores its
state in a hidden `<!-- referee:{...} -->` block at the end of each body and keeps the rest of
the body as it was.

## Use it

1. Copy `examples/caller.yml` into the code repo as `.github/workflows/alignment.yml`.
2. To mirror state into a GitHub Project (Table, Board, Roadmap views), the manager creates a
   fine-grained token that can read and write issues on the repo and edit the Project, and
   stores it as the secret `ALIGNMENT_TOKEN`. The workflow's own token can't edit a Project
   owned by a user. Without the secret, the referee says so once on the pinned issue and still
   assigns and labels.

   The Project fields it fills, when they exist: Task status (single select: To do, Working
   on it, Stuck, Done; a field named Status works too if it has those options), Owner, Stage, Lease, Waits on, Last updated, Criterion, Scope, Agent / model.

## Limits

- The push check reads commits on the default branch only.
- If a person edits an issue body during a run, the referee's write can undo that edit. The
  window is a few seconds.
- Effects are applied before state is saved, so a run that fails halfway can repeat a comment
  on the next run. Nothing is lost.

## Tests

```
python -m unittest
```

They run the rules against a board in GitHub's REST shape (`tests/fixtures/board.json`). Only the
standard library is used.
