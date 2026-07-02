# Life Navigation System — System Architecture

> Version: 1.0 | Status: Frozen Architecture

## 1. Architecture Goal

将人生导航系统拆解为可独立开发、可替换、可扩展的 AI 决策引擎系统。核心原则：每一层只做一件事。

## 2. High-Level Architecture

```
Birth Data ──┐
             ├──→ Calendar Engine (Dual-Mode) → BaZi Engine (Dual-Mode) → State Engine → Knowledge Graph
Current Time ──┘                                                                       ↓
                                                                          State Synthesizer (07A)
                                                                       ↓               ↓
                                                                  Time Engine (08)  Decision Engine (09)
                                                                       ↓               ↓
                                                                  Prompt Engine (10) → LLM / Output
```

> **Note**: Calendar Engine 和 BaZi Engine 均支持双模式：一次处理出生时间（静态命盘），一次处理当前时间（流日/流年）。两路输出分别注入下游引擎。

Full pipeline:

```
Birth Data ──┐             ┌→ Static Chart ──┐
             ├──→ Calendar ┤                  ├──→ BaZi ──→ State Engine → Knowledge Graph
Current Time ──┘           └→ Current Cycle ──┘                         ↓
                                                              State Synthesizer (07A)
                                                           ↓               ↓
                                                      Time Engine (08)  Decision Engine (09)
                                                           ↓               ↓
                                                      Prompt Engine (10) → LLM / Output

注：Caching Strategy (12A) 贯穿整个流水线，静态命盘（用户一生一次）→ Redis，年运（季→年）→ Redis TTL=365d，月运→ Redis TTL=31d，日运实时计算。
```

## 3. Layer Responsibilities

### 3.1 Calendar Engine（时间标准层）

职责：公历↔农历转换、节气计算、时区转换、DST处理、真太阳时（专业模式）

Output: `{solar_time, lunar_time, timezone, solar_term, location}`

### 3.2 BaZi Engine（命理计算层）

职责：四柱计算、十神推导、五行分布、大运/流年计算、神煞系统

Input: Calendar Engine Output

Output: `{four_pillars, ten_gods, five_elements, luck_cycles, deities}`

### 3.3 State Engine（状态建模层）

职责：将命理结构转化为人生状态模型

Output: `{current_stage, energy_level, risk_level, capability_profile, constraints}`

### 3.4 Knowledge Graph Engine（知识图谱层）

职责：命理→行为→能力→职业→风险→建议

Output: `{behavior_model, skill_model, career_mapping, risk_model, advice_template}`

### 3.5 State Synthesizer（状态合成层）

职责：合并 Knowledge Graph 输出，协调 Time Engine 和 Decision Engine 的数据流向

Output: `{synthesized_state, time_context, decision_ready}`

注：作为 Knowledge Graph 的下游扇出节点，将知识图谱输出分发至 Time Engine（08）和 Decision Engine（09）。

### 3.6 Time Engine（时间分析层）

职责：构建 T0(日)/T1(月)/T2(年)/T3(大运) 多时间尺度分析

Output: `{T0, T1, T2, T3}`

### 3.7 Decision Engine（决策层）

职责：风险排序、机会排序、行动优先级排序

Output: `{P0, P1, P2, P3}`

### 3.8 Prompt Engine（AI控制层）

职责：控制 LLM 输出、防止玄学化、强制结构化输出、注入知识图谱

### 3.9 Output Engine（输出层）

职责：多端输出（Web UI、Mobile App、API、PDF Report）

## 4. Data Flow Architecture

Full pipeline (dual-mode):

```
Birth Data ──┐             ┌→ Static Chart ──┐
             ├──→ Calendar ┤                  ├──→ BaZi ──→ State Engine → Knowledge Graph → Time Engine → Decision Engine → Prompt Engine → Output Engine → Client
Current Time ──┘           └→ Current Cycle ──┘
```

> Calendar Engine 和 BaZi Engine 分别处理出生数据（静态命盘）和当前时间（流日/流年），两路输出合并后共同注入下游引擎。

## 5. Core Data Objects

### 5.1 User Object

```json
{
  "birth_data": {
    "birth_date": "",
    "birth_time": "",
    "birth_place": {},
    "timezone": ""
  },
  "target_time": {
    "date": "YYYY-MM-DD",
    "time": "HH:MM"
  }
}
```

> **Note**: `target_time` 字段传入当前查询时间，由 Calendar Engine 和 BaZi Engine 并行处理，生成静态命盘和当前流年/流日两套结构，分别注入下游。

### 5.2 Life State Object

```json
{stage, energy, risk, capability[], constraints[]}
```

### 5.3 Timeline Object

```json
{T0, T1, T2, T3}
```

### 5.4 Decision Object

```json
{P0[], P1[], P2[], P3[]}
```

## 6. Module Dependency Rules

1. **Calendar Engine → BaZi Engine** — 唯一入口
2. **BaZi Engine → State Engine** — 不可跳过
3. **State Engine → Knowledge Graph** — 唯一映射来源
4. **Knowledge Graph → Decision Engine** — 唯一决策依据
5. **Prompt Engine** 不允许生成新知识，只能组织已有结构

## 7. System Constraints

- AI 不允许直接解释命理，必须通过 Knowledge Graph
- 所有输出必须包含时间维度
- 所有建议必须可执行
- 所有模块必须可替换（loosely coupled）

## 8. Scalability Design

支持：单用户分析、多用户并发、历史记录回溯、生命周期更新。

## 9. Performance Targets

- 单次分析 < 3s
- API响应 < 200ms（除AI）
- 支持缓存 State + Chart

## 10. Security Principle

禁止：命运恐吓、精准预测人生事件、医疗/法律级判断。

## 11. Extension Architecture (V2 Ready)

- 人生模拟器
- 职业路径预测
- 决策回溯系统
- 多用户对比分析

## 12. Architectural Philosophy

系统不是算命系统，而是**人生状态操作系统（Life Operating System）**。核心思想：**状态×时间×行动**三位一体。
