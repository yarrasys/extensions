import importlib

g = importlib.import_module("deepseek_core.guardrails")


def test_is_recursive():
    assert g.is_recursive({"DEEPSEEK_DELEGATE_DEPTH": "1"}) is True
    assert g.is_recursive({}) is False


def test_denied_paths_matches_recursive_globs():
    changed = ["src/app.py", ".github/workflows/ci.yml", "infra/main.tf", "docs/x.md"]
    deny = [".github/**", "infra/**", "**/*secret*"]
    assert g.denied_paths(changed, deny) == [".github/workflows/ci.yml", "infra/main.tf"]


def test_denied_paths_matches_secret_substring_glob():
    assert g.denied_paths(["config/my_secret.json"], ["**/*secret*"]) == ["config/my_secret.json"]


def test_denied_paths_empty_when_clean():
    assert g.denied_paths(["src/app.py"], [".github/**"]) == []


def test_within_budget():
    assert g.within_budget(0.10, 0.25) is True
    assert g.within_budget(0.30, 0.25) is False
    assert g.within_budget(None, 0.25) is True  # unknown cost never blocks
