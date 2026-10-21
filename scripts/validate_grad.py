#!/usr/bin/env python3
"""研究生产物轻校验器（grad profile）。

与旧版 validate_output.py 的十章尽调校验完全独立：本脚本只校验研究生场景
产物的通用契约，纯标准库、无需联网、不依赖任何配置文件。

十条检查
--------
1. 首屏一句话判断（硬）
2. 下一步三档动作（硬；周报类型改查三行结构）
3. 依据标签【文献/经验/推测】（警告）
4. 引用格式可解析（硬失败：占位 DOI；警告：正文无引用）
5. 绝对化/过度承诺（硬）
6. 内部黑话泄漏（硬）
7. 末尾说明（硬）
8. 代写/造假表述（硬）
9. 未清理占位符（硬）
10. 下一步是否具体可执行（警告）

退出码：0=通过（允许警告）；1=存在硬失败；2=参数/文件错误。

用法：
    python scripts/validate_grad.py --input examples/grad/topic_memo.md --type memo
    python scripts/validate_grad.py --input draft.md --type proposal --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

__version__ = "1.0.0"

ARTIFACT_TYPES = [
    "memo", "proposal", "matrix", "reading", "experiment",
    "meeting", "weekly", "venue", "rebuttal",
]

# 需要引用的产物类型：正文里没有引用时给警告（不阻断）
CITATION_EXPECTED = {"memo", "proposal", "matrix", "reading"}
# 至少需要 1 个依据标签的类型
LABEL_MINIMUM = {
    "memo": 2, "proposal": 2, "matrix": 2, "reading": 2, "experiment": 2,
    "meeting": 1, "venue": 1, "rebuttal": 1, "weekly": 0,
}

RE_ANSWER_FIRST = re.compile(r"\*\*一句话判断[：:]?\*\*")
RE_NEXT_HEADING = re.compile(r"^#{2,3}\s*下一步\s*$", re.MULTILINE)
RE_SECTION_END = re.compile(r"^#{1,3}\s+", re.MULTILINE)
RE_DOI_URL = re.compile(r"https?://(?:dx\.)?doi\.org/(\S+)")
RE_ARXIV_URL = re.compile(r"https?://arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})")
RE_BARE_FAKE_DOI = re.compile(r"10\.[xX]{3,}|doi:\s*10\.[xX]{3,}", re.IGNORECASE)

LABELS = ("【文献】", "【经验】", "【推测】")

HARD_OVERCLAIM = [
    r"保证(?:能|可)?(?:发表|中|过|录用)",
    r"一定能(?:发表|中|过|成)",
    r"必然(?:成功|有效|成立)",
    r"100\s*%",
    r"绝对(?:可靠|有效|正确|没问题)",
    r"毫无疑问",
    r"稳(?:过|中|发)",
    r"包(?:发|中|过)",
    r"以下是完整论文",
]
SOFT_OVERCLAIM = [
    r"国际领先",
    r"填补(?:了)?空白",
    r"尚属首次",
    r"没有人做过",
    r"无人研究",
]

JARGON = [
    r"SKILL\.md", r"validate_output\.py", r"validate_grad\.py",
    r"score_evidence", r"search_papers", r"scp_tools",
    r"evidence-rubric", r"output-template", r"plain-language-map",
    r"§\s*\d", r"\bL[0-3]\s*(?:卡片|档|层)\b", r"mock_fallback",
    r"rule2_triggered", r"valid_evidence_count", r"三选一",
    r"闸口", r"知识蒸馏", r"base_weight", r"decay_factor",
]

GHOSTWRITING = [
    r"(?<!不)代写", r"(?<!不)直接提交(?:即可)?", r"(?<!不)可直接发表",
    r"替你写", r"一键生成论文", r"保证录用",
]

PLACEHOLDERS = [
    r"TODO", r"FIXME", r"XXXX", r"待填", r"此处填写",
    r"\{\{", r"\}\}", r"\[占位\]", r"<占位>",
]

ACTION_VERBS = [
    "读", "写", "跑", "做", "找", "问", "发", "画", "列", "改",
    "测", "建", "复现", "整理", "预约", "提交", "确认", "记录",
    "补", "查", "算", "标", "拆", "填", "核",
]

DISCLAIMER_KEYS = ("自行核验", "不替代", "AI 辅助", "仅供参考", "AI辅助")


def _status(num, name, status, detail):
    return {"num": num, "name": name, "status": status, "detail": detail}


def _first_lines(text, count=25):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[:count]


def _next_section(text):
    """返回「## 下一步」到下一个二级标题之间的内容；没有则空串。"""
    m = RE_NEXT_HEADING.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    end = RE_SECTION_END.search(rest)
    return rest[: end.start()] if end else rest


def check_answer_first(text, artifact_type):
    head = "\n".join(_first_lines(text, 25))
    if RE_ANSWER_FIRST.search(head):
        return True, "首屏含「一句话判断」"
    return False, "前 25 行未找到「**一句话判断**」，读者无法在 10 秒内知道结论"


def check_next_actions(text, artifact_type):
    if artifact_type == "weekly":
        need = ["本周", "卡点", "下周"]
        missing = [k for k in need if k not in text]
        if missing:
            return False, "周报缺少：%s" % "、".join(missing)
        return True, "周报三行结构完整"

    section = _next_section(text)
    if not section:
        return False, "缺少「## 下一步」小节"
    marks = [k for k in ("今天", "本周", "两周", "明天", "48 小时") if k in section]
    if len(marks) < 2:
        return False, "下一步只有 %d 个时间档（至少 2 个：今天/本周/两周）" % len(marks)
    return True, "下一步含时间档：%s" % "、".join(marks)


def check_labels(text, artifact_type):
    minimum = LABEL_MINIMUM.get(artifact_type, 1)
    if minimum == 0:
        return None, "该类型不要求依据标签"
    found = {lb: text.count(lb) for lb in LABELS}
    total = sum(found.values())
    if total >= minimum:
        return True, "依据标签 %d 处（%s）" % (
            total,
            "，".join("%s%d" % (k, v) for k, v in found.items() if v),
        )
    return None, "依据标签仅 %d 处，建议至少 %d 处（【文献】/【经验】/【推测】）" % (
        total,
        minimum,
    )


def _extract_next_bullets(section):
    bullets = []
    for ln in section.splitlines():
        s = ln.strip()
        if s.startswith(("-", "*", "•")):
            bullets.append(s.lstrip("-*• ").strip())
    return bullets


def check_citations(text, artifact_type):
    errors = []
    for target in RE_DOI_URL.findall(text):
        if not re.match(r"10\.\d{4,9}/\S+", target):
            errors.append("DOI 链接格式可疑：%s" % target[:60])
        if re.search(r"10\.(?:x{3,}|X{3,})", target):
            errors.append("占位 DOI：%s" % target[:60])
    if RE_BARE_FAKE_DOI.search(text):
        errors.append("正文出现占位 DOI（10.xxx）")
    if errors:
        return False, "；".join(errors)
    has_citation = bool(RE_DOI_URL.search(text) or RE_ARXIV_URL.search(text))
    if not has_citation and artifact_type in CITATION_EXPECTED:
        return None, "正文没有可点开的 DOI/arXiv 链接；如为经验型备忘可忽略，否则请补出处"
    return True, "引用格式正常" if has_citation else "无需引用的类型"


def check_overclaim(text, artifact_type):
    hits = []
    for pat in HARD_OVERCLAIM:
        hits.extend(re.findall(pat, text))
    if hits:
        return False, "出现不可承诺的表述：%s" % "、".join(sorted(set(hits))[:6])
    soft = []
    for pat in SOFT_OVERCLAIM:
        soft.extend(re.findall(pat, text))
    if soft:
        return None, "出现需核验的强断言：%s（请确认已检索/有出处）" % "、".join(
            sorted(set(soft))[:6]
        )
    return True, "未发现绝对化承诺"


def check_jargon(text, artifact_type):
    hits = []
    for pat in JARGON:
        hits.extend(re.findall(pat, text))
    if hits:
        return False, "输出泄漏内部术语：%s" % "、".join(sorted(set(hits))[:8])
    return True, "未发现内部黑话"


def check_disclaimer(text, artifact_type):
    tail = "\n".join([ln for ln in text.splitlines() if ln.strip()][-8:])
    found = sum(1 for k in DISCLAIMER_KEYS if k in tail)
    if found >= 2:
        return True, "末尾说明完整"
    return False, "末尾 8 行缺少「AI 辅助 / 自行核验 / 不替代」说明"


def check_ghostwriting(text, artifact_type):
    hits = []
    for pat in GHOSTWRITING:
        hits.extend(re.findall(pat, text))
    if hits:
        return False, "出现代写/造假类表述：%s" % "、".join(sorted(set(hits))[:6])
    return True, "未发现代写表述"


def check_placeholders(text, artifact_type):
    hits = []
    for pat in PLACEHOLDERS:
        hits.extend(re.findall(pat, text))
    if hits:
        return False, "仍有未清理占位符：%s" % "、".join(sorted(set(hits))[:8])
    return True, "无占位符残留"


def check_action_specificity(text, artifact_type):
    if artifact_type == "weekly":
        return None, "周报不适用动作具体性检查"
    section = _next_section(text)
    if not section:
        return None, "无「## 下一步」小节，跳过"
    bullets = _extract_next_bullets(section)
    if len(bullets) < 2:
        return None, "下一步只有 %d 条动作（建议 ≥2 条）" % len(bullets)
    good = []
    for b in bullets:
        if len(b) >= 10 and any(v in b for v in ACTION_VERBS):
            good.append(b)
    if len(good) >= 2:
        return True, "%d 条动作具体可执行" % len(good)
    return None, "动作过于笼统：需要「动词 + 对象 + 可验收结果」"


def run_all(text, artifact_type="memo"):
    checks = [
        (1, "首屏一句话判断", check_answer_first),
        (2, "下一步三档动作", check_next_actions),
        (3, "依据标签", check_labels),
        (4, "引用格式", check_citations),
        (5, "绝对化/过度承诺", check_overclaim),
        (6, "内部黑话", check_jargon),
        (7, "末尾说明", check_disclaimer),
        (8, "代写/造假表述", check_ghostwriting),
        (9, "占位符清理", check_placeholders),
        (10, "动作具体性", check_action_specificity),
    ]
    results = []
    for num, name, fn in checks:
        try:
            ok, detail = fn(text, artifact_type)
        except Exception as exc:  # 校验器自身异常按硬失败处理，避免静默放行
            results.append(_status(num, name, "fail", "校验异常：%s: %s" % (type(exc).__name__, exc)))
            continue
        if ok is True:
            status = "pass"
        elif ok is None:
            status = "warn"
        else:
            status = "fail"
        results.append(_status(num, name, status, detail))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="研究生产物轻校验（grad profile），十条检查。"
    )
    parser.add_argument("--input", required=True, help="待校验的 Markdown 文件")
    parser.add_argument(
        "--type", default="memo", choices=ARTIFACT_TYPES,
        help="产物类型（默认 memo）",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.exists():
        print("ERROR: 文件不存在：%s" % path, file=sys.stderr)
        return 2
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print("ERROR: 读取失败：%s" % exc, file=sys.stderr)
        return 2

    results = run_all(text, args.type)
    hard = [r for r in results if r["status"] == "fail"]
    warns = [r for r in results if r["status"] == "warn"]

    if args.json:
        payload = {
            "file": str(path),
            "type": args.type,
            "validator_version": __version__,
            "passed": len(hard) == 0,
            "hard_fail": len(hard),
            "warning": len(warns),
            "checks": results,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("研究生产物校验：%s（类型 %s）" % (path, args.type))
        marks = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}
        for r in results:
            print("%s %2d. %s — %s" % (marks[r["status"]], r["num"], r["name"], r["detail"]))
        verdict = "通过" if not hard else "不通过"
        print("结果：%s（硬失败 %d，警告 %d）" % (verdict, len(hard), len(warns)))

    return 0 if not hard else 1


if __name__ == "__main__":
    sys.exit(main())
