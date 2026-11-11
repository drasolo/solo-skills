---
name: eval-ai
description: Evaluate and benchmark AI systems to research-grade validity, scaled to the work. Covers ML, deep learning, forecasting, LLM apps, RAG, agents and trading backtests. Use when the user wants an eval designed, built or audited, wants models or agents benchmarked, wants a claim graded, or reports that a result failed.
---

Produce numbers a skeptical reviewer would accept. One evaluator produces every number, each number is stamped, and each claim carries a grade. Find facts with sub-agents. Put decisions to the user.

## Modes

- **Design**: an idea with no code. Run steps 1 and 2 and write the stage plan.
- **Audit**: an existing eval, read-only. Answer step 1 from the project's own files and note each assumption. Score every stage and core item as solid, partial, missing, broken, N/A or dropped, and grade every claim. Run any checks on a copy outside the project. An item the project lacks scores missing even if your own run of it passes, so report your result beside it. An item that can't run, for example because the data is elsewhere, is dropped. Skip steps 3 and 6, then write the step 7 scorecard. Run the improvement path only if the audit exposed a real failure the checks missed.
- **Build**: run every step.

## Step 1. Intake

Recon returns the facts, through a sub-agent unless the project is a few files or the preset has a 10-minute cap: task, data, time columns and grouping keys, pretrained models and their training cutoffs, existing eval code, what the brief scores, available compute.

Then ask one round. Each question carries a recommendation and is worded so "yes" accepts it. Settle the goal, stakes, deadline, who judges, intended claims, subjects, preset, and any paid API or GPU spend.

| Preset | Overhead cap | Public ladder | Notes |
|---|---|---|---|
| short deliverable | 10 min | N/A | Write checklists and generate no code, so external AI-use rules hold. One-line pre-registration. |
| time-boxed sprint | 30 min | N/A | Gate on the first model, not the last. |
| LLM automation | 30 min | N/A | LLM outputs section is on. |
| tool/product | 30 min | Only when the eval pipeline is new | |
| research claim | none | Required | Paper volume: evaluation section and reproducibility package. |
| trading/time-series | none | Required: planted-signal rung | Time-series and quant section is on. |

Default N/A stages, which intake can change:

- Short deliverable: calibration, adversarial and privacy, system performance, ablation, planted-defect audit, regression gate.
- Time-boxed sprint: ablation.
- LLM automation and tool/product: calibration, ablation.
- Research claim and trading/time-series: none.
- Every preset: labels when an outside party supplies them, graders when the metric is purely numeric, and split items when nothing is fitted or tuned on the data.

Overhead is the time the checks add, excluding model training. Five items always run and can never be dropped under a cap: manifest, baseline, stamp with N, one evaluator, null test. The null test can use a subsample to fit. If the other core items can't fit, drop the costliest, name each one in the scorecard, and cap the claim at Smoke.

Mark every stage in the table below as required or N/A with a one-line reason. Read [references/tracks.md](references/tracks.md) and apply the sections that match the subjects.

Done when the preset is chosen and every stage is marked.

## Step 2. Requirements matrix

Map each scored criterion or requirement to a metric, test, threshold and results file. Include latency, cost, autonomy, explainability and regulation when the brief asks for them. A requirement with no measurement is listed as a gap.

Done when every requirement has a row.

## Step 3. Generate the gate

Build it from [references/generated-gate.md](references/generated-gate.md) before the first model exists. At short-deliverable volume, write the core as a checklist instead.

Done when the gate fails on an empty project for the right reasons.

## Step 4. Public ladder

When the preset requires it, take the cheapest fitting rung from [references/standards.md](references/standards.md), re-check that entry's source, and reproduce its reference score within tolerance. Failure stops work until the pipeline is fixed. A pass shows the pipeline works and nothing about the real problem. If no rung fits the system, as with an LLM pipeline or a retrieval system, mark the ladder N/A with that reason and rely on the step 6 oracle and trivial checks.

## Step 5. Pre-register and run

Before the test set is unlocked, write the claim, metric, threshold and kill criterion into the results file. Then run the required stages against the baselines. Only the `eval` command may produce a reported number.

Done when every required stage has its artifact and every requirement row has a result.

## Step 6. Audit the eval

Plant one defect per hard fail and confirm the gate catches each. Check the evaluator against a perfect oracle, which must score the maximum, and a trivial predictor, which must score at its baseline.

## Step 7. Close

Re-audit the requirements matrix. Write the scorecard: stage statuses, each claim with its grade, type and the grade it would reach once missing stamps are added, dropped items, overrides. End with exactly these two lines:

- Supports decision X. Does not support Y.
- Next cheapest test that could kill this claim: ...

Then run the improvement path.

## Validity core

- **Split manifest.** Records the method, grouping key, time column, and every step that touches data, including mining and augmentation. Near-duplicates and group members, such as the same episode, customer or song in another version, sit in a single split. In retrieval, this covers tuning and eval queries, and versions of one item count as one for relevance credit.
- **Leakage tests.** Split and group overlap, time ordering, and single-feature scores near perfect.
- **Overlap-aware splits.** When samples overlap in time or labels span windows, use purged k-fold with an embargo, or walk-forward when training on later periods would use the future.
- **Baselines.** On the same split as the model, from the track's list.
- **One evaluator.** The only source of reported numbers.
- **Locked test set.** Builders never see it, and it unlocks once.
- **Stamp.** Commit (or a content hash outside git), model version, data version, time range and N. N counts the configs, prompts, feature sets or windows tried against that split. A submission log counts as the record when every scored attempt is in it. Each submission to a test set that returns a score adds 1 to N, and final selection trusts cross-validation over that score. Choosing the best of N requires a selection-adjusted number: deflated Sharpe for strategies, otherwise Holm, Bonferroni or a fresh confirmation run.
- **Null test.** Run the whole pipeline on shuffled labels or random inputs, block-shuffled for time series. A score above chance means the eval is broken, so stop. Chance is the score of the best trivial predictor on the same null data, such as time-of-day climatology for a seasonal series or random rankings for retrieval. When the scorer is external, run the null on local validation. A pass does not rule out leakage, because a feature derived from the target also goes to chance once labels are shuffled.
- **Knowledge overlap.** For any pretrained model or LLM, and for public benchmarks with known contamination. It passes when items postdate the training cutoff, are masked, or a recall control runs. The recall control asks the model for each outcome without the evidence, and measures the correct rate against the base rate and a pre-registered threshold. Above the threshold, the claim is capped at Internal no matter what else passed. With no stated threshold, the cap applies when the correct rate's interval lies above the base rate. For generative tasks, probe the named facts the output depends on. For a model that can't be asked, such as an embedding model, compare performance on items it could know against items it couldn't. If neither is possible, this route fails. An unknown cutoff counts as not postdating.
- **Shift.** Adversarial validation between train and test, plus an input-envelope check that flags inference inputs outside the training range and reports them as their own slice.

## Gate severity

Data with a time column counts as temporal, including panels such as customer-months.

Hard fails block: missing manifest or split overlap, grouped-duplicate violation, missing baseline, unstamped result or missing N, null test missing or above chance, any split on temporal data that is not time-ordered (random k-fold, random holdout, interleaved blocks), knowledge overlap with no passing route.

Shift signals are reported without blocking. A slice that fails its threshold holds the claim below Stress-tested.

Any hard fail can be overridden only with a written reason logged in the results file, which caps the claim at Smoke.

## Claims

Grade:

- **Smoke**: ran on a small sample, has no N, or carries a dropped item, an override or an unresolved hard fail.
- **Internal**: validity core passed on the project's own data.
- **Stress-tested**: also survived slices, shift, adversarial cases and variation across seeds or folds.
- **Externally validated**: also held on independent data or a different population.
- **Paper-ready**: also meets the paper standard in `standards.md`.

Type: predictive or causal. A causal claim needs a written graph, named confounders and a falsification test. Without them, state it as associational. A randomized ablation or a controlled simulator intervention supports a causal claim about that system in that setup, and needs no graph.

State no claim above its grade. Editing the pre-registered claim, metric, threshold or kill criterion after unlock downgrades the claim to Internal.

## Stages

| Stage | Settles | Artifact |
|---|---|---|
| Claims and pre-registration | What will be claimed, about which population and level | Results file header |
| Metrics and decision metric | The ML metric, and the metric that drives the real decision after costs, re-run at 2x cost or latency. If the conclusion flips, the claim is fragile. | Metric definitions, tested on hand-computed cases |
| Labels and agreement | Who labeled, by what guide, how often labelers agree | Labeling guide and agreement score |
| Datasets | Sampling source, sizes, versions, and how to build a set when no labels exist | Dataset manifest |
| Split integrity | Grouping, time order, overlap | Split manifest and passing checks |
| Graders | Code check, human or judge model, and how each was validated | Grader tests against known good and bad outputs |
| Baselines | Trivial, non-ML, incumbent, human, oracle, where each applies | Baseline rows in the results |
| Run harness | One command, pinned versions, per-item raw outputs, and failures counted as failures | The `eval` command |
| Statistics and distributions | Spread across folds, seeds or paths, intervals, paired comparisons. A single walk-forward run is one sample. | Intervals in the results |
| Error analysis | Failure categories and counts, read from real failures | Failure table |
| Slices | Which groups, periods or input types must also pass | Per-slice results |
| Calibration | Whether scores can be read as probabilities, and interval coverage, against a constant-forecast reference | Reliability result |
| Robustness and shift | Perturbations, temporal and population shift, out-of-range inputs | Shift report |
| Adversarial and privacy | Threat model, attack success, private data paths | Attack results |
| System performance | Latency percentiles, cost per correct outcome, memory, measured on the shipped artifact | Performance table |
| Ablation | What each component adds. With more than about 20 correlated features, use clustered importance out of sample, never in-sample importance alone. | Ablation table |
| Planted-defect audit | Whether the gate catches each hard fail | Audit log |
| Regression gate | What must pass before a code, prompt, model, data or dependency change ships | Merge gate |

## Improvement path

Run this at close-out, and whenever the user reports that a result failed, even weeks later. Work out why the checks missed the failure, then propose one entry for approval. Each entry:

- Names a general failure category, never a specific project.
- Merges into an existing entry if it overlaps one.
- Passes the keep rule: it would have prevented a real failure, a near-term research or trading need requires it, or its work type recurs in at least 2 distinct projects or dated deliverables.

Also read `LATER.md` at this skill's root and offer back any item whose trigger fired. Log nothing automatically.
