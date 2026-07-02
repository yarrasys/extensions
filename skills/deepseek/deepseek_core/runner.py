"""Build the child `claude` invocation and resolve the DeepSeek key."""

import json
import pathlib
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
