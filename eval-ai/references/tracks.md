# Tracks

Apply "All tracks", then each section that matches the subjects chosen at intake.

## All tracks

- **Leakage.** Information from the test set or the future reaches training through duplicates, shared groups, preprocessing fitted on all data, or a feature derived from the target. Check for hash overlap across splits, group overlap, max train time before min test time, and single-feature scores near perfect.
- **Missing baseline.** No comparison against the simplest honest alternative, computed on the same split.
- **Test reuse.** A model, prompt, threshold or epoch was chosen on the data that reports the final score.
- **Truth-selected windows.** The periods or examples in a headline result were picked using the outcome. Fix selection rules before looking, or report every window.
- **Mismatched comparison.** Systems under comparison ran at different resolutions, horizons, data or conditions. Run them under identical conditions. Also check that train and test share a resolution, and look for forward-filled targets and clock-change days.
- **Evaluator disagreement.** Several scripts report different values for one metric. Keep one evaluator and delete the rest.
- **Rounded-up claims.** A headline multiple survives after its source number has changed. Generate every reported number from a results file.
- **Same-source validation.** A surrogate is validated only on data from the generator that trained it, or the average hides the region that matters. Test near the decision boundary and on independent data.
- **Proxy target.** The label stands in for the real outcome. Measure how well they agree.
- **Inactive safety.** A safety result counts periods when the action never ran. Report how often the system acted.
- **Untested alternative.** The obvious non-ML or simpler approach has no built comparison.
- **Metric mismatch.** The metric ignores what the matrix cares about. Recompute it independently, including averaging and filtered rows.
- **No uncertainty.** One seed, split or point estimate. Report the spread, and paired differences when comparing variants.
- **Hidden slices.** A good average covers a failing group, period or input type.
- **Demo as evidence.** Hand-picked examples stand in for a measured rate.
- **Claim beyond the data.** The eval population is narrower than the claim.
- **Unrunnable elsewhere.** Data or results exist on one machine only. The `eval` command must run from a clean checkout plus documented data.

## Model

Baselines: majority or mean, last value and seasonal naive for time series, a regularized linear model or boosted trees, the incumbent.

Metrics:

- Classification: PR-AUC, F1 or cost at the chosen threshold, Brier score for probabilities.
- Regression: MAE and RMSE with residuals by slice.
- Forecasting: MASE, pinball loss, interval coverage. Skip MAPE near zero.
- Ranking and retrieval: recall at k, NDCG at k.
- Detection and segmentation: mAP at stated IoU, IoU or Dice, per class.

Checks:

- Fit preprocessing, encoders and resampling inside each training fold.
- Tune on a separate holdout or use nested cross-validation.
- Choose thresholds and early stopping on validation data.
- Neural models must overfit one batch before anything else, and start at the chance-level loss.
- Evaluate the artifact that ships, including export or quantization.
- A fine-tune is compared to its base model on the same set and template.

## Product agent

Baselines: a fixed workflow or single model call.

Metrics, per task with repeats: end-state success graded from the environment, trajectory checks, cost per solved task, turns, safety violations, human interventions.

Checks:

- Run settings with oracle, retrieved and full context, so failures can be attributed to a component.
- Reset the environment between runs. Keep answers and graders outside the agent's reach.
- Never score from the agent's own final message.
- Report how often each stage's output was actually used downstream.
- Measure budget exhaustion and recovery after a tool failure.

## LLM outputs

An LLM used as a judge also turns this section on.

- Pin the model ID and prompt version. A provider-side update counts as a new model version.
- Validate every response against a structured schema.
- Cache raw outputs keyed by input hash, model ID, prompt version and parameters, so reruns are reproducible.
- Rerun a sample K times and report the agreement rate.
- Report cost and latency per output, including tail percentiles.
- Baseline: the same LLM without the pipeline.
- Keep a held-out portion of any set used for prompt tuning.
- RAG: measure retrieval (recall at k against labeled sources) separately from generation (faithfulness given retrieved text), compare with keyword search and no retrieval, and verify that each citation supports its claim.
- Rerun the eval on every model change.

## Unlabeled eval sets

For retrieval, generated hypotheses and LLM products with no ground truth:

- Write the queries before building the system.
- Report the relevance-judgment protocol.
- If an LLM judge is used, report its agreement with human labels on a sample, including the false-pass rate.
- Test any automated checker or judge against corrupted outputs, including negated and flipped claims.
- With a single annotator, re-label 10% after a delay and report self-agreement.
- Include a long-tail, not-in-pretraining slice.

## Time-series and quant

Evaluation only. How labels and signals get built belongs to model-building work. Mark any item that doesn't exist in the market at hand as N/A with a reason. Auction and physical markets usually have no borrow cost, corporate actions or survivorship.

- **Data.** Point-in-time values, a survivorship-free universe, corporate-action adjustment, and timestamp alignment across sources: close times, timezones, publication lag.
- **Splits.** Purged k-fold with embargo when labels overlap, otherwise walk-forward. Report the distribution across paths.
- **Slices.** By regime: volatility and trend. In power markets, also price spread, negative-price days, season and scarcity.
- **Realism.** Signal-to-execution delay, fees, borrow cost, capacity, and a re-run at 2x costs, naming which costs doubled. In power markets, also grid fees, price impact and balancing penalties.
- **Baselines.** Buy-and-hold, simple momentum, random-entry, and the best non-ML rule.
- **Selection.** Deflated Sharpe over every strategy variant tried. Where a return series doesn't fit its assumptions, use Holm or a fresh confirmation run.
- **Ladder.** Synthetic data with a planted signal: the pipeline must recover the planted edge and find nothing in pure noise. No trustworthy public finance benchmark exists, so never substitute one.
- **Decision.** For scheduling or dispatch, settle the decision at realized prices and report capture relative to perfect foresight and the best naive schedule.
