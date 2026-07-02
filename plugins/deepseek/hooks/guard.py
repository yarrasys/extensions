#!/usr/bin/env python3
"""deepseek autonomy-guard — a PreToolUse hook that turns the skill's *soft*
`mode` contract into a hard gate on agent-issued `deepseek … delegate` calls.

The skill (skills/deepseek) already hard-enforces recursion, denyGlobs, and cost
caps in-script. What it only *recommends* is the `.deepseek.json` `mode` contract,
which the CLI deliberately never reads. This hook enforces the two gaps:

  - auto mode  → `--in-place` is refused (auto forces worktree isolation);
  - explicit mode → `delegate` is refused unless it carries the sanctioned
    sentinel `DEEPSEEK_DELEGATE_APPROVED` that /deepseek:delegate supplies;
  - recursion → `delegate` is refused when `DEEPSEEK_DELEGATE_DEPTH` is set
    (belt-and-suspenders with the skill's own exit-4 guard).

`suggest` (the default) blocks nothing here — the parent proposes-then-runs after
user confirmation, which a Bash hook cannot observe.

Runs once per Bash tool call, so it is deliberately cheap and dependency-free
(stdlib only, no `uv`, Python 3.8+). It fails OPEN: anything that is not a clear
violation — including parse errors, an unreadable config, or a missing
interpreter — allows the command. A guard must never brick the user's shell.

Decision contract (see https://code.claude.com/docs/en/hooks):
  stdin  = PreToolUse JSON with tool_input.command (+ optional cwd)
  deny   = print hookSpecificOutput JSON with permissionDecision "deny", exit 0
  allow  = no output, exit 0
"""

import json
import os
import pathlib
import re
import shlex
import sys

# The env var the sanctioned /deepseek:delegate path sets to mark a
# user-initiated delegation; and the recursion sentinel the skill sets on the
# nested child's environment.
_SENTINEL = "DEEPSEEK_DELEGATE_APPROVED"
_DEPTH = "DEEPSEEK_DELEGATE_DEPTH"

_MODES = ("explicit", "suggest", "auto")

# Program names that count as the deepseek CLI (directly, or as the script run
# by `uv run`/`uvx`).
_DEEPSEEK = {"deepseek", "deepseek.py"}

# Shell operators separating independent command segments.
_SEG_SPLIT = re.compile(r"\|\||&&|[;|\n]")


def _program(tokens):
    """First non-(VAR=val) token of a segment = the invoked program (basename)."""
    for tok in tokens:
        head = tok.split("=", 1)[0]
        if "=" in tok and not tok.startswith("-") and "/" not in head:
            continue  # leading VAR=value assignment
        return os.path.basename(tok)
    return ""


def _deepseek_op(tokens):
    """If a segment invokes the deepseek CLI (as the program, or via `uv run`),
    return its subcommand string; else None. The program check avoids false
    positives like `echo deepseek delegate ...`."""
    if not tokens:
        return None
    prog = _program(tokens)
    for i, tok in enumerate(tokens):
        if os.path.basename(tok) in _DEEPSEEK:
            if os.path.basename(tok) == prog or prog in ("uv", "uvx"):
                for nxt in tokens[i + 1 :]:
                    if not nxt.startswith("-"):
                        return nxt
                return ""
            return None
    return None


def _has_sentinel(tokens, environ):
    """True if the delegation is sanctioned — either the env var is set in the
    hook's environment, or it appears as a leading `VAR=value` assignment on the
    command itself (how /deepseek:delegate supplies it)."""
    if environ.get(_SENTINEL):
        return True
    for tok in tokens:
        if tok.startswith(_SENTINEL + "="):
            return bool(tok.split("=", 1)[1])
    return False


def read_mode(start):
    """Effective `mode` — walk up from `start` for the nearest `.deepseek.json`
    and read its top-level `mode`. Missing, unreadable, garbage, or an unknown
    value all fail open to `suggest` (which blocks nothing)."""
    try:
        p = pathlib.Path(start)
    except Exception:
        return "suggest"
    for d in (p, *p.parents):
        cfg = d / ".deepseek.json"
        if cfg.is_file():
            try:
                mode = json.loads(cfg.read_text()).get("mode")
            except Exception:
                return "suggest"
            return mode if mode in _MODES else "suggest"
    return "suggest"


def decide(command, *, mode="suggest", environ=None):
    """Return a human-readable deny reason if `command` issues a `deepseek
    delegate` that violates the effective `mode`/recursion contract; else None."""
    if environ is None:
        environ = os.environ
    if not command or not command.strip():
        return None
    for raw_seg in _SEG_SPLIT.split(command):
        seg = raw_seg.strip()
        if not seg:
            continue
        try:
            tokens = shlex.split(seg)
        except ValueError:
            tokens = seg.split()
        if _deepseek_op(tokens) != "delegate":
            continue

        if environ.get(_DEPTH):
            return (
                "deepseek recursion-guard: a delegation is already in progress "
                "(DEEPSEEK_DELEGATE_DEPTH is set). A delegated session must not "
                "delegate again — refuse to nest."
            )
        if mode == "auto" and "--in-place" in tokens:
            return (
                "deepseek autonomy-guard: `auto` mode forces worktree isolation — "
                "`--in-place` is not allowed. Drop `--in-place` so the edit lands "
                "in a reviewable patch, not directly on the working tree."
            )
        if mode == "explicit" and not _has_sentinel(tokens, environ):
            return (
                "deepseek autonomy-guard: `.deepseek.json` mode is `explicit` — "
                "delegation must be user-initiated. Don't self-initiate `delegate`; "
                "ask the user, who can run it via the `/deepseek:delegate` command."
            )
    return None


def main():
    try:
        data = json.load(sys.stdin)
        command = (data.get("tool_input") or {}).get("command", "")
        cwd = data.get("cwd") or os.getcwd()
        reason = decide(command, mode=read_mode(cwd), environ=os.environ)
    except Exception:
        return 0  # fail open — never break the shell
    if reason:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
