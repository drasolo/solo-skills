# solo-skills

Agent skills for building and checking AI work, and for running several coding agents at once, alone or in a team. They follow the Agent Skills format, so Claude Code and Codex both read them.

| Folder | What it is |
|---|---|
| `grill-ai` | Grills you on an AI system's decisions, then reviews its code and evidence. |
| `eval-ai` | Designs, builds or audits evaluations and benchmarks of AI systems. |
| `alignment-grill` | Keeps people and agents aligned, with a task board on GitHub. |
| `agent-router` | Picks the agent, model and stages for each task. |
| `alignment-referee` | The GitHub Action behind alignment-grill's board. Not a skill. |

## grill-ai

Asks you about an AI system's decisions one round at a time, then reviews the code and the evidence. Covers classical ML, deep learning, LLM apps, RAG, agents and other model-based systems, with one reference file per kind.

## eval-ai

Designs, builds or audits an evaluation, scaled to the work: ML, deep learning, forecasting, LLM apps, RAG, agents and trading backtests. `LATER.md` lists checks that are parked until a project needs them.

## alignment-grill

Keeps people and agents agreeing on the goal, the decisions, the facts and the words, and keeps a task board on GitHub so two people or agents don't do the same work.

- **Modes:** kickoff, decide, check, defend.
- **Profiles:** hackathon, solo with many agents, uni group project, long work project, research or thesis, client work, open-source, incident response.
- **Where the data lives:** GitHub Issues labelled `task`, `decision` and `review`, a pinned `alignment` issue, and a GitHub Project. The code repo only gets one workflow file and one line in `AGENTS.md`.
- **The referee:** a GitHub Action is the only writer of task state. It handles `/claim`, `/done`, `/stuck`, `/vote` and the other commands, refuses overlapping claims and expires leases. It lives in the `alignment-referee` folder, and a repo uses it as `<owner>/solo-skills/alignment-referee@v1`.

It runs only when you invoke it.

## agent-router

Picks the agent (Claude Code, Codex, Antigravity), model and effort for a task, splits it into plan, implement and review stages, and prints a ready command per stage. The review stage always uses a different model family from the implement stage. Every routing and outcome goes to `~/.agent-router/outcomes.jsonl`, so the rules can be measured later.

The routing table in `references/rules.md` holds starting guesses. No bake-off has run yet; `references/bakeoff.md` describes how to run one.

Agents can call it on their own, and alignment-grill calls it when it fills a task's stages.

## alignment-referee

A composite GitHub Action in Python, standard library only. Setup is in its own README. Tests: `cd alignment-referee && python -m unittest`.

## Install

Claude Code reads `~/.claude/skills`; Codex reads `~/.agents/skills`. Copy the skill folders to both:

```
git clone https://github.com/drasolo/solo-skills
cd solo-skills
for s in grill-ai eval-ai alignment-grill agent-router; do
  cp -r $s ~/.claude/skills/
  cp -r $s ~/.agents/skills/
done
```

alignment-grill and agent-router also have `scripts/install.py`, which copies the skill from `~/.claude/skills` to `~/.agents/skills`. Rerun it after editing one of them.

## Requirements

- Python 3 for the scripts, standard library only.
- The `gh` CLI, logged in, for alignment-grill. Projects need the `project` scope: `gh auth refresh -s project`.
- Whichever of `claude`, `codex` and `agy` you use, for agent-router.

## License

MIT
