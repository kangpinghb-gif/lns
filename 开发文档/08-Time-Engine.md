# Life Navigation System — Time Engine

> Version: 1.0 | Status: Temporal Analysis Layer (Frozen)

## 1. Purpose

Time Engine 的职责是：在「人生状态模型」基础上，构建时间驱动的变化系统。

它回答的不是「你是谁」，而是你在不同时间尺度下如何变化。

## 2. Core Principle

Time Engine 不做预测命运。只做：

- 时间节奏分析
- 状态变化模拟
- 趋势结构表达

## 3. Input Contract

Time Engine 现在接收两套数据：用户的出生命盘状态（来自第一次 BaZi 计算），和当前时间的四柱干支（来自第二次 BaZi 计算，以当前时间为输入）。Time Engine 用当前干支与出生命盘的相互作用生成 T0/T1/T2/T3。

```json
{
  "birth_state": {
    "current_state": {},
    "capability_profile": {},
    "luck_cycles": {},
    "four_pillars": {}
  },
  "current_bazi": {
    "year_pillar": "",
    "month_pillar": "",
    "day_pillar": "",
    "hour_pillar": ""
  },
  "target_time": {
    "date": "",
    "time": "",
    "solar_term": ""
  },
  "behavior_patterns": {}
}
```

## 4. Output Contract

```json
{
  "T0": {
    "daily_state": "",
    "focus": [],
    "risk": [],
    "recommended_focus": []
  },
  "T1": {
    "monthly_trend": "",
    "opportunities": [],
    "risks": [],
    "recommended_focus": []
  },
  "T2": {
    "yearly_direction": "",
    "major_shift": [],
    "strategic_action": []
  },
  "T3": {
    "10_year_structure": "",
    "life_cycle_stage": "",
    "long_term_strategy": []
  }
}
```

## 5. Time Hierarchy System

### T0（日级）

核心问题：今天适合做什么？

输出内容：精力状态、风险提示、行动建议

### T1（月级）

核心问题：这个月的节奏是什么？

输出：机会窗口、波动周期、行动重点

### T2（年级）

核心问题：这一年人生在发生什么结构变化？

输出：结构转折点、发展方向、关键决策

### T3（大运级）

核心问题：人生长期结构是什么？

输出：10年人生轨迹、生命周期阶段、长期策略

### T-1（回顾级）

核心问题：过去的人生时段告诉我什么？

输出：已走大运回顾、关键转折点标注、路径模式识别

## 6. Time Flow Architecture

```
State Engine Output
        ↓
Luck Cycle Engine
        ↓
Temporal Mapping Engine
        ↓
Trend Detection Engine
        ↓
Opportunity Analyzer
        ↓
Risk Analyzer
        ↓
Action Generator
        ↓
Time Layer Output (T0-T3)
```

## 7. Temporal Mapping Rules

### Rule 1：时间不是预测，是变化框架

不允许：「你明天会发生X」
允许：「短期内波动增强」

### Rule 2：时间漏斗机制（宏观约束微观）

大尺度时间对小尺度时间具有自上而下的**约束投影关系**。

- T3（大运层）定义十年基调 → 作为 T2 的环境约束
- T2（年层）定义年度方向 → 作为 T1 的边界条件
- T1（月层）定义月度节奏 → 作为 T0 的上下文
- T0（日层）在 T1/T2/T3 的约束范围内进行计算

**投影规则：**
- 若 T2 标记为高风险（risk_level = high），T0 的 risk 等级不得低于 T2 的 risk_level
- 若 T3 标记为结构冲突期，T0 即使单日能量充足，输出中必须包含 T3 的风险提示
- 微观信号（T0 能量高）不得覆盖宏观信号（T2/T3 高风险）

### Rule 3：时间必须驱动行动

所有时间输出必须包含：风险、机会、行动

## 8. Daily Layer (T0)

```json
{
  "energy_state": "high / medium / low",
  "focus_area": [],
  "avoid_actions": [],
  "recommended_actions": []
}
```

## 9. Monthly Layer (T1)

```json
{
  "trend": "up / stable / down",
  "opportunities": [],
  "risks": [],
  "recommended_actions": []
}
```

## 10. Yearly Layer (T2)

```json
{
  "structural_shift": "",
  "key_transition": "",
  "strategic_focus": [],
  "avoidance_strategy": []
}
```

## 11. Ten-Year Layer (T3)

```json
{
  "life_stage": "",
  "long_term_direction": [],
  "structural_advantage": [],
  "structural_risk": [],
  "strategic_path": []
}
```

## 12. Historical Retrospective Layer (T-1)

### 12.1 Purpose
T-1 层是系统的回顾维度，与 T0/T1/T2/T3 形成完整时间闭环。它不预测未来，而是解读已走过的人生时段，帮助用户理解当前状态的形成逻辑。

### 12.2 Core Principle
T-1 不做「事后算命」。只做：已走过大运的结构化回顾、关键转折点标注、人生路径模式识别。

### 12.3 Input
{current_state, luck_cycles[completed], life_stage_history[], behavior_patterns[]}

### 12.4 Output Structure

```json
{
  "timeline": [
    {
      "period": "0-10岁",
      "luck_pillar": "甲子",
      "life_stage": "基础形成期",
      "energy_pattern": "",
      "key_theme": "",
      "structural_shift": false
    }
  ],
  "key_transitions": [],
  "repeating_patterns": [],
  "path_summary": ""
}
```

### 12.5 关键转折点标注规则

自动检测以下转折信号并在时间轴上标注：
- 大运切换点（每个10年交界）
- 五行结构突变（前后大运五行属性逆转）
- 十神关系转折（如正财运→偏财运）
- 人生阶段跨越（如路径探索期→结构建立期）

### 12.6 模式识别

对已走完的运气周期进行对比，识别：
- 相似结构重复出现的模式
- 压力/机会交替的节奏
- 能力结构与环境匹配度的变化趋势

### 12.7 路径总结

输出一句话概括：从已走完的人生时段中，识别出的核心路径特征。

### 12.8 Design Philosophy
T-1 不是为了证明系统「算得准」，而是帮助用户理解「我是怎么走到今天的」。

### 12.9 Extension (V2)
- 用户反馈校正（标记实际经历与系统分析的一致/差异）
- 多路径对比（如果当时选择了不同路径）
- 人生沙盘回放

## 13. Opportunity Detection Rules

**Rule 1：** 机会 = 状态优势 × 时间窗口

**Rule 2：** 机会不是「好运」，而是结构匹配 + 时间窗口

**Rule 3：** 机会必须可执行

## 13.5. Risk Detection Rules

风险来源：状态失衡、时间冲突、能力不匹配。

输出必须包含：风险等级、风险类型、避免策略。

## 14. Focus Generation Rules

所有时间层必须输出当前时间维度的**关注领域**（非优先级排序的行动指令）。

- T0：今日关注领域
- T1：本月关注领域
- T2：年度关注领域
- T3：十年长期关注领域

P0-P3 优先级排序由 `09-Decision-Engine.md` 统一负责。

Time Engine 的输出是 Decision Engine 的输入之一，两者不重叠。

## 16. Dependency Rule

Time Engine 依赖：State Engine、Luck Cycles (BaZi Engine)。

禁止：AI自由推导、Prompt生成时间逻辑。

## 17. Design Philosophy

Time Engine 的本质：把「命运」转化为「时间结构中的变化模型」。

## 18. System Output Principle

所有时间输出必须：可解释、可执行、可回溯。

## 19. Extension (V2)

未来扩展：实时状态更新、行为反馈修正、时间模拟器（What-if）、多路径人生模拟。
