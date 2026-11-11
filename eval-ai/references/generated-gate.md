# Generated gate

Generate this inside the project before the first model. Use the repo's language, test runner and CI. Coding agents run the `eval` command and never write their own eval scripts.

## Files

- `eval` command: the single entry point. Produces every reported number.
- `eval/manifest`: the split manifest.
- `eval/results/`: one stamped results file per run.
- `eval/matrix`: the requirements matrix.

## Split manifest fields

`method`, `group_key`, `time_column`, `folds`, `purge`, `embargo`, `data_hash`, `steps_touching_data`, `pretrained` (each with `id`, `cutoff`, and route: `postdates`, `masked` or `recall_control`). Fields that don't apply are written as explicit nulls, so an omission fails the gate.

## Results file fields

Header, written before unlock: `claim`, `claim_type`, `metric`, `threshold`, `kill_criterion`, `preregistered_at`.

Body: `commit`, `model_version`, `prompt_version`, `data_version`, `time_range`, `n_trials`, `selection_adjustment`, `metrics` with intervals, `baselines`, `null_test`, `recall_control`, `shift`, `dropped_items`, `overrides`, `grade`, `test_unlocked_at`.

The evaluator writes this file. Hand edits fail the check on the file's stored hash.

## Test lock

A separate evaluator sub-agent holds the test labels, stored outside the builder's working tree. Builders receive only the score from `eval`. The lock records each unlock, and a second unlock adds to N and is reported.

## Hard-fail checks

| Hard fail | Check |
|---|---|
| Missing manifest or split overlap | The manifest is absent or incomplete, or row hashes intersect between splits. |
| Grouped-duplicate violation | A value of `group_key` appears on both sides. Also compare perceptual or text hashes when near-duplicates are possible. |
| Missing baseline | No baseline row for the same split in the results. |
| Unstamped result or missing N | A required stamp field is empty, or a number in the matrix has no results file. |
| Null test missing or above chance | No null result exists, or the null run's interval lies above chance. Chance is the best trivial predictor's score on the same null data. |
| Non-time-ordered split on temporal data | `time_column` is set and the method is not time-ordered or purged, including random holdout and interleaved blocks, or a time-like column exists while `time_column` is null. |
| Knowledge overlap with no route | A pretrained entry's route is missing, an unknown cutoff has no masked or recall-control route, or a declared recall control has no measured result. |

## Override

Pass a written reason to `eval`. The evaluator logs the reason, the failed check and the time in `overrides`, and caps the claim at Smoke. The gate then lets the run through, labelled untrusted. Overrides can't be removed by a later run.

## Enforcement

Run the checks in a merge gate, or in a pre-merge hook where no CI exists, and run them on the first model. Limit concurrent training workers based on available memory.

## Reproducing

The `eval` command runs from a clean checkout plus documented data. Paper volume adds an evaluation section generated from results files and a reproducibility package: environment lockfile, data manifest, seeds, commands.
