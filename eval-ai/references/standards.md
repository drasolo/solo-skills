# Standards

Entries were verified on 2026-11-10 unless marked otherwise. Before relying on a rung, re-check only that entry's source and update its date.

## Public ladder

A rung shows that the pipeline works. It says nothing about the real problem. Write the tolerance into the pre-registration.

| Rung | Task and cost | Reference | Pass | Known problems |
|---|---|---|---|---|
| MNIST | Image classification, 70,000 images, minutes on a CPU | Linear classifier 12% test error, LeNet-5 0.95% (LeCun et al. 1998) | Linear model at or below 12% error. A small CNN near 1%. | 0.15% of test labels are wrong (Northcutt 2021). Too easy to support any claim beyond a working pipeline. |
| Imagenette | 10-class images, 13,394 images, 160px download 99 MB | 87.43% at 128px, 5 epochs, mean of 5 runs, from a tuned entry with about 1% run-to-run variation ([fastai/imagenette](https://github.com/fastai/imagenette)) | Within the pre-registered margin. A default pipeline should land below the tuned entry. | Small, easy subset. |
| OpenML task 31 (credit-g) | Tabular, 1,000 rows, 10-fold CV, seconds | Majority class 70.0%. Random forest median accuracy 0.753 and AUC 0.7745 across 28 uploaded runs ([task](https://www.openml.org/t/31)) | Beats majority and lands near the forest median. | The reference is a sample of uploaded runs, not a published score. |
| M4 Weekly | Forecasting, 359 series, horizon 13 | sMAPE: Naive2 9.161, Comb 8.944, competition winner 7.817 ([organizers' results](https://github.com/Mcompetitions/M4-methods)) | Beats Naive2. Other weekly entries reached 6.726, so the winner is not the ceiling. | Scores come from the organizers' file. The paper's tables were unreachable. |
| Planted signal | Time-series and quant, synthetic, minutes | No external score. The pipeline recovers the planted edge and finds nothing in pure noise. See Lopez de Prado below. | Both conditions hold. | Use it in place of a public finance benchmark, since no trustworthy one exists. |
| MMLU, HELM | LLM knowledge and holistic evaluation | [MMLU](https://arxiv.org/abs/2009.03300), [HELM](https://crfm.stanford.edu/helm/) | Run only when a brief requires them. | MMLU: an estimated 6.49% of questions contain errors ([Gema et al.](https://arxiv.org/abs/2406.04127)), and GPT-4 reached a 57% exact-match rate guessing masked options ([Deng et al., NAACL 2024](https://arxiv.org/abs/2311.09783)). Treat MMLU under the knowledge-overlap rule. |

## Paper standard

A claim is Paper-ready when all of these hold:

- Every REFORMS item is answered or marked N/A with a reason.
- The NeurIPS checklist is complete.
- Comparisons have intervals over folds or seeds and use a suitable test.
- Multiple comparisons are corrected.
- Ablations show what each component adds.
- A model card and a datasheet exist for what was trained and collected.
- The reproducibility package regenerates every reported number.

| Use | Source |
|---|---|
| Reporting checklist for ML-based science, 32 items in 8 sections | Kapoor et al., "REFORMS", Science Advances 10(18), eadk3452, 2024. [reforms.cs.princeton.edu](https://reforms.cs.princeton.edu/) |
| Conference reporting checklist | [NeurIPS Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist) |
| Comparing models across resampled splits. Corrected resampled t: variance (1/J + n2/n1)S², with t(J-1) critical values, for J resamples, train size n1, test size n2. | Nadeau and Bengio, "Inference for the Generalization Error", Machine Learning 52:239-281, 2003. doi:10.1023/A:1024068626366 |
| Leakage across fields, found in at least 294 papers in 17 fields | Kapoor and Narayanan, "Leakage and the reproducibility crisis in machine-learning-based science", Patterns 4(9):100804, 2023. doi:10.1016/j.patter.2023.100804 |
| Label errors in test sets and their effect on rankings | Northcutt, Athalye and Mueller, "Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks", NeurIPS 2021 Datasets and Benchmarks. [arXiv 2103.14749](https://arxiv.org/abs/2103.14749) |
| Documenting a trained model | Mitchell et al., "Model Cards for Model Reporting", FAT* 2019. [arXiv 1810.03993](https://arxiv.org/abs/1810.03993) |
| Documenting a dataset | Gebru et al., "Datasheets for Datasets", CACM 64(12):86-92, 2021. doi:10.1145/3458723 |
| Selection-adjusted Sharpe. Inputs: estimated Sharpe, return skewness and kurtosis, series length, variance of trial Sharpes, number of independent trials. | Bailey and Lopez de Prado, "The Deflated Sharpe Ratio", Journal of Portfolio Management 40(5):94-107, 2014. [PDF](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) |
| Familywise error across comparisons | Holm, "A Simple Sequentially Rejective Multiple Test Procedure", Scandinavian Journal of Statistics 6(2):65-70, 1979. Not opened at the primary source. |
| Purged k-fold and embargo (ch. 7), synthetic backtests (ch. 13) | Lopez de Prado, Advances in Financial Machine Learning, Wiley, 2018. |
| Testing on synthetic data (appendix A) | Lopez de Prado, Machine Learning for Asset Managers, Cambridge, 2020. doi:10.1017/9781108883658. Title confirmed from the table of contents only. |
| Adversarial validation | Zajac, "Adversarial validation, part one", FastML, 2016. [Post](https://fastml.com/adversarial-validation-part-one/). A blog post, and no peer-reviewed origin was found. |
