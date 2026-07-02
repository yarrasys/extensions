# Design note — `deepseek` plugin wrapper

**Date:** 2026-07-02
**Status:** Design (right-sized — no separate implementation plan; build TDD directly, review diff)
**Repo:** `yarrasys/extensions`
**Follows:** `2026-07-02-deepseek-delegation-design.md` (the skill; plugin was its documented follow-up)

## Why a plugin at all

The skill already *hard-enforces* recursion (`DEEPSEEK_DELEGATE_DEPTH` → exit 4), `denyGlobs`,
and cost caps in-script. What it only *recommends* — the `mode` autonomy contract — is where the
plugin earns its keep. Two contracts are genuinely unenforced by the skill today:

1. **auto-mode isolation.** `config.py:47` forces `auto.isolate = True` in the merged config, but
   `ops_delegate.py:55` computes `isolate = not args.in_place` and never consults `mode`/`isolate`.
   So `delegate --in-place` in `auto` mode runs in-place — the "non-overridable" isolation isn't.
2. **explicit-mode initiative.** Nothing blocks an agent-initiated `delegate` when `mode: explicit`.

A `PreToolUse` hook turns both hard. That is the plugin's reason to exist.

## Scope (YAGNI)

- ✅ **PreToolUse hook** — the enforcement.
- ✅ **`/deepseek:*` commands** — thin wrappers; `delegate` doubles as the *sanctioned* user-initiated path.
- ❌ **MCP server — deferred.** Commands already give the UX and the sanctioned path; an MCP
  `delegate` tool would be redundant surface. Revisit only if a structured/programmatic caller appears.

## The hook — `plugins/deepseek/hooks/guard.py`

Same shape as `plugins/kdbx/hooks/guard.py`: stdlib-only (no `uv`, Python 3.8+), runs per Bash
call, **fails OPEN** (any parse/read error → allow; a guard must never brick the shell). Decision
contract: deny = print `hookSpecificOutput` with `permissionDecision: "deny"`, exit 0; allow = no output.

**Applies only to Bash commands that invoke `deepseek … delegate`** (program is `deepseek`/`deepseek.py`
directly or via `uv run`/`uvx`; op token == `delegate`). Reuses kdbx's segment-split + leading-`VAR=`
program parsing. Non-delegate ops (`check`/`config`/`apply`/`init`) and all other Bash → allow.

For a delegate call, discover the effective **mode** by walking up from cwd for `.deepseek.json`
and reading its top-level `"mode"` (default `"suggest"`; unreadable/absent → `"suggest"` = no block).
Then apply, in all modes unless noted:

| Rule | Condition | Deny message gist |
|------|-----------|-------------------|
| Recursion | `DEEPSEEK_DELEGATE_DEPTH` in env | already delegating — refuse to nest (belt-and-suspenders w/ skill's exit 4) |
| Auto isolation | `mode == "auto"` **and** `--in-place` in tokens | auto mode forces worktree isolation; drop `--in-place` |
| Explicit initiative | `mode == "explicit"` **and** sentinel absent | explicit mode — delegate must be user-initiated via `/deepseek:delegate` |

`suggest` (default) blocks nothing here — the parent proposes-then-runs after user confirmation;
that confirmation is behavioral, not something a Bash hook can see.

### The sanctioned marker (explicit mode)

`DEEPSEEK_DELEGATE_APPROVED=1`, supplied as a leading env assignment on the delegate command by the
`/deepseek:delegate` command template (or exported in the user's env). The hook treats its presence
(inline `VAR=1` prefix **or** `os.environ`) as "user-initiated → allow". Enforcement lives entirely
in the plugin; the skill CLI is untouched.

**Honest guarantee (stated in the plugin README):** this stops an *over-eager cooperative* agent —
same threat model as kdbx's role-guard and the whole `mode` contract. It is **not** an unforgeable
sandbox; an agent that chooses to could set the sentinel itself. It raises the bar and makes any
bypass a deliberate, visible act.

## Commands — `plugins/deepseek/commands/*.md`

Five thin wrappers (kdbx ships five), each invoking the bundled skill per its SKILL.md invocation:

- **`delegate.md`** — the sanctioned path: instructs the agent to run delegate with
  `DEEPSEEK_DELEGATE_APPROVED=1` set, passing `$ARGUMENTS`, then read the JSON receipt and act on
  `status` (patch_ready → review + `/deepseek:apply`; verify_failed/denied/budget_exceeded → report, nothing applied).
- **`apply.md`** — `apply <patch>` a prior worktree patch.
- **`check.md`** — offline preflight.
- **`config.md`** — print merged effective config.
- **`init.md`** — scaffold `.deepseek.json`.

## Manifests, bundling, wiring

- `plugins/deepseek/.claude-plugin/plugin.json` — `name: deepseek`, `version: 0.1.0`, description, MIT, keywords.
- `plugins/deepseek/hooks/hooks.json` — PreToolUse/Bash → `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/guard.py" || exit 0`.
- **Symlink-bundle the skill:** `ln -s ../../../skills/deepseek plugins/deepseek/skills/deepseek` — edit the source, never the mirror.
- `.claude-plugin/marketplace.json` — add `deepseek` entry, `version: 0.1.0` (synced to plugin.json).
- `pytest.ini` — append `plugins/deepseek/tests`.
- `plugins/deepseek/README.md` — mirror kdbx's; include the honest-guarantee statement.
- `skills/deepseek/CHANGELOG.md` — note the plugin wrapper under `## [Unreleased]`.
- Repo `README.md` + `llms.txt` — note the plugin alongside kdbx.

## Tests — `plugins/deepseek/tests/test_plugin_guard.py`

Unit tests on `guard.decide()` (no subprocess), config discovery via `tmp_path` `.deepseek.json`:
allow non-delegate Bash; allow delegate in `suggest`; **deny** auto+`--in-place`, allow auto without it;
**deny** explicit without sentinel, allow explicit with inline sentinel and with env sentinel;
**deny** on `DEEPSEEK_DELEGATE_DEPTH`; parse `uv run … deepseek.py delegate`; fail-**open** on
missing/garbage `.deepseek.json`. No MCP tests (no MCP).

## Dogfooding — narrow, honest smoke test

Delegation as labor-saving doesn't pay here (the substance is the hook — careful TDD, not blind
delegation; the boilerplate is too trivial for the worktree ceremony to break even). So dogfood
**once, as a smoke test** of the skill's first live DeepSeek call: delegate the **plugin `README.md`**
(genuinely self-contained, low-stakes prose — exactly the skill's scoped use), worktree-isolated,
`--verify true`. Inspect the patch, `apply` if good, and **report how the skill performed**
(status/cost/turns/rough edges). Command `.md` files are written **by hand** — their sentinel wording
is enforcement surface, not boilerplate.

## Out of scope (v1)

- MCP server (above).
- Making the sentinel unforgeable / true sandboxing — out of the threat model.
- Hook honoring `delegate --dir` for config discovery — v1 uses cwd walk-up (matches the skill).
