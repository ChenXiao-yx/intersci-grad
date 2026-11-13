# 贡献指南

> 这个 skill 的目标是"研究生真的会用、用完真的少走一步"。贡献时优先问：
> **它有没有让某一步更可执行？** 而不是"规则是不是更全"。

## 可以贡献什么

| 类型 | 例子 | 改哪里 |
| :--- | :--- | :--- |
| 新工作流 | 投稿选刊、基金申请、开题被拒后的复盘 | `SKILL.md` + `references/grad-playbook.md` |
| 新产物模板 | cover letter、答辩逐页稿、实验记录表 | `references/artifact-templates.md` |
| 新样例 | 某个学科的真实（脱敏）使用示例 | `examples/grad/` |
| 新校验 | 能确定性拦住的坏输出 | `scripts/validate_grad.py` + `tests/` |
| 话术/痛点 | 导师沟通、组会、审稿回复的真实说法 | `references/grad-playbook.md` |
| 旧版能力 | 十章尽调、证据计分、SCP 数据工具 | `references/legacy-rd-engine.md` + 旧脚本 |

**不接受**：代写模板、编造文献的示例、承诺"包发"的话术、需要付费 Key 才能用的核心功能。

## 开发环境

```bash
git clone <repo-url>
cd intersci-grad
python -m pip install -r scripts/requirements.txt
python -m pip install pytest
```

Python >= 3.8。核心校验器 `scripts/validate_grad.py` 只用标准库。

## 提交前必须跑

```bash
python scripts/check_consistency.py          # 版本/配置/文档对账
python -m pytest -q                          # 全量测试
python scripts/make_release.py --check-only  # 发布包自检（不写文件）
python scripts/check_submission.py dist/intersci-grad-v5.0.0.zip  # 上传前文本审核自检
```

如果只改了某几份样例，至少跑：

```bash
python scripts/validate_grad.py --input examples/grad/topic_memo.md --type memo
```

CI 会跑 `SKIP_NETWORK_TESTS=1` 的离线测试；实网用例在本地按需跑。

## 加一个新工作流

1. 在 `SKILL.md` 的"七种工作流"表加一行：触发语 → 内部动作 → 产物。
2. 在 `references/grad-playbook.md` 加一节：痛点、判断标准、动作、话术、常见坑。
3. 如果产出新格式，在 `references/artifact-templates.md` 加模板，并在 `README.md` 的模板列表补一行。
4. 在 `examples/grad/` 加一份填好的样例；样例里的数据要标"教学示例"。
5. 如有确定性检查，加进 `scripts/validate_grad.py` 和 `tests/test_validate_grad.py`。
6. 在 `CHANGELOG.md` 追加一条。

## 加一个新校验

- 只做**确定性**检查：能写成正则/结构/计数，不依赖模型判断。
- 硬失败只留给"交付会误导人"的问题（编造、代写、绝对化承诺、缺结论）。
- 风格问题给警告，不阻断。
- 在 `validate_grad.py` 顶部 docstring 的"十条检查"里同步说明；如果数量变了，改标题和 `README` 里的"十条"。
- 加一条通过用例 + 一条失败用例。

## 改规则时的同步清单

| 改了 | 必须同步 |
| :--- | :--- |
| 输出契约 | `SKILL.md`、`EXECUTION_CHECKLIST.md`、`references/artifact-templates.md`、所有样例 |
| 判断标准 | `SKILL.md`、`references/grad-playbook.md`、至少一份样例 |
| 校验规则 | `scripts/validate_grad.py`、`tests/test_validate_grad.py`、`README` |
| 版本号 | `SKILL.md` frontmatter、`pyproject.toml`、`CHANGELOG.md` 尾行（`check_consistency.py` 会对账） |
| 安装/分发 | `README.md`、`DISTRIBUTION.md`、`scripts/make_release.py` |

## 旧版能力

旧版十章尽调仍在维护范围内：

- 入口：`references/legacy-rd-engine.md`
- 证据规则：`references/evidence-rubric.md` 与 `scripts/config/evidence_weights.json`（两者由 `check_consistency.py` 双向对账）
- 计分/校验：`scripts/score_evidence.py`、`scripts/validate_output.py`
- 旧测试全部保留，不要为了新功能删旧测试。

新增旧版领域时，按 `references/evidence-rubric.md` §4/§14.2 的流程改配置与文档，并跑一致性检查。

## PR 检查清单

- [ ] 目标单一：一个 PR 只做一件事。
- [ ] 所有命令在本地跑过；贴出测试结果。
- [ ] 新增/修改的样例通过 `validate_grad.py`。
- [ ] 没有 `.env`、密钥、个人数据、未脱敏的学校/导师信息。
- [ ] 没有绝对路径；脚本能从任意目录运行。
- [ ] 文档里的链接能点开。
- [ ] CHANGELOG 已追加；版本号三处一致。

## 风格

- 中文为主，术语保留英文原词（baseline、rebuttal、gap）。
- 一句话能说清，不写三段。
- 给动作，不给口号；给数字或"推测"标签，不写"显著提升"。
- 不写"保证/一定/稳过"。
