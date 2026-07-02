import importlib
import json

runner = importlib.import_module("deepseek_core.runner")


def test_build_child_env_sets_endpoint_and_key():
    env = runner.build_child_env({"PATH": "/usr/bin", "HOME": "/h"}, "sk-test")
    assert env["ANTHROPIC_BASE_URL"] == "https://api.deepseek.com/anthropic"
    assert env["ANTHROPIC_AUTH_TOKEN"] == "sk-test"
    assert env["DEEPSEEK_DELEGATE_DEPTH"] == "1"
    assert env["PATH"] == "/usr/bin"  # base preserved


def test_build_argv_shape():
    argv = runner.build_argv(
        "add docstrings",
        model="deepseek-v4-flash",
        allowed_tools=["Read", "Edit", "Write", "Bash"],
        settings_path="/tmp/s.json",
        max_turns=8,
    )
    assert argv[0] == "claude"
    assert "-p" in argv and "add docstrings" in argv
    assert "--output-format" in argv and "json" in argv
    assert "--model" in argv and "deepseek-v4-flash" in argv
    assert "--permission-mode" in argv and "acceptEdits" in argv
    assert "--allowedTools" in argv and "Read,Edit,Write,Bash" in argv
    assert "--settings" in argv and "/tmp/s.json" in argv
    assert "--max-turns" in argv and "8" in argv


def test_write_child_settings_disables_skill(tmp_path):
    p = runner.write_child_settings(tmp_path, "deepseek-v4-flash")
    data = json.loads(p.read_text())
    assert (
        "deepseek" in data.get("disabledSkills", [])
        or data["env"]["DEEPSEEK_DELEGATE_DEPTH"] == "1"
    )


def test_resolve_key_from_env():
    assert runner.resolve_key({"DEEPSEEK_API_KEY": "sk-x"}) == "sk-x"
    assert runner.resolve_key({}) is None
