# Contributing to kdbx-skill

Thanks for your interest! Contributions — bug reports, fixes, docs, and especially
**Windows verification** — are welcome.

## Ground rules

- **Never commit a real secret.** No vaults (`*.kdbx`), key files (`*.keyx`), or `.env` files;
  these are gitignored. Tests use throwaway vaults in temp dirs.
- Be kind. See the [Code of Conduct](CODE_OF_CONDUCT.md).

## Development setup

Requires [uv](https://docs.astral.sh/uv/) (the only prerequisite — it provides Python + deps).

```bash
git clone https://github.com/yarrasys/skills
cd skills

# run the test suite
uv run --with pytest --with pykeepass --with python-dotenv --with filelock --with platformdirs python -m pytest

# lint + format
uvx ruff check .
uvx ruff format .

# smoke the locked entrypoint
uv run --locked skills/kdbx/kdbx.py --version
```

## Pull requests

1. Open an [issue](https://github.com/yarrasys/skills/issues) first for anything non-trivial.
2. Work **test-first (TDD)** — add a failing test, then the minimal code to pass it. Keep the suite green.
3. Run `ruff check` / `ruff format` before pushing. CI runs tests on Linux/macOS/Windows + lint.
4. If you change the dependencies declared in `kdbx.py`, run `uv lock --script skills/kdbx/kdbx.py` and commit `kdbx.py.lock`.
5. Keep `skills/kdbx/kdbx_core/vault.py` the **only** module importing `pykeepass`, with an engine-agnostic interface.
6. Update `CHANGELOG.md` under `## [Unreleased]`.

## Security

Do not open public issues for vulnerabilities — see [SECURITY.md](SECURITY.md).
