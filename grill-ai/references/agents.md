# Agent catalog

Model-driven loops with tools, memory or sub-agents. Also load `llm-apps.md`.

## Decision branches

- **Need for a loop.** Do the steps vary with the input? If they are known in advance, a fixed workflow is cheaper and easier to test.
- **Autonomy.** Which actions run alone, which need approval, and which are never available?
- **Number of agents.** What does each extra agent add that one agent with the same tools lacks? What context does each handoff lose?
- **Done condition.** How does the system know the job is finished, independently of the agent saying so?
- **Limits.** What are the turn, token, money and wall-clock budgets, and what happens when one runs out?
- **Memory.** What persists between runs, who can write it, and how does a stale or wrong entry get removed?

## Evidence

- **Single-agent baseline missing.** A multi-agent design has no comparison to one agent with equal tools and budget.

## Mechanics

- **Unbounded loop.** No limit on turns or spend, or repeated identical tool calls go undetected.
- **Weak tool contract.** Overlapping tools, vague descriptions, or errors the model cannot act on. Return messages saying what failed and what to try.
- **Tool result overflow.** One large output crowds out the task. Paginate and cap results, then tell the model what was cut.
- **Lost instructions after compaction.** Summaries drop constraints or decisions. Test a long run and check that the constraints still apply.
- **Non-idempotent tools.** A retry or resumed run repeats a side effect. Use idempotency keys or check state first.
- **Dropped parallel results.** Tool results get mismatched to calls, or a partial failure is lost.
- **Unobservable runs.** No trace of each prompt, tool call, result, cost and decision. A failure cannot be replayed.
- **Crash recovery gaps.** A failure mid-run leaves partial state with no resume or cleanup path.

## Exposure

- **Lethal trifecta.** One agent holds private data, reads untrusted content and can send data out. Remove one of the three or gate the outbound channel, then attack it with planted instructions.
- **Excess privilege.** Tools hold broader credentials than the task needs. Scope them per task and user.
- **Irreversible actions.** Payments, deletes, deploys and outbound messages run without approval or undo.
- **Unsandboxed execution.** Generated code or shell commands can reach the host, the network or secrets.
- **Memory poisoning.** Untrusted content gets written to memory and steers later runs.
- **Approval fatigue.** So many prompts appear that humans approve everything. Put approval on the actions that matter.
- **Runaway delegation.** Sub-agents spawn sub-agents without a shared budget.
