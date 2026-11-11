"""Copy this skill to the folder Codex and other agents read (~/.agents/skills/<name>).

The copy under ~/.claude/skills is the master. Rerun after every edit; the target is replaced.
"""

import shutil
from pathlib import Path

skill = Path(__file__).resolve().parents[1]
target = Path.home() / ".agents" / "skills" / skill.name
if target.exists():
    shutil.rmtree(target)
shutil.copytree(skill, target, ignore=shutil.ignore_patterns("__pycache__"))
print(f"installed {skill.name} -> {target}")
