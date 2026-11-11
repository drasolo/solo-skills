---
name: agent-router
description: Pick the coding agent, model and effort for a task, and split it into plan, implement and review stages across agents. Use when choosing which agent or model should do a task, when handing work to Codex, Claude Code or Antigravity, or when a task needs a cross-agent review.
---

Route a task to the agents best placed to do it, then print the commands that start them. v1 recommends and the person launches. Every routing and every outcome goes to a log, so the rules can later be measured instead of guessed.

**Family** means the maker of the model (Claude, GPT, Gemini), not the tool running it: Antigravity can run Claude models, and then it counts as Claude.

## 1. Classify

Put the task in exactly one type from [references/task-types.md](references/task-types.md), and size it by scope: **small** (one file, one behaviour), **normal**, or **large** (several areas, or the approach is unclear). Show the type and size with one line of reasoning. If the person corrects either, use theirs.

Done when the type and size are shown and accepted.

## 2. Route

Look up the type in [references/rules.md](references/rules.md): it gives the stages, and for each stage a first and second choice of agent and family. Effort comes from the size rule in the same file. Then apply, in order:

- The review stage uses a different family from the implement stage.
- The person's word wins: when they say an agent is out of quota or they prefer another, take it and note the reason.
- An agent that is not installed (`claude --version`, `codex --version`, `agy --version` fail) is skipped for its second choice.
- Find current model ids by looking: `agy models`, the `model` line in `~/.codex/config.toml`, and the Claude Code aliases `opus`, `sonnet`, `haiku`.

If the type has no rule, choose from the capability cards in [references/cards/](references/cards/) and say that no rule covered it.

Done when every stage has an agent, family, model id and effort, and the review family differs from the implement family.

## 3. Print the commands

Find the criterion's command: the one the criterion names, else the repo's own test command (`pyproject.toml`, `package.json` scripts, `Makefile`). For each stage, write the prompt from [references/preamble.md](references/preamble.md) to a file outside the repo and print the command that starts the agent with it. Stages run in order. Each stage reads the previous one's output from the task issue, or, with no issue, from the handoff file `<task>-handoff.md` that you create next to the prompt files and every stage appends to.

Done when the person has one ready command per stage.

## 4. Log

Record the routing, and record each stage's outcome when the person reports it or you observe it:

```
python <this skill>/scripts/log_outcome.py routed --task T-12 --type feature --size normal --stage implement --agent codex --family gpt --model <id> --effort high [--override "<reason>"] [--type-corrected-from bug]
python <this skill>/scripts/log_outcome.py finished --task T-12 --stage implement --minutes 25 --retries 1 --review changes
```

The log is `~/.agent-router/outcomes.jsonl`, outside every repo. When the task is on an alignment board, also put the routing in its **Agent / model:** field.

Done when the routing line is in the log, and each finished stage has its line.

## The bake-off

The rules start as guesses. To replace them with measurements, run the procedure in [references/bakeoff.md](references/bakeoff.md) when the person asks for it.
