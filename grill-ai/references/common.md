# Common catalog

Applies to every AI system.

## Decision branches

- **Need.** What action changes because of this output, and what happens today without it? Would a rule, a lookup, a search or a query reach the bar?
- **Target.** What real outcome does the label, reward or task stand in for? Who produced the labels, and how often do two labelers disagree?
- **Error costs.** Which error is worse, and by how much? Does the system need a threshold, an abstain option or a human fallback?
- **Bar.** Which metric and number count as success? Which slices must also pass?
- **Data.** Where does it come from, and is the user allowed to use it for this? Does the data's population and period match what the system will see in use?
- **Eval design.** What holdout stays untouched, and who looks at it how many times?
- **Operation.** Batch or online? What latency, cost per request and hardware limits apply? What triggers retraining or a model change, and who owns it?
- **Failure.** What does a person see when the system is wrong? How is it detected, and how is it rolled back?
- **Harm.** Who is affected by errors without having chosen the system? Does the use fall under privacy, employment, credit, health or similar regulation?
- **Stop.** Which result ends the project?

## Mechanics

- **Unreproducible result.** A reported number cannot be tied to a commit, config, data snapshot, seed and package versions. Pin all five and rerun.
- **Training-serving skew.** Training and inference build inputs through different code. Share one transform and test that both paths give identical output on the same record.
- **Silent row loss.** Joins, filters or parsing drop or multiply records. Log counts at each stage and assert the expected ones.
- **Silent fallback.** An exception handler, default value or retry hides failures, so the metric counts them as normal outputs. Count fallbacks and report them with the metric.
- **Bad missing-value handling.** NaN, empty strings or sentinel values such as -1 or 999 flow through as real data. Profile each input and handle them explicitly.

## Exposure

- **No monitoring.** Nothing watches input distribution, output distribution, delayed ground truth, errors or cost.
- **Unbounded cost.** One user or one bad loop can spend without limit. Set budgets per request and per period.
- **Private data.** Personal data reaches logs, training sets, prompts or third parties without a basis. Trace each path.
- **Feedback loop.** Outputs change the data future versions learn from, as with recommendations or policing. Keep a holdout that the system does not influence.
- **No rollback.** A bad model, prompt or index cannot be reverted quickly to a known version.
- **Unsafe failure.** The system gives a confident wrong output where it should abstain or hand off. Test on inputs outside its range.
