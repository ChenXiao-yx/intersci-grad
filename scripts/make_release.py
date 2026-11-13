#!/usr/bin/env python3
"""Build a shareable release bundle for the grad skill.

- Collects only runtime files (SKILL.md, references, scripts, examples, docs).
- Excludes .env, tests, docs, caches and other development-only files.
- Scans for hardcoded credentials and refuses to build on a hit.
- Rejects binary / non-UTF-8 payloads, so the bundle passes text-only review.
- Writes dist/intersci-grad-v<version>.zip plus dist/SHA256SUMS.txt.
  The zip's single top-level directory is `intersci-grad/` (must equal the
  frontmatter `name`, otherwise DSH cannot discover the skill after unzip).

Usage:
    python scripts/make_release.py --check-only   # CI: validate, write nothing
    python scripts/make_release.py                # build dist/intersci-grad-v5.0.0.zip
    python scripts/make_release.py --out release  # custom output directory

Exit codes: 0 = ok, 1 = check/build failed, 2 = usage error.
"""
import argparse
import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

__version__ = "1.0.0"

VERSION_RE = re.compile(r'^version:\s*["\']?([\d.]+)', re.MULTILINE)
PYPROJECT_VERSION_RE = re.compile(r'^version\s*=\s*["\']([\d.]+)["\']', re.MULTILINE)
SKILL_NAME_RE = re.compile(r"^name:\s*([a-z0-9][a-z0-9-]*)", re.MULTILINE)

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "references/grad-playbook.md",
    "references/artifact-templates.md",
    "references/evidence-and-integrity.md",
    "scripts/validate_grad.py",
    "examples/grad/topic_memo.md",
]

ROOT_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "DISTRIBUTION.md",
    "SECURITY.md",
    "RELEASE_NOTES.md",
    "EXECUTION_CHECKLIST.md",
    "CONTRIBUTING.md",
    "MANIFEST.in",
    "pyproject.toml",
    ".env.example",
]

INCLUDE_DIRS = ["references", "scripts", "examples"]

# 发布包内唯一的顶层目录名，必须与 SKILL.md frontmatter 的 name 一致。
BUNDLE_DIR = "intersci-grad"

EXCLUDE_DIRS = {
    ".git", ".pytest_cache", "__pycache__", "tests", "docs", "dist",
    ".venv", "venv", ".idea", ".vscode", "delivery", "acl-recovery",
    ".github",
}
EXCLUDE_FILES = {".env", ".credentials.yaml"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}

# 只扫描文本文件，避免把二进制误报。
TEXT_SUFFIXES = {
    ".md", ".py", ".json", ".txt", ".toml", ".in", ".yml", ".yaml",
    ".example", ".cff", ".cfg",
}

SECRET_PATTERNS = [
    ("openai_like_key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    (
        "assigned_api_key",
        re.compile(
            r"(?:SCP_HUB_API_KEY|INTERNLM_API_KEY|COMPETITION_API_KEY|OPENAI_API_KEY)"
            r"[ \t]*=[ \t]*['\"]?[A-Za-z0-9_\-]{16,}"
        ),
    ),
    ("bearer_token", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}")),
]


def _parse_version(text: str) -> Optional[str]:
    match = VERSION_RE.search(text)
    return match.group(1) if match else None


def _collect_files(root: Path) -> List[Path]:
    files = []
    for name in ROOT_FILES:
        path = root / name
        if path.is_file():
            files.append(path)
    for dirname in INCLUDE_DIRS:
        base = root / dirname
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(root)
            if any(part in EXCLUDE_DIRS for part in rel.parts):
                continue
            if path.name in EXCLUDE_FILES:
                continue
            if path.suffix.lower() in EXCLUDE_SUFFIXES:
                continue
            files.append(path)
    return sorted(set(files))


def _scan_secrets(root: Path, files: List[Path]) -> List[Tuple[str, str, int]]:
    findings = []
    for path in files:
        if path.name in EXCLUDE_FILES:
            findings.append(("forbidden_file", str(path.relative_to(root)), 0))
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".env.example":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for name, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append((name, str(path.relative_to(root)), line))
    return findings


def _check_required(root: Path) -> List[str]:
    return [name for name in REQUIRED_FILES if not (root / name).is_file()]


def _check_versions(root: Path, skill_text: str) -> List[str]:
    issues = []
    skill_version = _parse_version(skill_text)
    pyproject = root / "pyproject.toml"
    pyproject_version = None
    if pyproject.is_file():
        match = PYPROJECT_VERSION_RE.search(pyproject.read_text(encoding="utf-8"))
        pyproject_version = match.group(1) if match else None
    if skill_version is None:
        issues.append("SKILL.md frontmatter 缺少 version")
    if pyproject_version is None:
        issues.append("pyproject.toml 缺少 version")
    if skill_version and pyproject_version and skill_version != pyproject_version:
        issues.append(
            "版本不一致: SKILL.md=%s, pyproject.toml=%s" % (skill_version, pyproject_version)
        )
    name_match = SKILL_NAME_RE.search(skill_text)
    if not name_match:
        issues.append("SKILL.md frontmatter 缺少合法 name")
    elif name_match.group(1) != "intersci-grad":
        issues.append("skill name 应为 intersci-grad，实际为 %s" % name_match.group(1))
    return issues


def _check_text(root: Path, files: List[Path]) -> List[str]:
    """确认每个待发布文件都是真实 UTF-8 文本。

    平台侧会按“内容与后缀是否相符”审核：带 NUL 的文件、或无法按 UTF-8
    解码的文件会被判成“二进制 / 压缩包伪装成文本”。这里提前拦住，
    避免打包成功、上传后才被驳回。
    """
    issues = []
    for path in files:
        data = path.read_bytes()
        if b"\x00" in data:
            issues.append("二进制文件（含 NUL 字节）: %s" % path.relative_to(root))
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            issues.append(
                "非 UTF-8 文本: %s（第 %d 字节）" % (path.relative_to(root), exc.start)
            )
    return issues


def _report(check_only: bool, version: str, files: List[Path], findings: List[Tuple[str, str, int]]) -> int:
    print("Release check: intersci-grad v%s" % version)
    print("  runtime files: %d" % len(files))
    if findings:
        print("  secret findings: %d" % len(findings))
        for kind, path, line in findings[:20]:
            print("    - %s in %s:%s" % (kind, path, line))
        return 1
    print("  secret findings: 0")
    print("  text check: all %d files are valid UTF-8 (no NUL bytes)" % len(files))
    if check_only:
        print("OK: bundle is clean (no files written)")
    return 0


def _build(root: Path, out_dir: Path, version: str, files: List[Path]) -> Tuple[Path, str]:
    build_dir = out_dir / BUNDLE_DIR
    if build_dir.exists():
        shutil.rmtree(build_dir)
    for src in files:
        rel = src.relative_to(root)
        dst = build_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    leaked = [path for path in build_dir.rglob(".env") if path.is_file()]
    if leaked:
        raise RuntimeError(".env leaked into release bundle: %s" % leaked[0])
    leaked_git = [path for path in build_dir.rglob(".git") if path.is_dir()]
    if leaked_git:
        raise RuntimeError(".git leaked into release bundle: %s" % leaked_git[0])

    zip_path = out_dir / ("intersci-grad-v%s.zip" % version)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(build_dir.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=str(Path(BUNDLE_DIR) / path.relative_to(build_dir)))

    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    sums_path = out_dir / "SHA256SUMS.txt"
    sums_path.write_text("%s  %s\n" % (digest, zip_path.name), encoding="utf-8")
    return zip_path, digest


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build a shareable grad-skill release zip.")
    parser.add_argument("--check-only", action="store_true", help="只检查，不写文件（CI 用）")
    parser.add_argument("--out", default="dist", help="输出目录（默认 dist/）")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent.parent
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        print("ERROR: 找不到 SKILL.md：%s" % skill_path, file=sys.stderr)
        return 1

    skill_text = skill_path.read_text(encoding="utf-8")
    version = _parse_version(skill_text)
    if not version:
        print("ERROR: SKILL.md 缺少 version", file=sys.stderr)
        return 1

    issues = []
    missing = _check_required(root)
    if missing:
        issues.append("缺少必需文件: %s" % ", ".join(missing))
    issues.extend(_check_versions(root, skill_text))

    files = _collect_files(root)
    findings = _scan_secrets(root, files)
    issues.extend(_check_text(root, files))
    if issues:
        for issue in issues:
            print("ERROR: %s" % issue, file=sys.stderr)
        return 1
    if _report(args.check_only, version, files, findings) != 0:
        return 1
    if args.check_only:
        return 0

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path, digest = _build(root, out_dir, version, files)
    print("Built: %s" % zip_path)
    print("  size: %.1f KB" % (zip_path.stat().st_size / 1024.0))
    print("  sha256: %s" % digest)
    print("  sums: %s" % (out_dir / "SHA256SUMS.txt"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
