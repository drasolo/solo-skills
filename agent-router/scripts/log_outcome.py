"""Append one routing or outcome line to ~/.agent-router/outcomes.jsonl.

    log_outcome.py routed   --task T-12 --type feature --size normal --stage implement
                            --agent codex --family gpt --model <id> --effort high
                            [--override "<reason>"] [--type-corrected-from bug]
    log_outcome.py finished --task T-12 --stage implement --minutes 25 --retries 1
                            --review pass|changes|fail|none [--note "<text>"]

The log lives outside every repo. A future classifier trains on it, so every line keeps the
same fields, with null for the ones that don't apply.
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

LOG = Path.home() / ".agent-router" / "outcomes.jsonl"
FIELDS = ["task", "type", "size", "stage", "agent", "family", "model", "effort", "override",
          "type_corrected_from", "minutes", "retries", "review", "note"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("event", choices=["routed", "finished"])
    p.add_argument("--task", required=True)
    p.add_argument("--stage", required=True, choices=["plan", "implement", "review"])
    p.add_argument("--type")
    p.add_argument("--size", choices=["small", "normal", "large"])
    p.add_argument("--agent", choices=["claude", "codex", "agy", "person"])
    p.add_argument("--family")
    p.add_argument("--model")
    p.add_argument("--effort")
    p.add_argument("--override")
    p.add_argument("--type-corrected-from")
    p.add_argument("--minutes", type=float)
    p.add_argument("--retries", type=int)
    p.add_argument("--review", choices=["pass", "changes", "fail", "none"])
    p.add_argument("--note")
    a = vars(p.parse_args())
    if a["event"] == "routed":
        missing = [k for k in ("type", "size", "agent", "family", "model", "effort") if not a[k]]
        if missing:
            p.error("routed needs --" + ", --".join(m.replace("_", "-") for m in missing))
    line = {"at": datetime.now(UTC).isoformat(timespec="seconds"), "event": a["event"]}
    line |= {k: a[k] for k in FIELDS}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")
    print(f"logged {a['event']} {a['task']} {a['stage']} -> {LOG}")


if __name__ == "__main__":
    main()
