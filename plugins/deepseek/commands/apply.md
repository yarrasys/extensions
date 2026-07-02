---
description: Land a patch produced by a prior deepseek delegation onto the working tree
argument-hint: <patch-path>
---
Apply a withheld delegation patch (a `.deepseek/edit-*.patch` from an earlier
`patch_ready` receipt) to the real working tree using the deepseek skill's
`apply` operation:

    uv run --locked "${CLAUDE_PLUGIN_ROOT}/skills/deepseek/deepseek.py" apply $ARGUMENTS

(If `${CLAUDE_PLUGIN_ROOT}` isn't set, use the skill's documented invocation:
`uv run --locked <SKILL_DIR>/deepseek.py apply <patch>`.)

Only apply a patch you've reviewed. On success, show `git diff` so the user can
see exactly what landed. If `apply` reports the patch doesn't exist (exit 2) or
fails to apply cleanly, say so — don't hand-edit files to force it.
