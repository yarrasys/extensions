import os
import pathlib
import subprocess
import sys

import pytest

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR))


@pytest.fixture
def git_repo(tmp_path):
    def run(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    run("init", "-q")
    run("config", "user.email", "t@t.t")
    run("config", "user.name", "t")
    (tmp_path / "a.py").write_text("x = 1\n")
    run("add", "-A")
    run("commit", "-qm", "init")
    return tmp_path


@pytest.fixture
def fake_claude(tmp_path, monkeypatch):
    """Put a fake `claude` on PATH. It writes canned JSON to stdout and, if asked,
    touches a file in cwd to simulate an edit. Controlled via env the test sets."""
    bin_dir = tmp_path / "fakebin"
    bin_dir.mkdir()
    script = bin_dir / "claude"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "edit = os.environ.get('FAKE_EDIT_FILE')\n"
        "if edit:\n"
        "    open(edit, 'a').write('# edited by fake claude\\n')\n"
        "rc = int(os.environ.get('FAKE_RC', '0'))\n"
        "if rc == 0:\n"
        "    print(json.dumps({'result': 'done', 'num_turns': 2, 'total_cost_usd': 0.0012}))\n"
        "else:\n"
        "    sys.stderr.write('boom\\n')\n"
        "sys.exit(rc)\n"
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return script
