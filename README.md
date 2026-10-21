# 研究生科研副驾（InterSci-Grad）

> 面向硕士/博士：把"我该做什么、读什么、怎么开题、实验怎么做、论文怎么写、导师那句话什么意思"
> 变成**今天就能动手的下一步**。

`v5.0.0` · 165 tests（离线 162 + 3 实网跳过）· MIT · 核心功能零 API Key

这个 skill 不是文献摘要器，也不是论文代写器。它只做三件事：

1. **给判断**：这个题能不能做、卡在哪、先补哪一块。
2. **切任务**：把"写论文"切成今天 30 分钟能完成的一步。
3. **帮你说话**：开题、组会、答辩、审稿回复，把逻辑链和取舍讲清楚。

## 它懂的三件事

- **选题不是"找个没人做过的"**：先过新颖性、可行性、时间三关，再谈创新。
- **读不完不是你不努力**：80% 的论文只配读 5 分钟，值得精读的只有 3–5 篇。
- **导师的话要翻译**："创新性不够"通常不是让你加形容词，而是你没说清"以前不知道什么"。

## 30 秒上手

直接对 Agent 说人话即可，不需要先填表：

```text
我研二，做可穿戴生理信号识别学业压力，导师让我"先看看这个方向"，
我还有 12 个月到预答辩，实验室只有两套 E4，没有 GPU。我该从哪开始？
```

默认会得到一页行动备忘：一句话判断、三条路、今天/本周/两周的动作、依据和待确认问题。

想直接看产物长什么样：

- [选题卡](examples/grad/topic_memo.md)
- [开题一页纸](examples/grad/proposal_onepager.md)
- [文献矩阵](examples/grad/literature_matrix.md)
- [单篇精读卡](examples/grad/reading_card.md)
- [实验设计卡](examples/grad/experiment_card.md)
- [组会提纲](examples/grad/meeting_outline.md)

样例说明与使用方式见 [examples/grad/README.md](examples/grad/README.md)：文献真实，课题、数据与结果仅作演示。

## 七种工作流

| 你说 | 你拿到 |
| :--- | :--- |
| "还剩 X 个月，来得及吗" | 进度体检 + 倒推表 |
| "导师给了个大方向" / "不知道做什么" | 选题卡（3 个候选 + 推荐） |
| "文献读不完" / "综述写不出" | 文献矩阵 + 缺口陈述 |
| "要开题/中期/答辩" | 开题一页纸 + 评委 12 问 |
| "实验做不出来" / "结果不显著" | 实验设计卡 + 排查清单 |
| "写不出/被拒/要 rebuttal" | 写作提纲 / 选刊表 / 回复表 |
| "组会讲什么" / "导师那句话什么意思" | 组会提纲 / 周报 / 提问句 |

完整打法（含话术、模板、判断标准）见：

- [references/grad-playbook.md](references/grad-playbook.md)：痛点地图、选题、读文献、开题、实验、写作、导师沟通、时间与心理。
- [references/artifact-templates.md](references/artifact-templates.md)：9 套产物模板 + 可选研究画像。
- [references/evidence-and-integrity.md](references/evidence-and-integrity.md)：引用核验、禁止话术、AI 使用边界。

## 校验产物

交付前建议跑一次轻校验（纯标准库，无需联网、无需 API Key）。`<skill-dir>` 指 skill 加载时显示的基目录；在本仓库开发时就是仓库根目录：

```bash
# 在 skill 目录下
python scripts/validate_grad.py --input examples/grad/topic_memo.md --type memo

# 在任意目录
python "<skill-dir>/scripts/validate_grad.py" --input "<skill-dir>/examples/grad/topic_memo.md" --type memo
```

十条检查：一句话判断、下一步三档动作、依据标签、引用格式、过度承诺、内部黑话、末尾说明、代写表述、占位符、动作具体性。

- 退出码 `0`：通过（可带警告）
- `1`：存在硬失败，必须重写
- `2`：文件不存在或参数错误

加 `--json` 输出机器可读结果。

## 安装到 DeepSeek Harness

DSH 会自动扫描 skill 目录并热加载，不需要注册命令。

### 方式一：用户级（推荐，所有项目可用）

```powershell
# Windows
robocopy . "$env:DSH_HOME\skills\intersci-grad" /E /XD .git tests docs __pycache__ .pytest_cache dist .github delivery /XF .env *.pyc
```

```bash
# macOS / Linux
mkdir -p ~/.dsh/skills/intersci-grad
rsync -a --exclude=.git --exclude=tests --exclude=docs --exclude=__pycache__ --exclude=dist --exclude=.github --exclude=.env ./ ~/.dsh/skills/intersci-grad/
```

### 方式二：项目级（只在这个项目生效）

把上面的目标改成 `<项目根>/.dsh/skills/intersci-grad`。项目根按 `.git` 识别。

### 验证

1. 新开一个 DSH 会话，技能列表里应出现 `intersci-grad`。
2. 输入："我研二，导师让我先看看可穿戴压力识别，还剩 12 个月。"
3. 或直接跑校验：

```bash
python "<skill-dir>/scripts/validate_grad.py" --input "<skill-dir>/examples/grad/topic_memo.md" --type memo
```

`<skill-dir>` 是 skill 加载时显示的基目录。

### 依赖

Python >= 3.8；核心功能零第三方依赖，不需要 API Key。旧版 SCP 数据工具可选，见 `.env.example`。

### 卸载 / 升级

删除 `intersci-grad` 文件夹即可卸载；升级用新版本覆盖同名文件夹，watcher 会自动刷新，必要时新开会话。

分发给别人的完整检查清单见 [DISTRIBUTION.md](DISTRIBUTION.md)。

## 构建发布包

```bash
python scripts/make_release.py --check-only   # 自检：不写文件，只报告
python scripts/make_release.py                # 生成 dist/intersci-grad-v5.0.0.zip + SHA256SUMS.txt
```

发布包只含运行文件，自动排除 `.env`、`tests/`、`docs/`、缓存，并做密钥扫描。上传前按 [DISTRIBUTION.md](DISTRIBUTION.md) 的 16 项清单过一遍。

## 文件地图

```
intersci-grad/                        # 本地目录名可保留，公开仓库建议用 intersci-grad
├── SKILL.md                          # 研究生科研副驾主文件（七种工作流 + 输出契约）
├── README.md
├── DISTRIBUTION.md                   # 分发 / 安装 / 发布检查清单
├── SECURITY.md                       # 安全、密钥、隐私、提示词注入
├── RELEASE_NOTES.md                  # v5.0.0 发布说明
├── EXECUTION_CHECKLIST.md            # 执行速查（档位/模式/自救）
├── CONTRIBUTING.md                   # 贡献指南
├── CHANGELOG.md
├── .github/workflows/ci.yml          # 多平台 CI（离线测试 + 发布包自检）
├── references/
│   ├── grad-playbook.md              # 痛点 → 打法（核心）
│   ├── artifact-templates.md         # 9 套产物模板
│   ├── evidence-and-integrity.md     # 引用、诚信、AI 边界
│   ├── legacy-rd-engine.md           # 旧版十章产业尽调（保留）
│   ├── output-template.md            # 旧版输出模板（保留）
│   └── evidence-rubric.md            # 旧版证据规则（保留）
├── scripts/
│   ├── validate_grad.py              # 研究生轻校验（十条检查）
│   ├── make_release.py               # 生成可上传的 release zip + 校验和
│   ├── validate_output.py            # 旧版尽调校验（保留）
│   ├── search_papers.py              # 可选：论文检索
│   ├── score_evidence.py             # 可选：证据计分（旧版）
│   └── ...
├── examples/grad/                    # 六份黄金样例
├── tests/                            # 含 test_validate_grad.py
└── dist/                             # 构建产物（gitignore，不提交）
```

## 旧版产业尽调

如果你要做的是**技术尽调 / 立项简报**（十章结构、证据计分、三选一建议），旧版协议完整保留：

- 执行手册：[references/legacy-rd-engine.md](references/legacy-rd-engine.md)
- 输出模板：[references/output-template.md](references/output-template.md)
- 证据规则：[references/evidence-rubric.md](references/evidence-rubric.md)
- 旧版校验器：`scripts/validate_output.py`（21 项校验，规则不变）

两套输出结构不要混用：研究生场景默认走 `SKILL.md`，尽调场景走旧版。

## 测试

```bash
python -m pytest -q
SKIP_NETWORK_TESTS=1 python -m pytest -q      # macOS/Linux 离线模式
$env:SKIP_NETWORK_TESTS='1'; python -m pytest -q  # Windows PowerShell
```

当前 165 条测试（离线模式 162 通过 + 3 个实网用例跳过），覆盖黄金样例、坏样本拦截、旧版计分、发布包自检与回归。CI 在 Ubuntu/Windows/macOS × Python 3.8/3.12 上跑离线模式；实网用例可本地按需开启。

## 安全与发布

- 安全、密钥、隐私、提示词注入：[SECURITY.md](SECURITY.md)
- v5.0.0 发布说明：[RELEASE_NOTES.md](RELEASE_NOTES.md)
- 分发给别人的 16 项检查清单：[DISTRIBUTION.md](DISTRIBUTION.md)

## 边界

- 提供科研方法与决策辅助，**不构成医疗、法律、投资建议**，不替代导师、评委和学校学位文件。
- 学位要求、署名规范、伦理审查、AI 使用政策，以学校/期刊正式文件为准。
- 持续两周以上的焦虑、失眠或情绪问题影响学习时，请联系学校心理中心或信任的人。

## License

MIT
