"""Build the child `claude` invocation and resolve the DeepSeek key."""

import json
import pathlib
import subprocess
from collections.abc import Mapping

ENDPOINT = "https://api.deepseek.com/anthropic"
DEPTH_ENV = "DEEPSEEK_DELEGATE_DEPTH"


def resolve_key(environ: Mapping):
    # v1: env only. kdbx resolution is wired in ops.cmd_delegate (subprocess) so this
    # stays pure and testable.
    return environ.get("DEEPSEEK_API_KEY") or None


def build_child_env(base_env: Mapping, key: str) -> dict:
    env = dict(base_env)
    env["ANTHROPIC_BASE_URL"] = ENDPOINT
    env["ANTHROPIC_AUTH_TOKEN"] = key
    env[DEPTH_ENV] = "1"
    return env


def build_argv(task: str, *, model: str, allowed_tools, settings_path: str, max_turns: int):
    return [
        "claude",
        "-p",
        task,
        "--output-format",
        "json",
        "--model",
        model,
        "--permission-mode",
        "acceptEdits",
        "--allowedTools",
        ",".join(allowed_tools),
        "--settings",
        settings_path,
        "--max-turns",
        str(max_turns),
    ]


def write_child_settings(dir_: pathlib.Path, model: str) -> pathlib.Path:
    settings = {
        "env": {DEPTH_ENV: "1"},
        "disabledSkills": ["deepseek"],
        "model": model,
    }
    p = dir_ / "deepseek-child-settings.json"
    p.write_text(json.dumps(settings, indent=2))
    return p


def run_child(argv, env, cwd, timeout: int) -> dict:
    try:
        proc = subprocess.run(
            argv,
            env=dict(env),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "result": None, "returncode": -1, "stderr_tail": "timeout"}
    stderr_tail = "\n".join(proc.stderr.strip().splitlines()[-5:])
    if proc.returncode != 0:
        return {
            "ok": False,
            "result": None,
            "returncode": proc.returncode,
            "stderr_tail": stderr_tail,
        }
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "result": None,
            "returncode": 0,
            "stderr_tail": "unparseable child output",
        }
    return {"ok": True, "result": result, "returncode": 0, "stderr_tail": stderr_tail}
