# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""deepseek — delegate simple dev tasks to a nested claude on DeepSeek. See SKILL.md."""

import os
import shutil
import sys

os.umask(0o077)


def _preflight() -> None:
    if sys.version_info < (3, 10):
        sys.stderr.write("deepseek: requires Python >=3.10 (run via `uv run`)\n")
        raise SystemExit(7)
    if shutil.which("git") is None:
        sys.stderr.write("deepseek: git not on PATH\n")
        raise SystemExit(7)


def main(argv=None) -> int:
    _preflight()
    from deepseek_core.ops import dispatch

    return dispatch(argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
