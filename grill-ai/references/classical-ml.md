# Classical ML catalog

Tabular models, forecasting, backtests and recommenders.

## Decision branches

- **Split unit.** Is the independent unit a row, customer, patient, site or time period? The split follows that answer.
- **Decision time.** At the moment of prediction, which fields are actually available, and with what delay?
- **Model family.** Does a boosted tree or regularized linear model on good features reach the bar before anything heavier is tried?
- **Probability use.** Does anything downstream consume the score as a probability? If so, calibration is a requirement.
- **Action rule.** How does a score become an action, and who sets the threshold from which costs?

## Evidence

- **Recommender measured only offline.** Compare against popularity, and treat logged interactions as biased by what was shown.

## Mechanics

- **Preprocessing outside the pipeline.** Scalers, imputers, feature selection or encoders see validation folds. Fit them inside each fold.
- **Target encoding in-fold.** Encode out-of-fold.
- **Resampling before the split.** SMOTE or oversampling runs before splitting, so synthetic neighbors cross into validation. Resample training folds only.
- **Lookahead features.** Centered rolling windows, backfilled values, full-period statistics or a join that takes the latest record. Use as-of joins keyed on when the value became known.
- **Early stopping on the test set.** Use a validation set that sits later in time than training for forecasting.
- **Category mismatch.** Unseen categories at inference, or category codes that differ between training and serving. Persist the mapping.
- **Unpinned booster behavior.** Tree library upgrades change defaults and sometimes crash. Pin the exact version.

## Exposure

- **Concept drift.** The relationship changes after deployment. Track rolling error against delayed truth and define a retraining trigger.
- **Proxy discrimination.** A permitted feature encodes a protected attribute. Compare error rates across groups named in the contract.
