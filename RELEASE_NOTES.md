# v5.0.0 发布说明

> 这是 **InterSci-Grad** 的第一个研究生版本：从"给立项者看的十章尽调报告"，
> 转向"研究生每天能用的科研副驾"。

## 这次最重要的变化

1. **默认一页行动备忘**：一句话判断 + 三条路 + 今天/本周/两周动作，不再一上来给十章。
2. **七种工作流**：进度体检、选题、文献、开题/中期/答辩、实验、写作/投稿、组会/导师沟通。
3. **判断标准可执行**：三闸口（新颖性/可行性/时间）、四种合法创新、最小可发表单元（MPU）。
4. **九套产物模板**：选题卡、开题一页纸、文献矩阵、单篇精读卡、实验设计卡、组会提纲、周报、选刊表、审稿回复表。
5. **诚实与引用规则**：三级标签、引用核验 SOP、禁止话术、AI 使用边界；不编造、不代写、不承诺发表。
6. **轻校验器**：`validate_grad.py` 十条检查，纯标准库、离线、退出码 0/1/2。
7. **旧版保留**：十章产业尽调、证据计分、21 项校验器和旧脚本全部还在，入口见 `references/legacy-rd-engine.md`。

## 安装（DeepSeek Harness）

```bash
# 用户级：所有项目可用
mkdir -p ~/.dsh/skills/intersci-grad
cp -r SKILL.md references scripts examples README.md LICENSE CHANGELOG.md DISTRIBUTION.md SECURITY.md RELEASE_NOTES.md EXECUTION_CHECKLIST.md ~/.dsh/skills/intersci-grad/
```

Windows 用 `robocopy` 或直接解压 zip 到 `%DSH_HOME%\skills\intersci-grad`。

**不需要 API Key。** 核心功能全部本地离线。

## 包内有什么

```text
intersci-grad/
├── SKILL.md
├── README.md
├── DISTRIBUTION.md
├── SECURITY.md
├── RELEASE_NOTES.md
├── EXECUTION_CHECKLIST.md
├── CHANGELOG.md
├── references/
├── scripts/
└── examples/grad/
```

## 升级与兼容

- 从 4.x 升级：**输出结构变了**。4.x 的十章简报仍可通过 `references/legacy-rd-engine.md` 使用，但不要和研究生模板混用。
- 从 5.x 小版本升级：覆盖同名目录即可；DSH watcher 会自动刷新，必要时新开会话。
- Python >= 3.8；核心功能零第三方依赖。

## 验证

```bash
python scripts/check_consistency.py
python -m pytest -q
python scripts/make_release.py --check-only
```

当前基线：165 条测试（离线 162 通过 + 3 个实网用例跳过）；六份研究生样例全部通过 `validate_grad.py`；发布包密钥扫描 0 命中。

## 校验和

Release 附件包含 `SHA256SUMS.txt`。下载后先校验再解压。

## 许可

MIT。引用第三方文献/数据时请保留出处与许可。
