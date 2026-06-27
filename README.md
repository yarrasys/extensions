<div align="center">

# 🔐 kdbx — KeePassXC credentials skill for Claude Code

**Manage per-project, per-environment secrets in key-file-only KeePassXC vaults — and inject them into commands without ever printing them.**

A [Claude Code](https://claude.com/claude-code) skill (and standalone CLI) that replaces `.env`
as the source of truth for secrets, API keys, and tokens.

[![CI](https://github.com/yarrasys/kdbx-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/yarrasys/kdbx-skill/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Claude Code skill](https://img.shields.io/badge/Claude%20Code-skill-8A2BE2.svg)](SKILL.md)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

`kdbx` is a small, self-contained tool for **secrets management** in development: one
[KeePassXC](https://keepassxc.org/) `.kdbx` vault **per project, per environment**, unlocked by a
**key file only** (no master password, fully scriptable), using **KDBX4 + Argon2**. A committed
`.keepassxc.json` pointer maps environment-variable names to vault entries, so a repository
documents its own secret contract — without exposing any values.

It's built for **AI coding agents**: the agent handles entry paths and variable names only and
**never authors or observes a secret value**. Secrets reach your tools via `kdbx run -- <cmd>`
(injected into the child process, never printed) or an explicit, gitignored `kdbx export`.

## Contents

- [Why kdbx](#why-kdbx)
- [Install](#install)
- [Quickstart](#quickstart)
- [How it works](#how-it-works)
- [Operations](#operations)
- [Security](#security)
- [Requirements](#requirements)
- [Development](#development)
- [How it compares](#how-it-compares)
- [Project status](#project-status)
- [License](#license)

## Why kdbx

- 🗂️ **Per project, per env** — `<keepassxc-dir>/<project>/<env>.kdbx`. No shared global vault;
  blast radius is one project + one environment.
- 🔑 **Key-file-only unlock** — no master password, so it's fully scriptable and CI-friendly.
- 🤖 **Agent-safe** — secrets never touch argv, stdout, the transcript, or shell history. `get`
  is masked by default; values are read from stdin / `getpass` / `--from-env`.
- 🚀 **Inject, don't print** — `kdbx run -- npm test` puts mapped secrets in the child's
  environment and runs it; nothing is echoed.
- 📄 **Replaces `.env`** — the committed `vars` map is a git-reviewable secret contract; `export`
  produces a real `.env` only when a tool demands a file.
- 📦 **Zero-install runtime** — a single [PEP 723](https://peps.python.org/pep-0723/) script run
  via [uv](https://docs.astral.sh/uv/); dependencies are pinned and locked, fetched on first run.
- 🔁 **Cross-engine** — vaults interoperate with `keepassxc-cli` and the KeePassXC GUI.

## Install

Install as a Claude Code skill on any machine:

```bash
git clone https://github.com/yarrasys/kdbx-skill ~/.claude/skills/kdbx
```

Claude Code discovers it via `~/.claude/skills/kdbx/SKILL.md`. Update later with
`git -C ~/.claude/skills/kdbx pull`. Invoke the CLI as:

```bash
uv run --locked ~/.claude/skills/kdbx/kdbx.py <op> [args]
```

(For a per-project install, clone anywhere and point your project's skill config at it.)

## Quickstart

```bash
# 1. Drop a pointer at your repo root (committed; contains no secrets)
cat > .keepassxc.json <<'JSON'
{
  "project": "ideas",
  "defaultEnv": "dev",
  "envs": {
    "dev": { "vars": { "OPENAI_API_KEY": "api/openai:password" } }
  }
}
JSON

KDBX=~/.claude/skills/kdbx/kdbx.py

uv run --locked "$KDBX" init                       # create the dev vault + key file (0600)
uv run --locked "$KDBX" set api/openai < key.txt   # store a secret from a file (never on argv)
uv run --locked "$KDBX" get api/openai             # -> (set, hidden)
uv run --locked "$KDBX" check                      # verify the vars map resolves
uv run --locked "$KDBX" run -- npm run dev         # OPENAI_API_KEY is in the child's env, never printed
```

## How it works

- **Discovery.** kdbx walks up from the current directory to the nearest committed
  `.keepassxc.json`. The active environment is `--env` › `$KDBX_ENV` › the pointer's `defaultEnv`.
- **The pointer** declares each env's `vault`/`keyFile` (or omits them to derive default paths)
  and a `vars` map of `ENV_VAR → "group/Title:field"`. See [`references/schema.md`](references/schema.md).
- **The vault** is a standard KDBX4 + Argon2 file unlocked by its key file. The key file is the
  sole secret — back it up; losing it makes the vault unrecoverable.
- **Secrets stay out of the repo** — vaults and key files live under your user config dir, never
  committed. Only the pointer (names, not values) is checked in.

## Operations

| Op | Use |
|----|-----|
| `init [--env E]` | create the vault + key file for an env (refuses to overwrite; 0600) |
| `set PATH [--var NAME] [--from-env VAR] [--raw]` | store a secret (value via stdin/`--from-env`, never argv); optionally register a var mapping |
| `get PATH [--reveal\|--clip]` | masked by default; `--reveal` prints; `--clip` copies (auto-clears) |
| `list [GROUP]` | list entry paths (never values; excludes Recycle Bin) |
| `delete PATH [--purge]` | soft-delete to Recycle Bin; `--purge` removes permanently |
| `mv OLD NEW` | rename/move an entry; rewrites affected var mappings |
| `run [--env E] -- CMD…` | inject the env's mapped vars into a child process and run it |
| `export [--out F]` | render mapped vars as a 0600 dotenv (for tools that need a file) |
| `import FILE` | read an existing `.env` into the vault + var map |
| `check` | verify every mapped var resolves (non-zero exit on drift) |
| `envs` | list configured envs; mark the active one |
| `rekey [--env E]` | rotate the key file |

Exit codes: `0` ok · `2` not-found · `3` locked/key-file-missing · `4` confirmation-required
(prod or `$KDBX_ENV`-inherited mutating op without `--yes`) · `5` drift · `6` vault-changed · `7` runtime.

## Security

- **The agent never authors or observes a secret value** — it handles paths and variable names
  only. Store values by piping on your own terminal (`kdbx set PATH < secret.txt`) or via an outer
  orchestrator's `--from-env VAR`. Never `echo SECRET | kdbx set …`.
- Vault, key file, and exported `.env` are `0600` (POSIX) / owner-only ACL (Windows).
- `delete` soft-deletes (recoverable); mutating **prod** or a `$KDBX_ENV`-inherited env requires `--yes`.
- Full threat model, `run` trust boundary, and rotation/leak runbooks: [`references/security.md`](references/security.md).
- Reporting vulnerabilities: [`SECURITY.md`](SECURITY.md).

## Requirements

- [**uv**](https://docs.astral.sh/uv/) — the only prerequisite. It provides a compatible Python
  (≥3.10) and the locked dependencies on first run, then caches them. No global `pip install`.
- The engine [`pykeepass`](https://github.com/libkeepass/pykeepass) (**GPL-3.0**) is fetched at
  runtime and **never bundled** by this MIT-licensed project — see [`NOTICE`](NOTICE).

## Development

```bash
git clone https://github.com/yarrasys/kdbx-skill && cd kdbx-skill
uv run --with pytest --with pykeepass --with python-dotenv --with filelock --with platformdirs python -m pytest
uvx ruff check . && uvx ruff format --check .
uv run --locked kdbx.py --version
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md). The design spec and TDD
plan live under [`docs/superpowers/`](docs/superpowers).

## How it compares

- **vs. a `.env` file** — kdbx keeps values encrypted at rest and out of the repo, injects them
  without writing plaintext to disk, and gives you a reviewable contract instead of an
  untracked file that drifts.
- **vs. raw `keepassxc-cli`** — kdbx adds the per-project/per-env convention, the `vars` map,
  `run`/`export`/`import`/`check`, and agent-transcript safety on top. (`keepassxc-cli` remains a
  read-only fallback — see [`references/fallback.md`](references/fallback.md).)
- **vs. cloud secret managers** — no network, no telemetry, no account. Local files only;
  your laptop or CI runner is the trust boundary.

## Project status

Implemented; test suite green (46 tests) on macOS and Linux. Windows paths are designed and run in
CI (informational), but not yet promoted to a required check — Windows verification is tracked in
[issues](https://github.com/yarrasys/kdbx-skill/issues) and contributions are welcome. See
[`CHANGELOG.md`](CHANGELOG.md).

## License

[MIT](LICENSE) for this project's own source. The default engine `pykeepass` is GPL-3.0, fetched
at runtime and never redistributed here; if you plan to ship a closed-source product that bundles
the engine, read [`NOTICE`](NOTICE). *(Not legal advice.)*
