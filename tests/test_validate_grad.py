"""validate_grad 轻校验器测试。

覆盖：
- 六份黄金样例在对应产物类型下全部通过
- 十条检查的硬失败路径（结论缺失、下一步缺失、过度承诺、黑话、说明缺失、代写、占位符、坏 DOI）
- 警告路径（依据标签不足、无引用、动作笼统）不阻断
- CLI 退出码：0=通过、1=硬失败、2=文件不存在
- 周报类型的三行结构
"""
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import validate_grad as vg

_ROOT = Path(__file__).resolve().parent.parent
_EXAMPLES = _ROOT / "examples" / "grad"

TYPES = {
    "topic_memo": "memo",
    "proposal_onepager": "proposal",
    "literature_matrix": "matrix",
    "reading_card": "reading",
    "experiment_card": "experiment",
    "meeting_outline": "meeting",
}


def _golden(kind):
    return (_EXAMPLES / ("%s.md" % kind)).read_text(encoding="utf-8")


def _statuses(results):
    return {r["num"]: r["status"] for r in results}


@pytest.mark.parametrize("kind,artifact_type", sorted(TYPES.items()))
def test_golden_samples_pass(kind, artifact_type):
    text = _golden(kind)
    results = vg.run_all(text, artifact_type)
    fails = [r for r in results if r["status"] == "fail"]
    assert fails == [], "黄金样例不应硬失败：%s" % fails


def test_answer_first_missing():
    text = _golden("topic_memo").replace("**一句话判断**", "**判断**")
    ok, detail = vg.check_answer_first(text, "memo")
    assert ok is False
    assert "一句话判断" in detail


def test_next_actions_missing_heading():
    text = _golden("topic_memo").replace("## 下一步", "## 后续")
    ok, detail = vg.check_next_actions(text, "memo")
    assert ok is False
    assert "下一步" in detail


def test_next_actions_requires_two_time_buckets():
    ok, detail = vg.check_next_actions("## 下一步\n\n- 今天把数据下好\n", "memo")
    assert ok is False
    assert "时间档" in detail


def test_weekly_structure():
    text = "**一句话判断**：本周有进展。\n\n本周：跑通基线\n卡点：没有卡点\n下周：做消融\n"
    ok, detail = vg.check_next_actions(text, "weekly")
    assert ok is True, detail


def test_hard_overclaim():
    ok, detail = vg.check_overclaim("按这个方案做，保证发表。", "memo")
    assert ok is False
    assert "保证发表" in detail


def test_soft_overclaim_is_warning():
    ok, detail = vg.check_overclaim("本工作填补空白。", "memo")
    assert ok is None
    assert "核验" in detail


def test_internal_jargon():
    ok, detail = vg.check_jargon("详见 SKILL.md 的规则。", "memo")
    assert ok is False
    assert "SKILL.md" in detail


def test_disclaimer_missing():
    text = "**一句话判断**：可做。\n\n## 下一步\n\n- 今天读论文\n- 本周跑基线\n"
    ok, detail = vg.check_disclaimer(text, "memo")
    assert ok is False
    assert "说明" in detail


def test_ghostwriting():
    ok, detail = vg.check_ghostwriting("我可以代写正文。", "memo")
    assert ok is False
    assert "代写" in detail


def test_placeholders():
    ok, detail = vg.check_placeholders("这里填 TODO。", "memo")
    assert ok is False
    assert "TODO" in detail


def test_bad_doi_format():
    ok, detail = vg.check_citations("见 https://doi.org/10.xxxx/abc", "memo")
    assert ok is False
    assert "DOI" in detail


def test_missing_citation_is_warning_for_memo():
    ok, detail = vg.check_citations("没有任何链接。", "memo")
    assert ok is None


def test_labels_below_minimum_is_warning():
    ok, detail = vg.check_labels("只有一句判断。", "memo")
    assert ok is None
    results = vg.run_all(
        "**一句话判断**：x\n\n## 下一步\n\n- 今天读一篇论文并记录\n- 本周跑一个基线实验\n\n"
        "> 本文件由 AI 辅助整理，引用与数据请自行核验；不替代导师意见与学校规范。",
        "memo",
    )
    # 标签不足只是警告，不阻断交付
    status = _statuses(results)[3]
    assert status == "warn"


def test_action_specificity_warns_on_vague():
    ok, detail = vg.check_action_specificity(
        "## 下一步\n\n- 继续努力\n- 多读文献\n", "memo"
    )
    assert ok is None


def test_run_all_fails_counted():
    text = "**一句话判断**：保证发表。\n\nTODO\n"
    results = vg.run_all(text, "memo")
    fails = [r for r in results if r["status"] == "fail"]
    assert len(fails) >= 4


def test_cli_exit_codes(capsys):
    good = _EXAMPLES / "topic_memo.md"
    assert vg.main(["--input", str(good), "--type", "memo"]) == 0

    # 复用仓库里已有的坏样本（旧版十章结构），在 grad 契约下必然硬失败
    bad = _ROOT / "tests" / "regression" / "fixtures" / "bad_samples" / "bad_vague_quality.md"
    assert vg.main(["--input", str(bad), "--type", "memo"]) == 1

    missing = _ROOT / "tests" / "fixtures" / "does_not_exist.md"
    assert vg.main(["--input", str(missing), "--type", "memo"]) == 2
    capsys.readouterr()


def test_cli_json_shape(capsys):
    path = _EXAMPLES / "topic_memo.md"
    vg.main(["--input", str(path), "--type", "memo", "--json"])
    payload = __import__("json").loads(capsys.readouterr().out)
    assert payload["passed"] is True
    assert payload["hard_fail"] == 0
    assert len(payload["checks"]) == 10
