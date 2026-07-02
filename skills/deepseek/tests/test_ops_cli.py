import importlib
import json

ops = importlib.import_module("deepseek_core.ops")


def test_config_prints_effective(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert ops.dispatch(["config"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["model"] == "deepseek-v4-flash"


def test_init_creates_then_refuses_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert ops.dispatch(["init"]) == 0
    assert (tmp_path / ".deepseek.json").is_file()
    data = json.loads((tmp_path / ".deepseek.json").read_text())
    assert data["mode"] == "suggest"
    assert ops.dispatch(["init"]) == 4  # refuses to clobber


def test_check_reports_missing_key(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    rc = ops.dispatch(["check"])
    err = capsys.readouterr().err
    assert "DEEPSEEK_API_KEY" in err
    assert rc != 0
