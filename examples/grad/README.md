# 研究生样例集

六份样例共享同一个人设，用来演示产物形态和判断口径：

> 研二学硕，做可穿戴生理信号与学业压力识别；距预答辩约 12 个月；
> 实验室有 Empatica E4 两套；无 GPU；目标 SCI 四区或中文核心。

## 哪些是真的

- 引用的四篇文献是真实论文，DOI 可点开核对。
- 场景约束（设备、时间、投稿目标）是常见的硕士生处境。

## 哪些是演示

- 学生、课题进展、实验结果、时间安排均为教学示例，不是真实研究数据。
- 文中的"初步结果""基线已跑通"等描述仅用于展示产物结构，**不要引用为研究证据**。

## 怎么用

1. 找到最接近你当前任务的一份，复制结构，替换成自己的内容。
2. 删掉用不到的行，保持一页。
3. 交付前跑校验：

| 文件 | 类型参数 |
| :--- | :--- |
| `topic_memo.md` | `--type memo` |
| `proposal_onepager.md` | `--type proposal` |
| `literature_matrix.md` | `--type matrix` |
| `reading_card.md` | `--type reading` |
| `experiment_card.md` | `--type experiment` |
| `meeting_outline.md` | `--type meeting` |

```bash
# 在 skill 目录下
python scripts/validate_grad.py --input examples/grad/topic_memo.md --type memo

# 在任意目录（<skill-dir> 为加载时显示的 skill 基目录）
python "<skill-dir>/scripts/validate_grad.py" --input "<skill-dir>/examples/grad/topic_memo.md" --type memo
```

硬失败必须改；警告能解释就保留。

> 本目录样例由 AI 辅助整理，引用与数据请自行核验；不替代导师意见与学校规范。
