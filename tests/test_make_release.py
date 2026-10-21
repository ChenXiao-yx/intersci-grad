"""make_release 发布包脚本测试。

覆盖：
- --check-only 在干净仓库上返回 0 且不写文件
- 版本号与 pyproject 一致
- 必需运行文件齐全
- 收集清单排除 .env / tests / docs / 缓存
- 密钥扫描 0 命中
"""
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import make_release as mr

_ROOT = Path(__file__).resolve().parent.parent


def test_check_only_passes():
    assert mr.main(["--check-only"]) == 0


def test_version_matches_pyproject():
    skill_text = (_ROOT / "SKILL.md").read_text(encoding="utf-8")
    pyproject = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert mr._parse_version(skill_text) == "5.0.0"
    assert '"5.0.0"' in pyproject


def test_required_files_exist():
    assert mr._check_required(_ROOT) == []


def test_collect_excludes_development_files():
    files = mr._collect_files(_ROOT)
    names = {path.name for path in files}
    assert "SKILL.md" in names
    assert "validate_grad.py" in names
    assert ".env" not in names
    assert not any("__pycache__" in path.parts for path in files)
    assert not any("tests" in path.parts for path in files)
    assert not any("docs" in path.parts for path in files)


def test_secret_scan_is_clean():
    files = mr._collect_files(_ROOT)
    assert mr._scan_secrets(_ROOT, files) == []
