# AGENTS.md

Guidance for AI coding agents working **in** this repository (and using the skill it ships).
See also [SKILL.md](SKILL.md) (how to *use* kdbx) and [CONTRIBUTING.md](CONTRIBUTING.md).

## What this repo is

`kdbx` — a single PEP-723 Python entry (`kdbx.py`) plus focused modules in `kdbx_core/`,
shipped as a Claude Code skill. It manages credentials in key-file-only KeePassXC KDBX4 vaults.

## Golden rule (security)

**Never author or observe a secret value.** Your job is the entry **path / variable name** only.
- To store a value, instruct the human to pipe it on *their* terminal: `kdbx set api/openai < secret.txt`,
  or use `--from-env VAR` set by an outer orchestrator (CI). Never `echo SECRET | kdbx set …`.
- Prefer `kdbx run -- <cmd>` (inject, never print) over `export` or `get --reveal`.
- Never put a secret value on argv, in a commit, in a test fixture, or in the transcript.

## Working in the codebase

- **Run the tests:** `uv run --with pytest --with pykeepass --with python-dotenv --with filelock --with platformdirs python -m pytest`
- **Lint:** `uvx ruff check .` (and `uvx ruff format .`).
- **Smoke the locked entrypoint:** `uv run --locked kdbx.py --version`.
- **Engine boundary:** only `kdbx_core/vault.py` may import `pykeepass`. Keep its public interface
  engine-agnostic (plain paths/str in and out) — it is the single swap point for a permissive engine.
- **TDD:** add a failing test first; keep the suite green. CI runs on Linux/macOS/Windows.
- **Lockfile:** if you change `kdbx.py` deps, run `uv lock --script kdbx.py` and commit `kdbx.py.lock`.
- **Docs of record:** the design spec and plan live under `docs/superpowers/`.

## Tracking

File bugs, ideas, and follow-ups as **GitHub Issues**: https://github.com/yarrasys/kdbx-skill/issues
