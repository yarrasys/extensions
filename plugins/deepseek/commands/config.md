---
description: Print the effective merged deepseek config (defaults + .deepseek.json)
---
Print the effective merged deepseek configuration (built-in defaults overlaid
with the nearest `.deepseek.json` found by walking up from cwd):

    uv run --locked "${CLAUDE_PLUGIN_ROOT}/skills/deepseek/deepseek.py" config

(If `${CLAUDE_PLUGIN_ROOT}` isn't set, use `uv run --locked <SKILL_DIR>/deepseek.py config`.)

Show the JSON. Point out the `mode` (`explicit` / `suggest` / `auto`) since that
governs the autonomy-guard, and the `auto` caps/globs if present. This is
read-only — it never spends tokens or edits anything.
