"""上传前自检脚本测试。

覆盖平台审核最常见的三类驳回：
- 目录/压缩包里带 .git/index（二进制）
- 带 .env（密钥）
- 文本文件内容其实是二进制
"""
import sys
import zipfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import check_submission as cs

SKILL_OK = "---\nname: intersci-grad\ndescription: demo\n---\n\n# demo\n"


def _zip(tmp_path: Path, mapping):
    target = tmp_path / "bundle.zip"
    with zipfile.ZipFile(target, "w") as archive:
        for name, data in mapping.items():
            archive.writestr(name, data)
    return target


def _inspect(target: Path):
    entries, kind = cs._load_entries(target)
    return cs.inspect(entries, kind)


def test_clean_zip_passes(tmp_path):
    target = _zip(tmp_path, {
        "intersci-grad/SKILL.md": SKILL_OK,
        "intersci-grad/references/a.md": "中文内容\n",
    })
    errors, warnings, info = _inspect(target)
    assert errors == []
    assert warnings == []
    assert info["files"] == 2


def test_git_index_is_rejected(tmp_path):
    target = _zip(tmp_path, {
        "intersci-grad/SKILL.md": SKILL_OK,
        "intersci-grad/.git/index": b"\x00\x01\x02DIRC",
    })
    errors, _, _ = _inspect(target)
    assert any(".git/index" in error for error in errors)
    assert any("二进制" in error or "NUL" in error for error in errors)


def test_env_file_is_rejected(tmp_path):
    target = _zip(tmp_path, {
        "intersci-grad/SKILL.md": SKILL_OK,
        "intersci-grad/.env": "SCP_HUB_API_KEY=real-secret\n",
    })
    errors, _, _ = _inspect(target)
    assert any(".env" in error and "环境变量" in error for error in errors)


def test_binary_content_in_markdown_is_rejected(tmp_path):
    target = _zip(tmp_path, {
        "intersci-grad/SKILL.md": SKILL_OK,
        "intersci-grad/notes.md": b"\x00\x00binary",
    })
    errors, _, _ = _inspect(target)
    assert any("notes.md" in error and "NUL" in error for error in errors)


def test_invalid_utf8_is_rejected(tmp_path):
    target = _zip(tmp_path, {
        "intersci-grad/SKILL.md": SKILL_OK,
        "intersci-grad/notes.md": "中文".encode("gb18030"),
    })
    errors, _, _ = _inspect(target)
    assert any("notes.md" in error and "UTF-8" in error for error in errors)


def test_directory_name_must_match_frontmatter(tmp_path):
    target = _zip(tmp_path, {"wrong-name/SKILL.md": SKILL_OK})
    errors, _, _ = _inspect(target)
    assert any("目录名" in error and "不一致" in error for error in errors)


def test_missing_skill_md_is_rejected(tmp_path):
    target = _zip(tmp_path, {"intersci-grad/README.md": "# hi\n"})
    errors, _, _ = _inspect(target)
    assert any("找不到 SKILL.md" in error for error in errors)


def test_root_level_skill_md_warns_for_zip(tmp_path):
    target = _zip(tmp_path, {"SKILL.md": SKILL_OK})
    errors, warnings, _ = _inspect(target)
    assert errors == []
    assert any("根目录" in warning for warning in warnings)


def test_folder_mode_accepts_skill_dir(tmp_path):
    folder = tmp_path / "intersci-grad"
    (folder / "references").mkdir(parents=True)
    (folder / "SKILL.md").write_text(SKILL_OK, encoding="utf-8")
    (folder / "references" / "a.md").write_text("内容\n", encoding="utf-8")
    errors, warnings, _ = _inspect(folder)
    assert errors == []
    assert warnings == []
