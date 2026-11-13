# 研究生科研副驾（InterSci-Grad）

> 面向硕士/博士：把"我该做什么、读什么、怎么开题、实验怎么做、论文怎么写、导师那句话什么意思"
> 变成**今天就能动手的下一步**。

`v5.0.0` · 165 tests · MIT · 不配 API Key 也能用（检索自动走 Crossref）· 不绑定某个 agent

**第一次用？** 不用看命令：把「模板 A」整段复制给你的 agent（DSH、Claude Code、Cursor、ChatGPT、Claude 网页版都行），填掉 4 个空，剩下的它做。

---

## 一、小白路径：让 agent 帮你装

你只需要做三件事：**复制模板 A → 填 4 个空 → 看它最后那三句汇报**（装在哪、Key 生效没、能不能搜到真文献）。

### 模板 A：安装 + 配 Key + 自检（整段复制）

```text
【任务】帮我安装并启用 intersci-grad 科研技能包，全程你操作，我只负责回答和粘贴 Key。

【我的情况】（把尖括号改成我的；没写的按默认处理）
- 电脑系统：<Windows 11 / macOS / Linux>
- 我在用的 agent：<DSH / Claude Code / Cursor / ChatGPT 网页版 / 其他：____>
- 安装位置：<默认即可 / 指定路径：____>
- 我的 SCP Key：<粘贴 Key；没有就写"没有"，留空也能用>

【按顺序做，最后一起汇报】
1. 下载：从 https://github.com/ChenXiao-yx/intersci-grad 拿代码。有 git 就 git clone，没有就网页下载 ZIP 解压；目录名保持 intersci-grad。
2. 安装：按你这个 agent 自己的机制加载——有"技能/skills"目录就放进去；没有就把 SKILL.md 设为常驻指令、需要时再读 references/ 里的文件；只能传文件就告诉我该上传哪几个。
3. 依赖与 Key：能执行命令就装 python -m pip install -r scripts/requirements.txt；把我的 Key 写进 .env 的 SCP_HUB_API_KEY（没有 Key 就从 .env.example 复制一份留空）。不要把 Key 回显到聊天里，也不要提交到 git。
4. 自检：执行 python scripts/search_papers.py --query "wearable stress recognition" --top_k 5 --pretty --output ./search_test.json，确认结果里没有 "is_mock": true；再执行 python scripts/validate_grad.py --input examples/grad/topic_memo.md --type memo，确认输出 PASS。
5. 汇报：用三句话告诉我——装在哪、Key 有没有生效、能不能搜到真文献。任何一步失败就停下，把报错原文贴给我。
```

### 你要填的 4 个空

| 空 | 怎么填 | 填错或不填的后果 |
| :--- | :--- | :--- |
| 电脑系统 | Windows / macOS / Linux 选一个 | agent 容易给错命令，装不上 |
| 在用 agent | 写你实际用的名字 | 可能按别家规范装，你的 agent 根本不加载 |
| 安装位置 | 不确定就写"默认即可" | 装进临时目录，换个会话就找不到 |
| SCP Key | 打开 [SCP Key 页面](https://discovery.intern-ai.org.cn/user-center/system?tab=apikey)，登录后复制；没有就写"没有" | 检索降级到 Crossref：能搜，但常缺摘要、没有被引 |

Key 长什么样、放哪、怎么换，见「专业路径 · 第 4 步」；小白这里只要粘贴一次。

### 你的 agent 属于哪一类

| 你的 agent | 能走到 | 需要额外做的 |
| :--- | :--- | :--- |
| 能执行命令（DSH、Claude Code、Cursor、Codex、Gemini CLI 等） | 模板 A 全部 5 步 | 无 |
| 只能上传文件 / 知识库（ChatGPT、Claude 网页版） | 第 1、2、5 步；第 3、4 步用不上（Key 对它没意义） | 检索交给它自己的联网搜索，并要求按模板 B 标来源 |
| 不能执行命令也不能联网 | 只有方法，没有检索 | 明确要求它写"本轮未检索" |

不确定自己是哪一类？直接把模板 A 粘过去——它会告诉你自己能走到哪一步，走到哪算哪。

### 模板 B：装好之后，粘一次长期生效

```text
你按 intersci-grad 的规则帮我做科研：涉及文献时先检索、再下结论，不凭记忆列文献。
- 有终端：先跑 python "<技能目录>/scripts/search_papers.py" --query "<2–5 个英文核心词>" --top_k 10 --domain <域> --pretty --output "<工作目录>/search_<主题>.json"，读这个 JSON 再说话。
- 没终端：用你的联网搜索，但每条引用必须给 DOI 或可点链接。
硬规则：is_mock:true 的条目一律丢弃；doi 或 year 为空只能标"仅摘要"；作者、年份、期刊以返回结果为准，不补全。
至少 2–3 组检索式（核心词、同义词、作者名、survey）之后才允许说"没人做过"，并写成"截至 <日期> 在 <数据源> 用 <关键词> 未检索到"。
--domain 可选：AI / hardware / material / biotech / drug / regulatory / oncology / chemistry / patent / knowledge / psychology / education / social / business / default。
```

装完想先看看它长什么样：直接说"我研二，导师让我先看看可穿戴压力识别，还剩 12 个月"，会得到一页行动备忘。产物样例见 [examples/grad/](examples/grad/README.md)。

---

## 二、专业路径：自己动手装（约 5 分钟）

| 步骤 | 做什么 | 跳过会怎样 |
| :--- | :--- | :--- |
| 1 | 拿到代码 | 后面全做不了 |
| 2 | 放进你的 agent | 代码在硬盘上，agent 不知道它存在 |
| 3 | 装 `requests` | 检索降级到 Crossref：摘要大多缺失、没有被引数 |
| 4 | 配 `.env` 并填 Key | 每次运行停下来问你要 Key；只能用 Crossref |
| 5 | 跑自检 | 可能一直在用 `is_mock` 假文献，等于编造引用 |
| 6 | 卸载 / 升级 | —— |

### 1. 拿到代码

```bash
git clone https://github.com/ChenXiao-yx/intersci-grad.git
```

没有 git：在仓库页点 `Code → Download ZIP` 解压，目录名保持 `intersci-grad`。

### 2. 放进你的 agent

skill 的通用形态是"一个目录 + 一份 `SKILL.md`"。不同 agent 的加载方式：

| 你的 agent | 放哪 | 它怎么加载 |
| :--- | :--- | :--- |
| **DSH** | `~/.dsh/skills/intersci-grad`（或项目 `<项目根>/.dsh/skills/intersci-grad`） | 自动扫描，新开会话即出现 |
| **Claude Code** | 项目内 `.claude/skills/intersci-grad/`，或用户级 `~/.claude/skills/` | 读 `SKILL.md` 的 name/description，按需加载 `references/` |
| **Cursor / Windsurf 等 IDE agent** | 放进项目根目录 `intersci-grad/`，或把 `SKILL.md` 加进 rules | 让它"读 `intersci-grad/SKILL.md` 并遵守" |
| **ChatGPT / Claude 网页版** | 上传 `SKILL.md` + `references/*.md` 到项目文件 / 知识库 | 对话开头让它按该文件回答 |
| **其他能跑命令的 CLI** | 克隆到工作目录即可 | 直接调 `scripts/` 下的脚本 |

**DSH 用户级安装（Windows）：**

```powershell
robocopy . "$env:DSH_HOME\skills\intersci-grad" /E /XD .git tests docs __pycache__ .pytest_cache dist .github delivery /XF .env *.pyc
```

**macOS / Linux：**

```bash
mkdir -p ~/.dsh/skills/intersci-grad
rsync -a --exclude=.git --exclude=tests --exclude=docs --exclude=__pycache__ --exclude=dist --exclude=.github --exclude=.env ./ ~/.dsh/skills/intersci-grad/
```

装完新开一个会话，技能列表里应出现 `intersci-grad`。

### 3. 装依赖

```bash
python -m pip install -r "<技能目录>/scripts/requirements.txt"
```

Python >= 3.8。只有 `requests` 一个第三方包，且仅 SCP 检索需要；判断、模板、校验器是纯标准库。缺它时 stderr 会反复打印 `'requests' package not installed`，检索自动退到 Crossref。

### 4. 配 `.env` 并填 Key

先建文件，再填 Key：

```bash
cp "<技能目录>/.env.example" "<技能目录>/.env"
# Windows PowerShell: Copy-Item "<技能目录>\.env.example" "<技能目录>\.env"
```

Key 在 [SCP Key 页面](https://discovery.intern-ai.org.cn/user-center/system?tab=apikey) 登录后复制，粘到 `.env` 的 `SCP_HUB_API_KEY=` 后面（不要加引号）。三条链路：

| 你的情况 | `.env` 里填什么 | 检索实际走哪 | 结果质量 |
| :--- | :--- | :--- | :--- |
| 有 SCP Key（推荐） | `SCP_HUB_API_KEY=...` | SciVerse / Origene-Search / PubMed / Scholar-KG 等数据工具 | 好：带摘要、来源类型、被引 |
| 没有 Key 或 Key 失效 | 留空即可 | 自动降级到 Crossref（免费、无需 Key） | 中：多学科有元数据，常缺摘要 |
| 外网不通（或被代理拦截） | —— | mock 假数据（`is_mock: true`） | 不可用：拿它写矩阵等于编造引用 |

`.env` 放技能根目录即可（脚本会向上找 3 层）；它已在 `.gitignore` 里，**不要提交、不要打包、不要发给别人**——Key 是 bearer 令牌，泄露后无法按人回收。

### 5. 跑自检

```bash
python "<技能目录>/scripts/key_setup.py" --status
python "<技能目录>/scripts/search_papers.py" --query "wearable stress recognition" --top_k 5 --pretty --output ./search_test.json
```

判据：文件里至少有 1 条带 `doi` 的真实条目，且全文没有 `"is_mock": true`。SCP 返回的个别 PubMed 记录 `doi`/`year` 为空，只能标"仅摘要"，不要补全。

- 出现 `INFO [provider_fallback]`：走的是 Crossref，正常；
- 出现 `auth_error`：Key 写错或已失效，改 `.env`，不用重启；
- 出现 `parse_error`：后端解析失败，脚本会自动降级，不用处理。

### 6. 卸载 / 升级

删除 `intersci-grad` 文件夹即卸载；升级用新版本覆盖同名文件夹（DSH 会自动刷新，必要时新开会话）。

分发给别人的完整检查清单见 [DISTRIBUTION.md](DISTRIBUTION.md)。

---

## 三、故障排查

| 现象 | 原因 | 修复 |
| :--- | :--- | :--- |
| 技能列表里没有 `intersci-grad` | 目录层级不对，或 frontmatter 坏了 | 确认是 `<root>/intersci-grad/SKILL.md`，文件夹名与 `name` 一致 |
| agent 说"我没有技能机制" | 它不支持 skill 目录 | 改为把 `SKILL.md` 设为常驻指令，或上传到知识库 |
| 搜出来全是 mock | 没 Key，且 Crossref 也不通 | 查网络；装 `requests`；填 SCP Key；重跑自检 |
| 终端停在"请粘贴你的 SCP_HUB_API_KEY" | 没有 `.env`，或 Key 为空 | 直接回车跳过；长期方案是按第 4 步建 `.env` |
| 报 `auth_error` | Key 写错或已失效 | 去 Key 页面重新复制，改 `.env`，无需重启 |
| 结果只有元数据、没有摘要 | 走的是 Crossref 免费兜底 | 正常现象；要摘要和被引就配 SCP Key |
| 中文乱码 | 终端不是 UTF-8 | Windows 先 `chcp 65001`，或设 `$env:PYTHONIOENCODING='utf-8'` |
| 改了 `.env` 没生效 | 终端里已有同名环境变量，优先级更高 | 关掉该变量或新开终端 |
| 脚本提示找不到文件 | 用了相对 cwd 的路径 | 用 `<技能目录>/scripts/...` 的绝对路径 |

---

## 四、七种工作流

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

## 五、校验产物

交付前建议跑一次轻校验（纯标准库，无需联网、无需 API Key）。`<技能目录>` 指 skill 加载时显示的基目录；在本仓库开发时就是仓库根目录：

```bash
# 在 skill 目录下
python scripts/validate_grad.py --input examples/grad/topic_memo.md --type memo

# 在任意目录
python "<技能目录>/scripts/validate_grad.py" --input "<技能目录>/examples/grad/topic_memo.md" --type memo
```

十条检查：一句话判断、下一步三档动作、依据标签、引用格式、过度承诺、内部黑话、末尾说明、代写表述、占位符、动作具体性。

- 退出码 `0`：通过（可带警告）
- `1`：存在硬失败，必须重写
- `2`：文件不存在或参数错误

加 `--json` 输出机器可读结果。

## 六、构建发布包

```bash
python scripts/make_release.py --check-only   # 自检：不写文件，只报告
python scripts/make_release.py                # 生成 dist/intersci-grad-v5.0.0.zip + SHA256SUMS.txt
python scripts/check_submission.py dist/intersci-grad-v5.0.0.zip  # 上传前：无 .git/.env/二进制
```

发布包只含运行文件，自动排除 `.env`、`tests/`、`docs/`、缓存，并做密钥扫描。构建后顶层目录固定为 `intersci-grad/`，解压即与技能名一致。

**提交到 skill 平台时不要传仓库根目录**：`.git/index` 是二进制，会被平台判成“文件内容与后缀不符”，`.env` 还会泄露密钥。平台能传压缩包就传 [intersci-grad-v5.0.0.zip](dist/intersci-grad-v5.0.0.zip)；只能传文件 / 文件夹就传构建后生成的 `upload/intersci-grad/` 文件夹本身。上传前按 [DISTRIBUTION.md](DISTRIBUTION.md) §6.1 的自检流程过一遍。

## 七、文件地图

```
intersci-grad/
├── SKILL.md                          # 主文件（七种工作流 + 输出契约）
├── README.md
├── .env.example                      # 配置模板（Key 只影响检索质量）
├── DISTRIBUTION.md                   # 分发 / 安装 / 发布检查清单
├── SECURITY.md                       # 安全、密钥、隐私、提示词注入
├── RELEASE_NOTES.md                  # v5.0.0 发布说明
├── EXECUTION_CHECKLIST.md            # 执行速查（档位/模式/自救）
├── CONTRIBUTING.md
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
│   ├── search_papers.py              # 论文检索（有 Key 走 SCP，无 Key 走 Crossref）
│   ├── key_setup.py                  # Key 状态诊断 / 首次运行引导
│   ├── make_release.py               # 生成可上传的 release zip + 校验和
│   ├── check_submission.py           # 上传前自检：.git/.env/二进制/UTF-8
│   ├── validate_output.py            # 旧版尽调校验（保留）
│   ├── score_evidence.py             # 旧版证据计分（保留）
│   └── ...
├── examples/grad/                    # 六份黄金样例
├── tests/
└── dist/                             # 构建产物（gitignore，不提交）
```

## 八、旧版产业尽调

如果你要做的是**技术尽调 / 立项简报**（十章结构、证据计分、三选一建议），旧版协议完整保留：

- 执行手册：[references/legacy-rd-engine.md](references/legacy-rd-engine.md)
- 输出模板：[references/output-template.md](references/output-template.md)
- 证据规则：[references/evidence-rubric.md](references/evidence-rubric.md)
- 旧版校验器：`scripts/validate_output.py`（21 项校验，规则不变）

两套输出结构不要混用：研究生场景默认走 `SKILL.md`，尽调场景走旧版。

## 九、测试

```bash
python -m pytest -q
SKIP_NETWORK_TESTS=1 python -m pytest -q      # macOS/Linux 离线模式
$env:SKIP_NETWORK_TESTS='1'; python -m pytest -q  # Windows PowerShell
```

当前 165 条测试（离线模式 162 通过 + 3 个实网用例跳过），覆盖黄金样例、坏样本拦截、旧版计分、发布包自检与回归。CI 在 Ubuntu/Windows/macOS × Python 3.8/3.12 上跑离线模式。

## 十、安全与发布

- 安全、密钥、隐私、提示词注入：[SECURITY.md](SECURITY.md)
- v5.0.0 发布说明：[RELEASE_NOTES.md](RELEASE_NOTES.md)
- 分发给别人的检查清单：[DISTRIBUTION.md](DISTRIBUTION.md)

## 边界

- 提供科研方法与决策辅助，**不构成医疗、法律、投资建议**，不替代导师、评委和学校学位文件。
- 学位要求、署名规范、伦理审查、AI 使用政策，以学校/期刊正式文件为准。
- 持续两周以上的焦虑、失眠或情绪问题影响学习时，请联系学校心理中心或信任的人。

## License

MIT
