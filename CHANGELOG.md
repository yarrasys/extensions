# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-27

Initial release.

### Added

- Per-project, per-env credential management in key-file-only KeePassXC KDBX4 + Argon2 vaults.
- 12 operations: `init`, `set`, `get`, `list`, `delete`, `mv`, `run`, `export`, `import`,
  `check`, `envs`, `rekey`.
- `run -- <cmd>` injects mapped secrets into a child process without printing them;
  `export` materializes a 0600 dotenv only when a tool requires a file.
- Committed `.keepassxc.json` pointer with a git-reviewable `vars` map (env var → entry path).
- Single PEP-723 entry script run via `uv` (no global installs); pinned, locked dependencies.
- Engine-agnostic `vault.py` boundary (pykeepass today; permissive engine swappable later).
- Secret-safety: values never on argv/stdout, scrubbed errors, masked `get` by default,
  prod / inherited-`$KDBX_ENV` write gate.
- Ships as a Claude Code skill (`SKILL.md` + `references/`); 46-test suite.

[Unreleased]: https://github.com/yarrasys/kdbx-skill/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yarrasys/kdbx-skill/releases/tag/v0.1.0
