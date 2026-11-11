# Routing rules

**Status: starting guesses, not measured.** No bake-off has run yet. The choices are spread
across agents on purpose, so the outcome log collects data on each. Replace a row when a bake-off
or at least 10 logged outcomes of that type say otherwise, and write the date and the evidence in
the Basis column.

Agents: `claude` (Claude Code), `codex` (Codex CLI), `agy` (Antigravity). The family follows the
model, not the agent.

| Type | Stages | Plan | Implement | Review | Basis |
|---|---|---|---|---|---|
| bug-fix | implement, review | | claude / Claude; then codex / GPT | codex / GPT; then agy / Gemini | guess |
| feature | plan, implement, review | claude / Claude | codex / GPT; then claude / Claude | claude / Claude; then agy / Gemini | guess |
| refactor | implement, review | | codex / GPT; then claude / Claude | claude / Claude | guess |
| data-sql | implement, review | | claude / Claude; then codex / GPT | codex / GPT | guess |
| ml-experiment | plan, implement, review | claude / Claude | claude / Claude; then codex / GPT | codex / GPT, with the eval-ai skill's audit if the agent has it | guess |
| docs | implement | | claude / Claude | the person | guess |
| code-review | review | | | a family that did not write the change | rule |
| ui | implement, review | | agy / Gemini; then claude / Claude | claude / Claude; then codex / GPT | guess |
| research | implement | | claude / Claude; then agy / Gemini | | guess |
| ops-config | implement, review | | codex / GPT | claude / Claude | guess |

Small tasks drop the plan stage. Large tasks add one (plan by the first choice of the
implement family's opposite: Claude when GPT implements, GPT when Claude implements). Docs and
research skip review unless the person asks. When two types fit, the type is the one the
criterion checks: an end-to-end click test makes it ui, a unit test of new logic makes it feature.

The ml-experiment review prompt names the checks explicitly: split leakage, a baseline, and
whether the result survives another seed or split.

When Antigravity implements, it can't run shell commands headless (see `preamble.md`), so the
review stage runs the criterion and the person commits.

## Effort

| Size | Plan | Implement | Review |
|---|---|---|---|
| small | none | medium | medium |
| normal | high | high | high |
| large | xhigh | high | xhigh |

Claude model: `sonnet` for small tasks, `opus` otherwise. Inside Antigravity, pick the model id
of the family the row names, at the level matching the effort.

Map to each agent: Claude Code `--effort <level>` (low to max); Codex
`-c model_reasoning_effort=<level>`; Antigravity `--effort <level>`, and some of its model ids
carry the level in the name: pick the id that matches. When an agent rejects a level, use the
nearest one it accepts and say so.
