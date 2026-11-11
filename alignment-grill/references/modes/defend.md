# Defend

A person defends a decision or a result they own: a model's score, a design choice, a number in
a report. The goal is a record anyone can audit, and a list of what nobody checked yet.

## 1. Pick the target

The decision issue or task, and the exact claim, in one sentence with its number if it has one
("the forecast beats persistence by 18% MAE on June"). Find the evidence the person points to
yourself: the commit, the notebook, the run log, the test.

Done when the claim is one sentence and you have opened each piece of evidence.

## 2. Grill

One round at a time, each question with what you found:
- **Claim**: is this sentence what they would stand behind in front of the team?
- **Evidence**: which file, run or test shows it, linked? Rerun it when that takes under two minutes.
- **Baseline**: compared against what? Would the simple option score close to this?
- **Leakage and luck** (for results): could the test data have reached training, or one lucky split carry the number?
- **What would change your mind**: the observation that would make them drop the claim.
- **Unchecked**: what they know they have not tested.

Write down where an answer is missing or the evidence does not match the claim.

Done when every question has an answer or is marked unanswered.

## 3. Record

Post one comment on the decision issue or task, headed `Defense: <claim>`, with the claim, the
evidence links, the baseline, what would change their mind, and the unanswered items. Each
unanswered item becomes a `task` issue with a criterion that answers it. If the evidence does not
support the claim, say so in the comment and propose a decision that narrows or withdraws it.

Done when the comment is posted and every unanswered item has a task.
