# Life Navigation System (LNS) — 文档索引

> 版本：v1.0.1-Execution | 状态：冻结

---

## 文档结构总览

| 编号 | 文档 | 内容 | 状态 |
|------|------|------|------|
| 00A | ADR | 架构决策记录（10条不可更改的核心决策，含夜子时/视觉边界） | ✔ |
| 00 | README | 产品世界观、核心理念 | ✔ |
| 01 | Developer Constitution | 开发宪法（最高原则） | ✔ |
| 02 | Product Specification | 产品规范（行为冻结） | ✔ |
| 03 | System Architecture | 系统架构（工程结构冻结） | ✔ |
| 04 | Calendar Engine | 时间标准化底座 | ✔ |
| 05 | BaZi Engine | 命理计算核心层 | ✔ |
| 06 | State Engine | 人生状态建模引擎 | ✔ |
| 07 | Knowledge Graph | 语义转换中枢 | ✔ |
| 07A | State Synthesizer | KG冲突消解与权重归一化（追加冻结） | ✔ |
| 08 | Time Engine | 时间分析系统（T-1/T0-T3） | ✔ |
| 09 | Decision Engine | 决策引擎（行动优先级） | ✔ |
| 10 | Prompt Engine | AI控制层（Prompt架构/约束/模板） | ✔ |
| 11 | API Design | 后端接口设计 | ✔ |
| 12 | Database Design | 数据持久化设计（含版本断代） | ✔ |
| 12A | Caching Strategy | 缓存策略（5层数据分类/Short-Circuit） | ✔ |
| 13 | Frontend Spec | 前端规范 | ✔ |
| 14 | UI/UX Guideline | 设计系统规范 | ✔ |
| 15 | System Orchestration | 系统编排与调用链 | ✔ |
| 16 | Product Definition | 产品定义与商业定位 | ✔ |
| 17 | Output Specification | 统一输出Schema（页面/API/AI/报告） | ✔ |
| 18 | Language Specification | 产品语言规范（命理→现代翻译） | ✔ |
| 19 | Prompt Library | Prompt模板库（12种场景，含实体文件） | ✔ |
| 20 | Knowledge Graph Data Dict | 知识图谱数据字典 | ✔ |
| 21 | Testing Specification | 测试规范（含Golden Dataset基准） | ✔ |
| 22 | Deployment Guide | 部署指南 | ✔ |
| 23 | Security & Compliance | 安全与合规 | ✔ |
| 24 | Development Roadmap | 开发路线图（4阶段） | ✔ |
| 25 | Algorithm Cookbook | 算法速查手册（工程黑洞/逻辑悖论/合规固化） | ✔ |

---

## 模块依赖关系

```
User Input
  ↓
Calendar Engine (04)  ← 独立，最底层
  ↓
BaZi Engine (05)     ← 纯规则计算，无AI
  ↓
State Engine (06)     ← 命盘 → 人生状态
  ↓
Knowledge Graph (07)  ← 符号 → 行为/能力/职业/风险/建议
  ↓
State Synthesizer (07A) ← 冲突消解、权重归一化
  ↓
Time Engine (08)      ← T-1/T0/T1/T2/T3 分析
  ↓
Decision Engine (09)  ← P0-P3 优先级排序
  ↓
Prompt Engine (10)    ← AI控制与结构化输出
  ↓
LLM / Output
```

---

## 核心数据流

```
输入 → Calendar → BaZi → State → Knowledge Graph → Time → Decision → Prompt → LLM → Output
```

---

## 文档完成状态

所有 28 份文档（00A, 00–25, 07A, 12A）已全部完成并冻结。文档体系已闭合。

---

## 补充目录

| 路径 | 内容 | 说明 |
|------|------|------|
| `prompts/` | Prompt实体文件 | daily.md, career.md, chat.md, monthly.md, wealth.md, relationship.md, **retrospective.md** |
| `knowledge/` | 知识图谱JSON数据（V1） | 十神/五行/神煞/行动库，Git管理，Redis缓存 |
