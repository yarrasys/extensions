import importlib
import os

runner = importlib.import_module("deepseek_core.runner")


def test_run_child_parses_json(fake_claude, tmp_path):
    env = dict(os.environ)
    res = runner.run_child(
        ["claude", "-p", "x", "--output-format", "json"], env, tmp_path, timeout=30
    )
    assert res["ok"] is True
    assert res["result"]["num_turns"] == 2
    assert res["result"]["total_cost_usd"] == 0.0012


def test_run_child_nonzero_is_not_ok(fake_claude, tmp_path):
    env = dict(os.environ, FAKE_RC="1")
    res = runner.run_child(["claude", "-p", "x"], env, tmp_path, timeout=30)
    assert res["ok"] is False
    assert res["returncode"] == 1
    assert "boom" in res["stderr_tail"]


def test_run_child_actually_edits_file(fake_claude, tmp_path):
    target = tmp_path / "a.py"
    target.write_text("x = 1\n")
    env = dict(os.environ, FAKE_EDIT_FILE=str(target))
    runner.run_child(["claude", "-p", "x"], env, tmp_path, timeout=30)
    assert "edited by fake claude" in target.read_text()
