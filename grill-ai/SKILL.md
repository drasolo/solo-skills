---
name: grill-ai
description: Grill the user on an AI system's decisions, then review its code and evidence. Covers ML, deep learning, LLM apps, RAG, agents, RL and any other model-based system. Use when the user wants an AI idea or project stress-tested, wants a model, training run, prompt, eval or agent reviewed, or doesn't trust a result.
---

Stress-test an AI system with a **grill** that settles what it must achieve, a **review** that tests the build against those decisions, and a second grill that turns every finding into a decision. Facts are your job: find them with sub-agents. Decisions are the user's: put each one to them and wait.

## Grill format

Work a **design tree**, where every decision branches into the decisions that depend on it. The **frontier** is every decision whose prerequisites are settled. Ask the whole frontier in one round, then wait. A question that depends on another question still open belongs to a later round.

```
**Q1. <title>.** <question, with the concrete choices and what each one costs>

Recommended: <your answer and the reason>
```

Word each question so "yes" accepts your recommendation. Bring the system's own numbers, files and code into the question. Ask only what changes what gets built, measured or claimed. A running sub-agent blocks only the questions downstream of it.

## Steps

### 1. Recon

Dispatch a sub-agent to read the project and return a **system card**: stage (idea, built, trained, deployed), system types, the target or task, data sources and their time range, model or provider, the metrics and every result the project claims, spec and coding-standards documents, what has actually been run, available compute. Each fact cites `file:line` or says "not found".

If the target is only an idea, write the card from what the user said and mark the review steps as skipped.

Done when every card field holds a cited fact or "not found".

### 2. Load the catalogs

Read [references/common.md](references/common.md) always. Then read each one that matches the card, since one system often matches several:

- [references/classical-ml.md](references/classical-ml.md) for tabular models, forecasting, backtests and recommenders.
- [references/deep-learning.md](references/deep-learning.md) for neural network training, vision, audio, fine-tuning and generative models.
- [references/llm-apps.md](references/llm-apps.md) for anything that calls an LLM, including prompts, RAG and LLM judges.
- [references/agents.md](references/agents.md) for model-driven loops with tools or memory.
- [references/other-systems.md](references/other-systems.md) for RL and probabilistic or causal models, and for any system the other catalogs miss. It holds the procedure for deriving a catalog for an unlisted system.

General evidence rules live in `eval-ai`. These catalogs hold only the checks specific to their system type.

Done when every system type on the card has a catalog, read or derived.

### 3. Grill the intent

Start at the root of the tree with the decision branches in `common.md`, then the matching catalogs. Keep going until you can write the **intent contract**:

- The decision or action the output changes.
- The success metric and the number it must reach, fixed independently of current results.
- The baseline it must beat.
- Which errors cost most, and what happens when the system is wrong.
- Constraints on cost, latency, hardware, privacy and data rights.
- The result that would end the project.

If the user asks to skip straight to review, draft the contract from the card and carry every inferred line into step 5 as an open question.

Done when every contract line is the user's decision or a marked open question. For an idea with no code, go to step 6.

### 4. Review on four axes

Pin the scope. By default the scope is the whole path from raw data or user input to the final metric or action. If the user names a commit or branch, review that diff plus any code on the same path it feeds, because AI bugs usually sit upstream of the changed line.

Spawn one sub-agent per axis, all together in the foreground. Each prompt carries the system card, the intent contract, the scope, the paths of the loaded catalogs, the proof rules and the finding format.

- **Intent**: requirements in the contract that the build misses or implements wrongly, and behaviour nobody asked for.
- **Evidence**: this sub-agent follows the `eval-ai` skill in audit mode, given the absolute paths of `../eval-ai/SKILL.md` and its `references/` folder. It scores every eval stage, and every claim on the card gets a verdict, a grade and a type. Supported means the evidence holds at Internal grade or above. Unsupported means evidence exists and fails. Untested means no evidence exists. It reports findings in the format below and appends `eval-ai`'s scorecard.
- **Mechanics**: code that runs and does the wrong thing. Apply the Mechanics entries in the catalogs and the repo's documented standards. A documented repo standard overrides a catalog entry.
- **Exposure**: what happens on real input, including adversarial input, drift, runaway cost, private data and irreversible actions.

Every catalog entry for the axis must end up applied, marked not applicable with a reason, or flagged as a finding.

**Proof rules.** Prove findings by running them. Scripts go in a temporary folder outside the project and change nothing in it. Each check stays under two minutes and uses no paid API call or GPU training. A larger check becomes the "cheapest check" of a suspected finding. Check claims about a library or model API against its current docs, and send no user email or other personal details in web requests.

**Finding format.**

```
[CONFIRMED|SUSPECTED] [invalidates a claim|degrades results|hygiene] <catalog entry or rule>
<file:line>: what happens, and what it does to the result
Proof: command and observed output. For SUSPECTED: the cheapest check that would settle it.
Fix: the change to make.
```

CONFIRMED requires observed output or a code path with one possible reading.

Done when all four reports are back. Show them under separate `## Intent`, `## Evidence`, `## Mechanics` and `## Exposure` headings without merging or reranking across axes, so a strong axis can't hide a failing one.

### 5. Grill the findings

Each finding that survives the user's reading is a decision with four possible answers: fix now, measure first, accept the stated risk, or out of scope. Group the findings that one decision settles. Findings often reopen the tree, for instance when leakage removal means the success number needs revisiting, so recompute the frontier after each round.

Done when the frontier is empty, every finding has an answer, and every open question from step 3 is closed.

### 6. Close

Give the user the final record:

- The intent contract.
- A table of findings and their answers.
- The eval scorecard, with stage statuses and claim grades.
- Claims the evidence supports, and claims to withdraw.
- Work in order, with any measurement that can change later decisions placed first.

Change code only after the user confirms this record.
