# solo-skills

Two agent skills for working with several coding agents at once, alone or in a team. They follow the Agent Skills format, so Claude Code and Codex both read them.

## alignment-grill

Keeps people and agents agreeing on the goal, the decisions, the facts and the words, and keeps a task board on GitHub so two people or agents don't do the same work.

- **Modes:** kickoff, decide, check, defend.
- **Profiles:** hackathon, solo with many agents, uni group project, long work project, research or thesis, client work, open-source, incident response.
- **Where the data lives:** GitHub Issues labelled `task`, `decision` and `review`, a pinned `alignment` issue, and a GitHub Project. The code repo only gets one workflow file and one line in `AGENTS.md`.
- **The referee:** a GitHub Action is the only writer of task state. It handles `/claim`, `/done`, `/stuck`, `/vote` and the other commands, refuses overlapping claims and expires leases. It lives in a separate repo, `alignment-referee`, which isn't published yet. Until it is, kickoff asks you for the action's `owner/repo`.

It runs only when you invoke it.

## agent-router

Picks the agent (Claude Code, Codex, Antigravity), model and effort for a task, splits it into plan, implement and review stages, and prints a ready command per stage. The review stage always uses a different model family from the implement stage. Every routing and outcome goes to `~/.agent-router/outcomes.jsonl`, so the rules can be measured later.

The routing table in `references/rules.md` holds starting guesses. No bake-off has run yet; `references/bakeoff.md` describes how to run one.

Agents can call it on their own, and alignment-grill calls it when it fills a task's stages.

## Install

Claude Code reads `~/.claude/skills`; Codex reads `~/.agents/skills`.

```
git clone https://github.com/drasolo/solo-skills
cp -r solo-skills/alignment-grill solo-skills/agent-router ~/.claude/skills/
python ~/.claude/skills/alignment-grill/scripts/install.py
python ~/.claude/skills/agent-router/scripts/install.py
```

The two `install.py` scripts copy each skill from `~/.claude/skills` to `~/.agents/skills`. Rerun them after editing a skill.

## Requirements

- Python 3 for the scripts, standard library only.
- The `gh` CLI, logged in, for alignment-grill. Projects need the `project` scope: `gh auth refresh -s project`.
- Whichever of `claude`, `codex` and `agy` you use, for agent-router.

## License

MIT
