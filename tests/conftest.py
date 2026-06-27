import pathlib
import sys

import pytest

# the skill package lives under skills/kdbx/ — put it on the path so `import kdbx_core` works
SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent / "skills" / "kdbx"
sys.path.insert(0, str(SKILL_DIR))


@pytest.fixture
def built_vault(tmp_path):
    from kdbx_core import vault

    vp, kf = tmp_path / "v.kdbx", tmp_path / "v.keyx"
    vault.create_vault(vp, kf)
    return vp, kf
