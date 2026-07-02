"""Pure shaping of the compact delegation receipt."""


def verify_result(cmd, exit_code, tail: str = ""):
    if cmd is None:
        return None
    passed = exit_code == 0
    res = {"cmd": cmd, "exit": exit_code, "passed": passed}
    if not passed and tail:
        res["tail"] = tail
    return res


def build_receipt(*, status, workspace, files, verify, patch, cost, turns) -> dict:
    rc = {
        "status": status,
        "workspace": workspace,
        "files": files,
        "verify": verify,
        "cost": cost,
        "turns": turns,
    }
    if patch is not None:
        rc["patch"] = patch
    return rc
