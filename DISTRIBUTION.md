# 分发与安装：让别人正常使用这个 skill

> 目标：别人拿到这个目录，放进正确位置，新开一个会话就能用；不报错、不缺文件、不泄露密钥。

---

## 1. DSH 的 skill 放在哪

DSH 按目录扫描 skill，不需要注册命令。优先级从高到低：

| Rank | 来源 | 路径 |
| :--- | :--- | :--- |
| 100 | project-dsh | `<项目根>/.dsh/skills` |
| 200 | project-agents | `<项目根>/.agents/skills` |
| 300 | custom | 配置项 `customSkillDirs` |
| 400 | user-dsh | `<DSH_HOME>/skills`（默认 `~/.dsh/skills`） |
| 500 | user-agents | `<AGENTS_HOME>/skills`（默认 `~/.agents/skills`） |

- 项目根按 `.git` 识别；没有 `.git` 时用当前工作目录。
- 同一个 skill 名不要同时放在多个 root，否则容易出现"改了没生效"。
- 用户级安装对所有项目生效；项目级安装只对该项目生效。

## 2. 目录格式（硬要求）

```
intersci-grad/
├── SKILL.md          # 必须有，YAML frontmatter 必须有 name + description
├── references/       # 按需加载的细节
├── scripts/          # 可选，能被 SKILL.md 引用
└── examples/         # 可选，给人看的样例
```

- 只识别 `<root>/<name>/SKILL.md` 或扁平文件 `<root>/<name>.md`。
- **不支持** `**/SKILL.md` 这种嵌套发现；不要把 skill 再套一层目录。
- 目录名与 frontmatter 的 `name` 保持一致，`name` 用 kebab-case。
- `description` 必填，写清"做什么 + 什么时候用 + 触发词"；`whenToUse` 可选但建议写。
- 可选字段：`disable-model-invocation`、`user-invocable`、`metadata`。未知字段一般被忽略，但不要依赖它们改变行为。

## 3. 发布前 16 项检查

- [ ] 目录名 == `name`，kebab-case，没有重名。
- [ ] `SKILL.md` 第一行是 `---`，YAML 能解析，`name` / `description` 非空。
- [ ] 所有被引用的文件都在包内：`references/`、`scripts/`、`examples/`。
- [ ] 没有绝对路径（`D:\`、`/Users/...`、`~`）；脚本路径用 `<skill-dir>/scripts/...` 说明。
- [ ] 没有 `.env`、API Key、cookie、个人数据、未公开数据。
- [ ] 核心功能不依赖网络和第三方包；可选依赖写清安装方式。
- [ ] Python >= 3.8，脚本纯标准库优先；跨平台路径用 `pathlib`。
- [ ] 从**另一个工作目录**运行一次脚本，确认不依赖 cwd。
- [ ] 所有黄金样例通过校验器；坏样本能被拦住。
- [ ] `python scripts/make_release.py --check-only` 通过（文件齐全、无密钥、版本一致）。
- [ ] 用 3 句真实用户会说的话测试触发，确认 skill 会被选中且首轮输出符合契约。
- [ ] 在一台干净机器/干净 profile 上安装一次，确认能发现、能加载。
- [ ] 版本号、CHANGELOG、LICENSE 齐全；升级/卸载方式写清。
- [ ] 脚本没有破坏性命令（删库、覆盖用户文件、外传数据）。
- [ ] README 有安装、30 秒上手、示例、故障排查。
- [ ] 公开仓库不包含 `tests/` 里的真实 LLM 原始输出、`docs/` 内部文档、`live_runs/`。

## 4. 别人机器上的验收 5 步

1. 把 `intersci-grad/` 放进 `~/.dsh/skills/`（或项目 `.dsh/skills/`）。
2. 新开一个 DSH 会话，技能列表出现 `intersci-grad`。
3. 输入："我研二，导师让我先看看可穿戴压力识别，还剩 12 个月，没有 GPU。"
4. 期望：先给一句话判断 + 三条路 + 今天/本周/两周动作，末尾有"自行核验"说明。
5. 跑一次校验器：

```bash
python "<skill-dir>/scripts/validate_grad.py" --input "<skill-dir>/examples/grad/topic_memo.md" --type memo
```

## 5. 常见故障

| 现象 | 原因 | 修复 |
| :--- | :--- | :--- |
| 技能列表没有 | 目录层级不对 / frontmatter 坏了 | 确认 `<root>/<name>/SKILL.md`；`name` 与目录一致 |
| 触发了但不按规则 | `description` 太宽 / 正文太长 | 收窄触发词；把细节移到 `references/` |
| 脚本找不到 | 用了相对 cwd 的路径 | 用 `<skill-dir>/scripts/...` 或先 `cd` 到 skill 目录 |
| 中文乱码 | 终端编码不是 UTF-8 | 终端切 UTF-8；文件保持 UTF-8 无 BOM |
| 改了没生效 | 缓存 / 同名 skill 在别的 root | 新开会话；删掉重复目录 |
| 装完报错 | 缺文件 / Python 版本低 | 对照 §3 检查；Python >= 3.8 |

## 6. 发布方式

- **一键构建**：`python scripts/make_release.py` 生成 `dist/intersci-grad-v5.0.0.zip` 与 `SHA256SUMS.txt`；`--check-only` 只检查不写文件（CI 用）。
- **Git 仓库**：打 tag（如 `v5.0.0`），Release 附上面生成的 zip。
- **zip 内容**：`SKILL.md`、`references/`、`scripts/`、`examples/`、`README.md`、`LICENSE`、`CHANGELOG.md`、`SECURITY.md`、`RELEASE_NOTES.md`、`DISTRIBUTION.md`。
- **不要打包**：`.git/`、`.env`、`tests/`、`docs/`、`__pycache__/`、`.pytest_cache/`、`live_runs/`、`dist/`。
- **版本**：语义化版本；`SKILL.md`、`pyproject.toml`、`CHANGELOG.md` 三处同步（本仓库有 `scripts/check_consistency.py` 对账）。
- **许可**：MIT；引用第三方文献/数据时保留出处与许可。
- **安全**：skill 会执行本地脚本，发布前自己审一遍；不要要求用户关闭安全策略。

## 7. 密钥与隐私（发布前必读）

- **研究生核心功能不需要任何密钥**：备忘、模板、校验器全部本地离线运行。
- **仓库根 `.env` 只在本机**：`.gitignore` 已排除；安装命令显式 `/XF .env` / `--exclude=.env`，不会复制到 skill 目录。
- **旧版 SCP 工具需要每个使用者自己的 Key**：不要把同一个 Key 分给多人，也不要写进 `SKILL.md`、示例、issue 或截图。
- **密钥是 bearer token**：谁拿到谁就能用，直到你在平台吊销/轮换；无法按人回收。
- **发布前扫描**：确认发布包没有 `.env`、`sk-...`、`SCP_HUB_API_KEY=真实值`、cookie、个人数据。
- **一旦泄露**：立刻在平台吊销并重新生成；检查 git 历史、Release zip、聊天记录；必要时通知使用者。
- **共享电脑**：同一 Windows 账号下的进程可以读 `.env`；敏感环境建议用系统凭据管理或临时环境变量。

## 8. 本仓库现状

- 已安装到 `~/.dsh/skills/intersci-grad`，可直接在新会话使用。
- 项目名与 skill 名已统一为 `intersci-grad`（`pyproject.toml` / `SKILL.md`）。
- CI 已加：`.github/workflows/ci.yml` 在 Ubuntu/Windows/macOS × Python 3.8/3.12 上跑一致性、离线测试和发布包自检。
- 发布脚本已加：`scripts/make_release.py`，自动排除 `.env`/测试/文档/缓存并做密钥扫描。
- 旧版十章产业尽调仍保留，但两套输出结构不要混用；`SKILL.md` 已注明入口。
- 本地目录名仍是 `intersci-kd-skill`；上传到 GitHub 时建议把仓库名改成 `intersci-grad`，与 skill 名一致。
