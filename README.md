# 研究生科研副驾（InterSci-Grad）

> 面向硕士/博士：把"我该做什么、读什么、怎么开题、实验怎么做、论文怎么写、导师那句话什么意思"
> 变成**今天就能动手的下一步**。

`v5.0.0` · 165 tests（离线 162 + 3 实网跳过）· MIT · 不配 API Key 也能用（检索自动走 Crossref）

**刚下载下来？** 想让它真的去搜文献，按下面「5 分钟装好（含文献检索）」走完四步；只想先聊选题和开题，装完第 1 步就能对话。

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

## 5 分钟装好（含文献检索）

| 步骤 | 做什么 | 跳过会怎样 |
| :--- | :--- | :--- |
| 1 | 把 `intersci-grad/` 放进 DSH 的 skill 目录 | 技能列表里没有它，Agent 不会触发，你只能每次手动敲脚本路径 |
| 2 | `python -m pip install -r scripts/requirements.txt`（只有 `requests`） | SCP 数据工具全部不可用，检索降级到 Crossref：摘要大多缺失、没有被引数，排序也更弱 |
| 3 | 复制 `.env.example` 为 `.env`，要更强检索就填 `SCP_HUB_API_KEY` | 每次运行都会停下来问你要 Key（在 Agent 里等于卡住），且只能用 Crossref |
| 4 | 跑两条自检命令，确认结果里没有 `is_mock` | 你可能一直在用 mock 假文献写矩阵——那等于编造引用 |

只想聊选题、开题、实验、写作：装完第 1 步就能用；第 2–4 步只影响"它能不能真的去搜文献"。检索入口是 `scripts/search_papers.py`，不依赖模型自己联网。

### 第 1 步：放进 skill 目录

DSH 会自动扫描 skill 目录并热加载，不需要注册命令。

**方式一：用户级（推荐，所有项目可用）**

```powershell
# Windows
robocopy . "$env:DSH_HOME\skills\intersci-grad" /E /XD .git tests docs __pycache__ .pytest_cache dist .github delivery /XF .env *.pyc
```

```bash
# macOS / Linux
mkdir -p ~/.dsh/skills/intersci-grad
rsync -a --exclude=.git --exclude=tests --exclude=docs --exclude=__pycache__ --exclude=dist --exclude=.github --exclude=.env ./ ~/.dsh/skills/intersci-grad/
```

**方式二：项目级（只在这个项目生效）**

把上面的目标改成 `<项目根>/.dsh/skills/intersci-grad`。项目根按 `.git` 识别。

装完新开一个 DSH 会话，技能列表里应出现 `intersci-grad`；随便问一句"我研二，导师让我先看看可穿戴压力识别，还剩 12 个月"，能出一页行动备忘即装对了。

### 第 2 步：装依赖

```bash
python -m pip install -r "<skill-dir>/scripts/requirements.txt"
```

Python >= 3.8。只有 `requests` 一个第三方包，且仅 SCP 检索需要；判断、模板、校验器是纯标准库，不装也能跑。缺它时 stderr 会反复打印 `'requests' package not installed`，检索自动退到 Crossref。

### 第 3 步：配 `.env`（决定检索质量）

```bash
cp "<skill-dir>/.env.example" "<skill-dir>/.env"
# Windows PowerShell: Copy-Item "<skill-dir>\.env.example" "<skill-dir>\.env"
```

| 你的情况 | `.env` 里填什么 | 检索实际走哪 | 结果质量 |
| :--- | :--- | :--- | :--- |
| 有 SCP Key（推荐） | `SCP_HUB_API_KEY=...`，申请：<https://scp.intern-ai.org.cn> | SciVerse / Origene-Search / PubMed / Scholar-KG 等数据工具 | 好：带摘要、来源类型、被引 |
| 没有 Key 或 Key 失效 | 留空即可 | 自动降级到 Crossref（免费、无需 Key） | 中：多学科有元数据，常缺摘要 |
| 外网不通（或被代理拦截） | — | mock 假数据（`is_mock: true`） | 不可用：拿它写矩阵等于编造引用 |

`.env` 放 skill 根目录即可（脚本会向上找 3 层）；它已在 `.gitignore` 里，**不要提交、不要打包、不要发给别人**——Key 是 bearer 令牌，泄露后无法按人回收。

### 第 4 步：自检

```bash
python "<skill-dir>/scripts/key_setup.py" --status
python "<skill-dir>/scripts/search_papers.py" --query "wearable stress recognition" --top_k 5 --pretty --output ./search_test.json
```

判据：文件里至少有 1 条带 `doi` 的真实条目，且全文没有 `"is_mock": true`。SCP 返回的个别 PubMed 记录 `doi`/`year` 为空，只能标"仅摘要"，不要补全。

- 出现 `INFO [provider_fallback]`：走的是 Crossref，正常；
- 出现 `auth_error`：Key 写错或已失效，改 `.env` 即可，不用重启；
- 出现 `parse_error`：后端解析失败，脚本会自动降级，不用处理。

### 给 Agent 的启用指令（粘一次，之后正常说话）

```text
你已加载 intersci-grad，技能目录 = <skill-dir>。
凡涉及文献（选题撞题、综述、related work、文献矩阵、精读卡、开题依据），先跑
python "<skill-dir>/scripts/search_papers.py" --query "<2–5 个英文核心词>" --top_k 10 --domain <域> --pretty --output "<工作目录>/search_<主题>.json"
再下结论。--domain 取 AI / hardware / material / biotech / drug / regulatory / oncology / chemistry / patent / knowledge / psychology / education / social / business / default。
硬规则：is_mock:true 的条目一律丢弃、不得引用；doi 或 year 为空只能标"仅摘要/元数据不全"；作者、年份、期刊以返回 JSON 为准，不补全、不脑补。
至少 2–3 组检索式（核心词、同义词、作者名、survey）之后才允许说"没人做过"，且必须写成"截至 <日期> 在 <数据源> 用 <关键词> 未检索到"。
SCP 失败会自动走 Crossref；两者都没结果就明说"本次未取到真实文献"，可改用 web_search 兜底并注明来源；任何情况下不得用 mock 或记忆冒充检索结果。
```

### 卸载 / 升级

删除 `intersci-grad` 文件夹即可卸载；升级用新版本覆盖同名文件夹，watcher 会自动刷新，必要时新开会话。

分发给别人的完整检查清单见 [DISTRIBUTION.md](DISTRIBUTION.md)。

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

## 故障排查

| 现象 | 原因 | 修复 |
| :--- | :--- | :--- |
| 技能列表里没有 `intersci-grad` | 目录层级不对，或 frontmatter 坏了 | 确认是 `<root>/intersci-grad/SKILL.md`，文件夹名与 `name` 一致 |
| 搜出来全是 mock | 没 Key，且 Crossref 也不通 | 查网络；装 `requests`；填 SCP Key；重跑第 4 步自检 |
| 终端停在"请粘贴你的 SCP_HUB_API_KEY" | 没有 `.env`，或 Key 为空 | 直接回车跳过；长期方案是按第 3 步建 `.env` |
| 报 `auth_error` | Key 写错或已失效 | 重新申请，改 `.env`，无需重启 |
| 结果只有元数据、没有摘要 | 走的是 Crossref 免费兜底 | 正常现象；要摘要和被引就配 SCP Key |
| 中文乱码 | 终端不是 UTF-8 | Windows 先 `chcp 65001`，或设 `$env:PYTHONIOENCODING='utf-8'` |
| 改了 `.env` 没生效 | 终端里已有同名环境变量，优先级更高 | 关掉该变量或新开终端 |
| 脚本提示找不到文件 | 用了相对 cwd 的路径 | 用 `<skill-dir>/scripts/...` 的绝对路径 |

## 构建发布包

```bash
python scripts/make_release.py --check-only   # 自检：不写文件，只报告
python scripts/make_release.py                # 生成 dist/intersci-grad-v5.0.0.zip + SHA256SUMS.txt
python scripts/check_submission.py dist/intersci-grad-v5.0.0.zip  # 上传前：无 .git/.env/二进制
```

发布包只含运行文件，自动排除 `.env`、`tests/`、`docs/`、缓存，并做密钥扫描。构建后顶层目录固定为 `intersci-grad/`，解压即与技能名一致。

**提交到 skill 平台时不要传仓库根目录**：`.git/index` 是二进制，会被平台判成“文件内容与后缀不符”，`.env` 还会泄露密钥。平台能传压缩包就传 [intersci-grad-v5.0.0.zip](dist/intersci-grad-v5.0.0.zip)；只能传文件 / 文件夹就传构建后生成的 `upload/intersci-grad/` 文件夹本身。上传前按 [DISTRIBUTION.md](DISTRIBUTION.md) §6.1 的自检流程过一遍。

## 文件地图

```
intersci-grad/                        # 本地目录名可保留，公开仓库建议用 intersci-grad
├── SKILL.md                          # 研究生科研副驾主文件（七种工作流 + 输出契约）
├── README.md
├── .env.example                      # 可选配置模板（只有 SCP 检索需要 Key）
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
│   ├── check_submission.py           # 上传前自检：.git/.env/二进制/UTF-8
│   ├── validate_output.py            # 旧版尽调校验（保留）
│   ├── key_setup.py                  # Key 状态诊断 / 首次运行引导
│   ├── search_papers.py              # 论文检索（有 Key 走 SCP，无 Key 走 Crossref）
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
