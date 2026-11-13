#!/usr/bin/env python3
"""上传前自检：准备提交的包（zip 或目录）能不能通过 skill 平台的文本审核。

平台常见驳回理由：

    「文件内容与后缀不符（疑似二进制或压缩包伪装成文本）」

最常见的原因是**把整个工作目录直接打包上传**，于是带进了：

    .git/index          # git 索引，二进制
    .env                # 本机密钥，绝不能上传
    __pycache__/*.pyc   # Python 字节码，二进制
    dist/*.zip          # 上一次的压缩包，套娃

本脚本按平台审核的口径逐文件检查：

1. 禁止项：.git/、.env、缓存目录、字节码、内嵌压缩包与可执行文件。
2. 文本性：不能含 NUL 字节，必须能按 UTF-8 严格解码。
3. 结构：SKILL.md 在包根目录或唯一顶层目录内；目录名与 frontmatter
   的 name 一致（DSH 按 `<root>/<name>/SKILL.md` 发现技能）。

用法：

    python scripts/check_submission.py dist/intersci-grad-v5.0.0.zip
    python scripts/check_submission.py dist/intersci-grad
    python scripts/check_submission.py dist/intersci-grad-v5.0.0.zip --json

退出码：0 = 可以上传，1 = 有问题（已列出文件与原因），2 = 用法错误。
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Dict, List, Tuple

FORBIDDEN_DIRS = {
    ".git", ".hg", ".svn",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox",
    ".idea", ".vscode", ".venv", "venv", "node_modules", "__MACOSX",
}
FORBIDDEN_SUFFIXES = {
    ".pyc", ".pyo", ".pyd", ".class", ".jar",
    ".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".bz2", ".xz",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".a",
    ".pkl", ".npy", ".npz", ".h5", ".pt", ".pth", ".onnx",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
}
ENV_NAMES = {".env", ".env.local", ".env.production", ".env.development", ".env.test"}


def _normalize(name: str) -> str:
    name = name.replace("\\", "/").lstrip("/")
    while name.startswith("./"):
        name = name[2:]
    return name


def _load_entries(target: Path) -> Tuple[List[Tuple[str, bytes]], str]:
    if target.is_dir():
        entries = []
        for path in sorted(target.rglob("*")):
            if path.is_file():
                entries.append((_normalize(path.relative_to(target).as_posix()),
                                path.read_bytes()))
        return entries, "dir"
    if target.is_file() and zipfile.is_zipfile(target):
        with zipfile.ZipFile(target) as archive:
            entries = [
                (_normalize(item.filename), archive.read(item))
                for item in archive.infolist()
                if not item.is_dir()
            ]
        return entries, "zip"
    raise ValueError("既不是目录，也不是 zip：%s" % target)


def _check_path(name: str) -> List[str]:
    """只看路径就能确定的问题。"""
    problems = []
    parts = PurePosixPath(name).parts
    for part in parts:
        if part in FORBIDDEN_DIRS:
            problems.append("禁止上传的目录内容（%s）" % part)
            break
    base = parts[-1] if parts else name
    if base in ENV_NAMES:
        problems.append("禁止上传的环境变量文件（可能含真实密钥）")
    suffix = PurePosixPath(name).suffix.lower()
    if suffix in FORBIDDEN_SUFFIXES:
        problems.append("二进制或压缩包（%s）" % suffix)
    return problems


def _check_text(data: bytes) -> List[str]:
    """返回内容层面的问题列表。"""
    if b"\x00" in data:
        offset = data.index(b"\x00")
        return ["内容与后缀不符：含 NUL 字节（偏移 %d），会被判为二进制" % offset]
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return ["内容与后缀不符：不是合法 UTF-8（第 %d 字节起无法解码）" % exc.start]
    return []


def _parse_frontmatter(text: str) -> Dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    result = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip().strip("\"'")
    return result


def inspect(entries: List[Tuple[str, bytes]], kind: str = "dir") -> Tuple[List[str], List[str], Dict[str, object]]:
    errors: List[str] = []
    warnings: List[str] = []
    names = [name for name, _ in entries]

    for name, data in entries:
        for reason in _check_path(name):
            errors.append("%s: %s" % (name, reason))
        for reason in _check_text(data):
            errors.append("%s: %s" % (name, reason))

    duplicates = sorted({name for name in names if names.count(name) > 1})
    for name in duplicates:
        errors.append("%s: 包内重复出现" % name)

    layout = ""
    if "SKILL.md" in names:
        layout = "根目录"
        skill_name = "SKILL.md"
    else:
        tops = {PurePosixPath(name).parts[0] for name in names if len(PurePosixPath(name).parts) > 1}
        candidates = [top for top in tops if top + "/SKILL.md" in names]
        if len(candidates) == 1:
            layout = "唯一顶层目录 %s/" % candidates[0]
            skill_name = candidates[0] + "/SKILL.md"
        else:
            errors.append("找不到 SKILL.md：应在包根目录，或唯一顶层目录 <name>/SKILL.md")
            skill_name = ""

    expected_dir = None
    if layout == "根目录" and kind == "zip":
        warnings.append(
            "SKILL.md 在压缩包根目录；DSH 要求 <root>/<name>/SKILL.md，"
            "上传平台后请确认会解压成 intersci-grad/ 目录"
        )
    elif layout.startswith("唯一顶层目录"):
        expected_dir = PurePosixPath(layout.split()[1].rstrip("/")).name

    if skill_name:
        raw = dict(entries).get(skill_name, b"")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = ""
        meta = _parse_frontmatter(text)
        name = meta.get("name", "")
        if not name:
            errors.append("%s: frontmatter 缺少 name" % skill_name)
        else:
            if expected_dir and name != expected_dir:
                errors.append(
                    "%s: 目录名 %s 与 frontmatter name=%s 不一致"
                    % (skill_name, expected_dir, name)
                )
            if not all(ch.islower() or ch.isdigit() or ch == "-" for ch in name):
                warnings.append("frontmatter name 建议用 kebab-case：%s" % name)

    info = {
        "files": len(entries),
        "bytes": sum(len(data) for _, data in entries),
        "layout": layout or "未知",
    }
    return errors, warnings, info


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="检查准备上传的 skill 包是否为纯文本、无 .git/.env。")
    parser.add_argument("target", help="zip 文件或待上传目录")
    parser.add_argument("--json", action="store_true", help="输出机器可读结果")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists():
        print("ERROR: 路径不存在：%s" % target, file=sys.stderr)
        return 2
    try:
        entries, kind = _load_entries(target)
    except ValueError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2

    errors, warnings, info = inspect(entries, kind)
    size_kb = info["bytes"] / 1024.0

    if args.json:
        print(json.dumps({
            "target": str(target),
            "kind": kind,
            "files": info["files"],
            "bytes": info["bytes"],
            "layout": info["layout"],
            "errors": errors,
            "warnings": warnings,
            "passed": not errors,
        }, ensure_ascii=False, indent=2))
        return 0 if not errors else 1

    print("Submission check: %s (%s)" % (target, kind))
    print("  files: %d, size: %.1f KB" % (info["files"], size_kb))
    print("  layout: %s" % info["layout"])
    for warning in warnings:
        print("  WARN: %s" % warning)

    if errors:
        print("FAIL: 发现 %d 个问题，修好后再上传：" % len(errors))
        for error in errors[:50]:
            print("  - %s" % error)
        if len(errors) > 50:
            print("  ... 其余 %d 条省略" % (len(errors) - 50))
        return 1

    print("PASS: 不含 .git/.env/缓存/二进制，全部文件均为 UTF-8 文本，可以上传。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
