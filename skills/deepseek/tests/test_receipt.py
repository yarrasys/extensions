import importlib

r = importlib.import_module("deepseek_core.receipt")


def test_verify_result_none_when_no_cmd():
    assert r.verify_result(None, None) is None


def test_verify_result_pass():
    assert r.verify_result("ruff check x.py", 0) == {
        "cmd": "ruff check x.py",
        "exit": 0,
        "passed": True,
    }


def test_verify_result_fail_includes_tail():
    res = r.verify_result("pytest", 1, tail="E   assert 1 == 2")
    assert res["passed"] is False
    assert res["tail"] == "E   assert 1 == 2"


def test_build_receipt_omits_patch_when_none():
    rc = r.build_receipt(
        status="applied",
        workspace="in_place",
        files=[{"path": "x.py", "diffstat": "+1 -0"}],
        verify=None,
        patch=None,
        cost={"reported_usd": None, "note": "n/a"},
        turns=1,
    )
    assert "patch" not in rc
    assert rc["status"] == "applied"
    assert rc["files"][0]["path"] == "x.py"


def test_build_receipt_includes_patch():
    rc = r.build_receipt(
        status="patch_ready",
        workspace="worktree",
        files=[],
        verify={"cmd": "ruff", "exit": 0, "passed": True},
        patch=".deepseek/edit-abc.patch",
        cost={"reported_usd": 0.001, "note": "approx"},
        turns=2,
    )
    assert rc["patch"] == ".deepseek/edit-abc.patch"
