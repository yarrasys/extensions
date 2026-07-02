---
description: Offload a simple, mechanical dev task to DeepSeek (worktree-isolated, reviewed as a patch)
argument-hint: --task "…" [--file F] [--verify CMD] [--in-place] [--model M]
---
The user is explicitly asking to delegate this task, so run the deepseek skill's
`delegate` operation **as the sanctioned, user-initiated path** — set the
`DEEPSEEK_DELEGATE_APPROVED=1` sentinel so the autonomy-guard recognizes it (this
is required in `explicit` mode; harmless otherwise):

    DEEPSEEK_DELEGATE_APPROVED=1 uv run --locked "${CLAUDE_PLUGIN_ROOT}/skills/deepseek/deepseek.py" delegate $ARGUMENTS

(If `${CLAUDE_PLUGIN_ROOT}` isn't set in your shell, use the deepseek skill's
documented invocation — `uv run --locked <SKILL_DIR>/deepseek.py delegate …` —
keeping the `DEEPSEEK_DELEGATE_APPROVED=1` prefix.)

Then read the single JSON **receipt** on stdout and act on `status` — do **not**
apply anything the skill withheld:

- `patch_ready` — success, isolated. Review the patch at `receipt.patch`, then land
  it with `/deepseek:apply <patch>`.
- `applied` — success, `--in-place`. Already in the working tree; review `git diff`.
- `verify_failed` / `denied` / `budget_exceeded` — nothing was applied. Report the
  reason (`receipt.verify.tail` on verify failures); don't retry blindly.
- `error` — the child failed. Surface the message; suggest `/deepseek:check`.

Report the outcome compactly: status, files changed, cost, turns. Never paste the
child's full output into the conversation — the receipt is the point.
