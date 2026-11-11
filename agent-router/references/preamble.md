# Stage prompt and commands

## The prompt

Every stage prompt starts with the same preamble, whatever the agent, so alignment does not
depend on which instruction files a tool reads.

```
You are the <stage> stage of task <T-n or a short name>, working for <Person>.
Sign comments and commits as [<Person> / <Agent> <Family>].

Before you start:
- If this repo has an alignment board (AGENTS.md names a pinned GitHub issue), read that issue's "For agents" section and follow it: run its check before /claim and before /done, and act only on decided decisions.
- Read the task: <issue URL, or the task text below>.
- Read the previous stage's output: <plan comment URL or handoff file path>, if there is one.

Your stage:
- plan: write the plan as one comment on the task (or the handoff file): steps, files, the decisions it relies on, how the criterion will be checked. Change no code.
- implement: follow the plan. Write down every departure from it, and why, before /done. Start commit messages with the task ID.
- review: review the diff against the task's criterion, the decisions it cites, and the plan. Run the check yourself. Do not edit code: ask for changes in a comment (/changes on a board), or approve.

Done when: <the task's criterion>.
```

Then the task text.

## The commands

Write the prompt to a file outside the repo (for example in a temp folder), then, from the repo
root, in bash:

| Agent | Command |
|---|---|
| Claude Code | `claude -p "$(cat <prompt file>)" --model <alias or id> --effort <level> --permission-mode acceptEdits --allowedTools "Bash(git *)" "Bash(<test command> *)"` |
| Codex | `codex exec -m <model id> -c model_reasoning_effort=<level> -s workspace-write "$(cat <prompt file>)"` |
| Antigravity | `agy -p "$(cat <prompt file>)" --model <model id> --effort <level> --mode accept-edits` |

Headless permissions differ:
- **Claude Code** edits files under `acceptEdits` but runs no shell command unless `--allowedTools` names it. Allow git and the criterion's command, nothing wider.
- **Codex** under `workspace-write` edits, runs commands and commits inside the repo.
- **Antigravity** edits files, but headless mode denies every shell command unless a `permissions.allow` rule in its settings covers it (its error names the form `command(<target>)`). Until the person sets such a rule, it edits and the person runs the check and commits. Give it no blanket allow-all.

Fill the signature line yourself (`[Ana / Codex GPT]`), so the agent copies it rather than inventing one.

For the review stage, the reviewer must run the check but change no code:
- Codex: `-s read-only` (it can still run read commands).
- Claude Code: drop `--permission-mode acceptEdits`, keep `--allowedTools` for git and the check command, and add `--disallowedTools Edit Write`. Plan mode would block the check.
- Antigravity: `--mode plan`; it reads but can't run the check headless, so prefer another agent as reviewer.
