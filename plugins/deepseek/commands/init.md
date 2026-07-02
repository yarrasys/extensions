---
description: Scaffold a starter .deepseek.json in the current project (refuses to overwrite)
---
Scaffold a starter `.deepseek.json` with safe defaults in the current directory
using the deepseek skill's `init` operation:

    uv run --locked "${CLAUDE_PLUGIN_ROOT}/skills/deepseek/deepseek.py" init

(If `${CLAUDE_PLUGIN_ROOT}` isn't set, use `uv run --locked <SKILL_DIR>/deepseek.py init`.)

`init` refuses to overwrite an existing `.deepseek.json` (exit 4) and also adds
`.deepseek/` to the project `.gitignore` so worktrees and patch files stay
untracked. After it runs, show the user the generated file and remind them the
default `mode` is `suggest` (propose-then-confirm) — change it to `explicit` or
`auto` to shift how much initiative the agent has. No secret ever goes in this
file.
