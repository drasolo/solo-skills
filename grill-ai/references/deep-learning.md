# Deep learning catalog

Neural network training, vision, audio, fine-tuning and generative models.

## Decision branches

- **Train or reuse.** Does a pretrained model, embedding plus linear head, or hosted model reach the bar before custom training?
- **Label budget.** How many labeled examples exist, and what would more of them cost compared to a bigger model?
- **Compute budget.** How many full runs can the user afford, and which experiment most deserves one?
- **Deployment artifact.** What finally runs, at which precision and on which hardware?

## Evidence

- **Train and validation curves unexamined.** The claim rests on a final number with no curve, so overfitting or a broken pipeline stays invisible.
- **Weak generative evaluation.** FID or a similar score from too few samples or a mismatched reference set. Add a blind human comparison and test for memorization by searching training data for nearest neighbors.

## Mechanics

Start with the sanity loop: the model must overfit a single batch to near-zero loss. A model that cannot do this has a bug.

- **Loss input mismatch.** Softmax or sigmoid applied before a loss that expects logits, or targets in the wrong shape or type. Check loss at initialization against the chance-level value, such as ln(classes) for cross-entropy.
- **Broadcast shape bug.** A `[N]` tensor meets a `[N, 1]` tensor and silently forms an N by N result. Assert shapes at the loss.
- **Train and eval mode errors.** Dropout or batch norm in the wrong mode at validation, or batch norm running on tiny batches.
- **Gradient flow errors.** Missing `zero_grad`, an accidental `detach`, frozen layers that should train or the reverse. Log the gradient norm per parameter group.
- **Normalization mismatch.** Statistics computed on all data, pretrained-model statistics omitted, or value ranges that differ between training and inference.
- **Augmentation errors.** Augmentation runs on validation data, or changes the label, as a horizontal flip does for left and right.
- **Sequence masking errors.** Padding not masked, causal masks wrong, labels misaligned by one position or ignored tokens counted in the loss.
- **Tokenizer or template mismatch.** Training and inference use different special tokens, padding sides or chat templates.
- **Dataloader bugs.** Training data left unshuffled, workers sharing a random seed, or last-batch handling that distorts metrics.
- **Distributed metric errors.** Validation samples duplicated across processes, or metrics averaged per batch when batches differ in size.
- **NaN masking.** Mixed precision or a clamp hides exploding values. Detect the first NaN and stop.

## Exposure

- **Out-of-range inputs.** A new camera, accent, resolution or language with no measured behavior. Test those conditions directly.
- **Unknown-license weights or data.** The license of the checkpoint or training data forbids the intended use.
- **Training-data extraction.** A model trained on private data can reproduce it. Test for regurgitation before sharing the weights.
