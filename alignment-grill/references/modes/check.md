# Check

The self-check an agent runs before `/claim` and before `/done`. The rules live in the pinned
issue's "For agents" section, so agents without this skill run the same check. This file adds
what changes when a person is in the session.

## 1. Load the record

- The pinned issue: `gh issue view <pinned>`.
- Decisions: `gh issue list --label decision --state all --json number,title,labels,body --limit 200`.
- The task: `gh issue view <n> --comments`, including any plan comment from an earlier stage.
- Before `/done`, the diff: `git diff <base>...HEAD` and the commit messages.

Done when you have all four (three before a claim).

## 2. Answer the three questions

1. Does this task or diff act on anything still **proposed**?
2. Does it touch a **superseded** or **dropped** decision: code, names or data formats that decision covered?
3. Does it go against a line of the **Vision**?

Also before `/done`: does every commit start with the task ID, does the diff stay inside **Paths:**, and does the **Criterion** hold? Run it when it is a command.

For each yes, write down the IDs on both sides and the lines of the diff involved.

Done when every question has a yes or no with its evidence.

## 3. Act on the answer

- All no: post the command.
- Any yes, **with a person in this session**: put each conflict to them as a question with your recommendation, and act on the answer. If the answer settles something others depend on, record it as a decision (see `decide.md`).
- Any yes, **no person in the session**: open a `review` issue naming the conflict and the IDs, follow the manager's Vision meanwhile, link the review issue from the task, then post the command.
- The diff left **Paths:**: update **Paths:** if the person agrees, otherwise move that change to its own task.
- The implementation left the plan comment: write a comment before `/done` saying what changed and why.

Done when the command is posted and every yes has a person's answer or a review issue.
