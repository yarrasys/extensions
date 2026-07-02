# AGENTS.md — deepseek

Guidance for AI coding agents working **on the deepseek skill** (`skills/deepseek/`). See
[SKILL.md](SKILL.md) for how to *use* deepseek, and the repo-root
[AGENTS.md](../../AGENTS.md) / [CONTRIBUTING.md](../../CONTRIBUTING.md) for monorepo-wide norms.

## What deepseek is

A single PEP-723 Python entry (`deepseek.py`) plus focused modules in `deepseek_core/`, shipped as
a Claude Code skill. It shells out to a nested, headless `claude` process pointed at DeepSeek's
Anthropic-compatible endpoint to do bounded, mechanical edits — trading the parent session's own
tokens for a cheaper delegate, isolated in a git worktree and returned as a reviewable patch.

## Golden rules

- **Edit the source, not a mirror.** There is no `plugins/deepseek/` yet (no plugin wrapper for
  this skill exists). If one is added later: ✅ `skills/deepseek/` · ❌ any bundled-skill symlink
  under `plugins/deepseek/skills/deepseek/` — same rule as kdbx.
- 🔑 **The recursion guard is load-bearing — never unset or work around `DEEPSEEK_DELEGATE_DEPTH`.**
  `guardrails.is_recursive()` checks *presence* of that var in `os.environ`; `run_child` sets it
  (via `build_child_env`) in the nested `claude`'s environment together with
  `disabledSkills: ["deepseek"]` in its settings. Removing either mechanism, or clearing the var
  before calling `cmd_delegate` again in the same process, reopens unbounded self-delegation. Any
  change touching `guardrails.is_recursive`, `runner.build_child_env`, or
  `runner.write_child_settings` needs a test asserting the guard still fires.
- **Pure vs. side-effecting module boundary — keep it that way:**
  - **Pure, unit-tested directly (no subprocess/filesystem fakes needed):** `config.py`
    (discovery/merge — takes/returns dicts and `pathlib.Path`s it never touches),
    `guardrails.py` (recursion/deny-glob/budget predicates over plain data), `receipt.py`
    (shapes the receipt dict), and the argv/env/settings *builders* in `runner.py`
    (`build_argv`, `build_child_env`, `write_child_settings`, `resolve_key` — these build inputs,
    they don't execute anything).
  - **Side-effecting, tested via real git tmp repos + the fake `claude`:** `workspace.py` (every
    git worktree/diff/patch operation — `is_dirty`, `numstat`, `create_worktree`, `write_patch`,
    `remove_worktree`, `apply_patch`) and `runner.run_child` (the actual `subprocess.run` of the
    nested `claude`). Tests for these use the `git_repo` and `fake_claude` fixtures in
    `tests/conftest.py`, not mocks — a fake `claude` script stands in for the real CLI so tests
    stay hermetic and fast without hitting a real DeepSeek endpoint.
  - New logic belongs on the pure side whenever it *can* be pure — push subprocess/filesystem
    calls to the edges (`workspace.py`, `runner.run_child`) and keep everything else testable
    without a real git repo or process.

## Working in the codebase

- **Tests** (suite lives in `skills/deepseek/tests/`):
  `uv run --with pytest --with pykeepass --with python-dotenv --with filelock --with platformdirs --with "mcp>=1.0,<2" python -m pytest`
- **Lint:** `uvx ruff check .` / `uvx ruff format .`.
- **Smoke the locked entrypoint:** `uv run --locked skills/deepseek/deepseek.py --version`.
- **TDD:** failing test first; keep the suite green. CI runs on Linux/macOS/Windows — the
  `fake_claude` fixture writes both a POSIX shebang script and a `claude.bat` launcher so the fake
  binary resolves on `windows-latest` too.
- **Lockfiles:** changing `deepseek.py`'s PEP-723 deps → `uv lock --script skills/deepseek/deepseek.py`,
  commit `deepseek.py.lock`. It currently declares no third-party dependencies (empty lock is
  expected and correct).
- **CHANGELOG:** record changes in `skills/deepseek/CHANGELOG.md` under `## [Unreleased]`; release
  tag = `deepseek/v<version>`.
- **Docs of record:** design spec + task plan under `.superpowers/sdd/` at the repo root.

## Open items

- **"Defining simple"** — `auto.allowTasks` (`docstrings`, `formatting`, `boilerplate`, `tests`,
  `comments`, `rename`) is a fixed, unvalidated string list; nothing in `delegate` actually checks
  the `--task` text against it or classifies task complexity. The *enforcement* of "is this task
  actually simple enough to auto-delegate" is entirely a parent-agent-side judgment call per the
  `mode` contract in SKILL.md — `deepseek` itself has no notion of task difficulty. If this needs
  to become a real guardrail (not just a config knob the parent is trusted to honor), that's
  unbuilt design work, not a bug.
- **`maxCostUsdPerSession`** is parsed into the merged config but never checked — there's no
  session-level cost ledger. Enforcing it needs a place to persist cumulative spend across
  `delegate` invocations (a session id, a state file, or the parent tracking it itself); out of
  scope for v1 (see SKILL.md's "v1 limitations").
