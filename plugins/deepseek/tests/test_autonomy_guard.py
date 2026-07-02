"""Tests for the deepseek plugin autonomy-guard (plugins/deepseek/hooks/guard.py).

The guard turns the skill's *soft* `mode` contract into a hard PreToolUse gate:
  - auto mode: `--in-place` is refused (auto forces worktree isolation);
  - explicit mode: agent-initiated `delegate` is refused unless it carries the
    sanctioned sentinel supplied by /deepseek:delegate;
  - recursion: `delegate` is refused when already inside a delegation.
Everything else — including all non-`delegate` ops and `suggest` mode — passes.
The guard is stdlib-only and fails OPEN.
"""

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

_GUARD = pathlib.Path(__file__).resolve().parents[1] / "hooks" / "guard.py"

_spec = importlib.util.spec_from_file_location("deepseek_guard", _GUARD)
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)

_DELEGATE = "uv run --locked skills/deepseek/deepseek.py delegate --task 'add docstrings'"


# --- allow: not a delegate call at all -------------------------------------
ALLOW_NON_DELEGATE = [
    "cat README.md",
    "npm run dev",
    "",
    "grep TODO src/app.py",
    "uv run --locked skills/deepseek/deepseek.py check",
    "uv run --locked skills/deepseek/deepseek.py config",
    "uv run --locked skills/deepseek/deepseek.py apply .deepseek/edit-8f3a.patch",
    "uv run --locked skills/deepseek/deepseek.py init",
    "echo deepseek delegate is a thing",  # not an invocation -> not flagged
]


@pytest.mark.parametrize("cmd", ALLOW_NON_DELEGATE)
@pytest.mark.parametrize("mode", ["explicit", "suggest", "auto"])
def test_allows_non_delegate(cmd, mode):
    assert guard.decide(cmd, mode=mode, environ={}) is None, f"expected allow: {cmd!r} @ {mode}"


# --- suggest (default): delegate is never blocked by the guard --------------
def test_suggest_allows_delegate():
    assert guard.decide(_DELEGATE, mode="suggest", environ={}) is None
    assert guard.decide(_DELEGATE + " --in-place", mode="suggest", environ={}) is None


# --- auto mode: --in-place is refused, isolation stays mandatory ------------
def test_auto_allows_isolated_delegate():
    assert guard.decide(_DELEGATE, mode="auto", environ={}) is None


@pytest.mark.parametrize(
    "cmd",
    [
        _DELEGATE + " --in-place",
        "uv run --locked skills/deepseek/deepseek.py delegate --in-place --task x",
    ],
)
def test_auto_denies_in_place(cmd):
    reason = guard.decide(cmd, mode="auto", environ={})
    assert reason and "isolation" in reason.lower(), f"expected auto-isolation deny: {cmd!r}"


# --- explicit mode: agent-initiated delegate refused without the sentinel ---
def test_explicit_denies_unsanctioned_delegate():
    reason = guard.decide(_DELEGATE, mode="explicit", environ={})
    assert reason and "explicit" in reason.lower()


def test_explicit_allows_inline_sentinel():
    cmd = "DEEPSEEK_DELEGATE_APPROVED=1 " + _DELEGATE
    assert guard.decide(cmd, mode="explicit", environ={}) is None


def test_explicit_allows_env_sentinel():
    env = {"DEEPSEEK_DELEGATE_APPROVED": "1"}
    assert guard.decide(_DELEGATE, mode="explicit", environ=env) is None


# --- recursion: delegate refused when already delegating (any mode) ---------
@pytest.mark.parametrize("mode", ["explicit", "suggest", "auto"])
def test_recursion_denies_delegate(mode):
    env = {"DEEPSEEK_DELEGATE_DEPTH": "1", "DEEPSEEK_DELEGATE_APPROVED": "1"}
    reason = guard.decide(_DELEGATE, mode=mode, environ=env)
    assert reason and "recurs" in reason.lower(), f"expected recursion deny @ {mode}"


# --- config discovery: read_mode walks up, defaults + fails open to suggest -
def test_read_mode_reads_nearest(tmp_path):
    (tmp_path / ".deepseek.json").write_text(json.dumps({"mode": "explicit"}))
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    assert guard.read_mode(sub) == "explicit"


def test_read_mode_defaults_suggest_when_absent(tmp_path):
    assert guard.read_mode(tmp_path) == "suggest"


def test_read_mode_fails_open_on_garbage(tmp_path):
    (tmp_path / ".deepseek.json").write_text("{ not json")
    assert guard.read_mode(tmp_path) == "suggest"


def test_read_mode_rejects_unknown_mode(tmp_path):
    (tmp_path / ".deepseek.json").write_text(json.dumps({"mode": "yolo"}))
    assert guard.read_mode(tmp_path) == "suggest"


# --- subprocess decision contract ------------------------------------------
def _run(payload):
    return subprocess.run(
        [sys.executable, str(_GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def test_subprocess_deny_contract(tmp_path):
    (tmp_path / ".deepseek.json").write_text(json.dumps({"mode": "explicit"}))
    p = _run({"cwd": str(tmp_path), "tool_input": {"command": _DELEGATE}})
    assert p.returncode == 0
    hso = json.loads(p.stdout)["hookSpecificOutput"]
    assert hso["hookEventName"] == "PreToolUse"
    assert hso["permissionDecision"] == "deny"
    assert "explicit" in hso["permissionDecisionReason"].lower()


def test_subprocess_allow_is_silent(tmp_path):
    p = _run({"cwd": str(tmp_path), "tool_input": {"command": "cat README.md"}})
    assert p.returncode == 0
    assert p.stdout.strip() == ""


def test_subprocess_malformed_json_fails_open():
    p = _run_raw("not json at all {")
    assert p.returncode == 0
    assert p.stdout.strip() == ""


def _run_raw(stdin_text):
    return subprocess.run(
        [sys.executable, str(_GUARD)],
        input=stdin_text,
        capture_output=True,
        text=True,
    )
