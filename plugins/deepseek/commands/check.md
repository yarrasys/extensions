---
description: Offline preflight — is deepseek ready to delegate? (claude/git on PATH, key resolvable)
---
Run the deepseek skill's offline `check` preflight:

    uv run --locked "${CLAUDE_PLUGIN_ROOT}/skills/deepseek/deepseek.py" check

(If `${CLAUDE_PLUGIN_ROOT}` isn't set, use `uv run --locked <SKILL_DIR>/deepseek.py check`.)

Report the result plainly. This is offline — it confirms `claude`/`git` are on
PATH and a `DEEPSEEK_API_KEY` is resolvable, but does **not** verify the DeepSeek
endpoint or that the key is valid (that's only exercised on the first real
`delegate`). If the key is missing, tell the user to set it themselves (e.g. via
the kdbx skill) — never author or echo the key value.
