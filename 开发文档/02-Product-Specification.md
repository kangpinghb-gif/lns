# Life Navigation System — Product Specification

> Version: 1.0 | Status: Frozen Spec

## 1. Product Definition
Life Navigation System (LNS) 是一个基于八字与时间建模的人生决策系统。核心不是预测未来，而是将用户人生转化为「状态 + 时间 + 行动」的结构化导航系统。

## 2. Core Product Loop
输入出生信息 → 生成人生状态模型 → 生成时间结构 (T0-T3) → 生成能力与风险结构 → 生成行动建议 (P0-P3) → 持续对话与导航更新

## 3. Core Features (V1 Frozen)

### 3.1 用户输入系统
- 出生日期（必填）
- 出生时间（必填）
- 出生地点（必填）
不允许缺失。

### 3.2 人生状态总览 (Life State Dashboard)
展示：当前人生阶段、能力结构、风险结构、当前趋势、当前建议。系统首页核心页面。

### 3.3 时间导航系统 (Time Navigation)
- T0（日）：今日状态、今日行动建议
- T1（月）：本月趋势、节奏调整建议
- T2（年）：年度发展方向、长期目标建议
- T3（大运）：10年人生结构、长期变化趋势

### 3.4 行动建议系统 (Action System)
- P0：立即执行
- P1：重要任务
- P2：优化建议
- P3：可选探索
禁止无优先级建议。

### 3.5 AI问答系统 (Navigator Chat)
AI 必须基于状态模型、时间轴、知识图谱回答。禁止自由发挥。

### 3.6 人生分析报告 (Report System)
日报、月报、年报、大运报告。格式必须结构化。

### 3.7 历史导航系统（Historical Navigation）

支持以时间轴形式回顾已走过的人生时段。

**核心功能：**
- 已走大运周期展示（每个10年周期的主题、结构、能量特征）
- 关键转折点标注（大运切换、人生阶段跨越、五行结构突变）
- 人生路径总览（从出生到现在的结构化回顾）
- 模式识别（跨周期重复出现的结构相似性）

**用途：**
- 用户理解当前状态的形成逻辑
- 辅助决策：过去相似结构的应对经验
- 路径感知：从「我在哪」延伸到「我怎么到这里的」

**设计原则：**
- 不做事后预测验证，只做结构化回顾
- 标注而非判断（标注转折点，不说好坏）
- 回顾服务于当前决策，不沉溺于过去

## 4. Page Structure (UI信息架构)
- 首页：当前人生状态、当前阶段、当前建议、快速进入导航
- 人生总览：状态模型、能力结构、风险结构
- 时间导航：T0/T1/T2/T3
- 历史导航：人生路径回顾、关键转折点
- AI问答：聊天式导航
- 报告中心：周期报告生成
- 专业模式：八字显示、完整命理结构（仅高级用户）

## 5. System Output Rules
必须包含：当前状态、时间分析、行动建议、原因解释。禁止：吉/凶、宿命论、单点结论、无行动输出。

## 6. Data Flow Architecture
User Input → Calendar Engine → BaZi Engine → State Engine → Knowledge Graph → Time Engine → Decision Engine → Prompt Engine → Output Engine

## 7. Core Entities
- User: birth_date, birth_time, birth_place, timezone
- State: current_stage, energy_level, risk_level, capability_profile
- Timeline: T0, T1, T2, T3
- Action: priority, description, urgency

## 8. Business Logic Rules
1. 所有分析基于状态模型，不是文本生成
2. 所有命理符号通过 Knowledge Graph 转换
3. 所有建议必须落到行动
4. 所有输出必须具有时间维度
5. AI不能自由解释命理

## 9. Personalization Rules
允许：多轮对话、状态更新、历史记录、周期回顾。禁止：改变历史命盘、随机解释变化。

## 10. Performance Requirements
实时分析 <3s、多轮问答、报告生成、状态缓存。

## 11. Product Boundaries
明确不做：算命娱乐化、风水推荐、吉祥物分析、姓名评分、黄历择日。

## 12. Success Criteria
用户能够：理解自己当前状态、理解未来趋势、获得行动建议、形成长期规划。

## 13. Version Scope (V1)
单用户分析、基础时间轴、基础知识图谱、AI问答、报告系统。

## 14. V2 Direction
多用户画像对比、职业路径推荐、人生模拟器、决策回溯系统。
