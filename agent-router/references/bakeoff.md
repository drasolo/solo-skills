# Bake-off

Measures which agent and model does each task type best, on the person's own work. Run it only
when the person asks: after setting up, or when a new model ships.

## 1. Design

Call the Skill tool with `eval-ai` to design it, and give it this frame:
- **The set:** about 12 finished tasks from the person's own repos, at least one per common task type, each with a commit before the change and a criterion that can be checked (tests, or a written rubric).
- **The contestants:** decided by the person at this point, given the agents installed and their models. Keep the count small enough to run: contestants × tasks runs.
- **The run:** every contestant gets the same prompt (the preamble plus the task) in a fresh worktree at the commit before the change, with the same time limit.
- **The grading:** tests where they exist, then a blind review by the person, with outputs labelled A, B, C so they can't tell the agent. Record time and retries.

Done when eval-ai's design is accepted by the person, with the contestants named.

## 2. Run and grade

Run every contestant on every task, collect the diffs and logs, grade blind, then reveal.

Done when every run has a grade, a time and a retry count.

## 3. Update the cards and rules

For each agent, rewrite its card in `references/cards/` with the date, the bake-off's task list, its scores per type, and what it was good and bad at, with examples. Change a row in `references/rules.md` only when the bake-off shows a clear difference, and write the date and the scores in its Basis column. Log every run with `scripts/log_outcome.py finished`, so the bake-off also feeds the outcome log.

Done when each card has a date and scores, and every changed rule names its evidence.
