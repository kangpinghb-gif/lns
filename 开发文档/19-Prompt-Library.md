# Life Navigation System — Prompt Library

> Version: 1.0 | Status: Frozen

## 1. Purpose
Prompt Library 是 Prompt Engine 使用的模板库。每个 Prompt 包含：Role、Task、Input、Knowledge、Constraints、Output、Examples。

## 2. Structure
/prompts/: career.md, wealth.md, relationship.md, health.md, learning.md, entrepreneur.md, investment.md, daily.md, monthly.md, yearly.md, report.md, chat.md

## 3. Prompt Template
每个 Prompt 固定结构：
1. Role — AI 身份
2. Task — 任务描述
3. Input — 输入数据（State/Time/Decision/Knowledge Graph）
4. Knowledge — 知识图谱注入
5. Constraints — 约束规则
6. Output — 输出格式
7. Examples — 示例

## 3.1 Output Language Rule

Prompt 模板必须采用双轨语言机制：

- Role 层：AI 是「懂现代决策的命理顾问」，不是冷冰冰的数据说明器。
- Output 层：默认先输出「命理锚点」，再进入现代解读。
- 标题/首次展示：允许命理术语 + 括号注释现代含义。
- 正文：产品语言为主，命理术语只作为依据。
- 行动建议：纯产品语言，不出现命理术语。
- 专业模式：允许完整命理术语，无需翻译。

## 4. Example: Career Prompt
读取 State → Time → Decision → Knowledge → 输出职业建议。

## 5. Design Rule
Codex 直接读取 Prompt 文件，不经过 AI 推理。
