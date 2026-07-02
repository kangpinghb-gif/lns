# Life Navigation System — System Orchestration

> Version: 1.0 | Status: System Integration Layer (Frozen)

## 1. Purpose
将所有独立引擎（Calendar/BaZi/State/Time/Decision/Prompt）串联为一个完整人生计算系统。定义系统启动顺序、数据流路径、调用关系、生命周期。

## 2. Core Principle
系统不是模块集合，而是一个从时间输入到决策输出的闭环系统。

## 3. End-to-End Flow

```
                    ┌─→ Calendar Engine (Birth) ─→ BaZi Engine (Birth) ─→ Static Chart ──┐
User Input ─→ Split ├─→ Calendar Engine (Target) ─→ BaZi Engine (Target) ─→ Current Cycle ─┼─→ State Engine → ...
                    └─→ target_time ──────────────────────────────────────────────────────┘
```

The pipeline splits at entry: `birth_data` flows through Calendar Engine (Birth) → BaZi Engine (Birth) to produce the **Static Chart** (lifelong four pillars, ten gods, five elements, luck cycles), while `target_time` flows through Calendar Engine (Target) → BaZi Engine (Target) to produce the **Current Cycle** (current year/month/day/hour stems & branches). Both outputs merge at the State Engine entry point, then continue through KG → Time → Decision → Prompt → AI Response.

## 4. System Boot Sequence

> **Note:** Steps 2 and 3 execute in **dual mode** — once for birth data (static chart) and once for target time (current cycle). See §4.1 below.

Step 1: User Initialization (birth_date + birth_time + location + target_time)
Step 2: Calendar Initialization (solar→lunar→solar term→timezone) — runs for birth_data and target_time
Step 3: BaZi Construction (four pillars + ten gods + five elements + luck cycles) — runs for birth_data and target_time
Step 4: State Construction (behavior model + capability profile + risk structure + life stage)
Step 5: Knowledge Graph Mapping (symbol→behavior→career→risk→advice)
Step 6: Time Layer Generation (T0/T1/T2/T3)
Step 7: Decision Generation (P0/P1/P2/P3 ranking)
Step 8: Prompt Assembly (structured data→LLM prompt)
Step 9: AI Output (final structured response)

### 4.1 Dual-Mode Execution

Calendar Engine 和 BaZi Engine 在每次请求中执行两次：

**第一次（Birth Mode）：** 以 `birth_data` 为输入，计算用户静态命盘（四柱、十神、五行、大运）。结果缓存至 Redis，每天仅计算一次。

**第二次（Target Mode）：** 以 `target_time` 为输入，计算当前时间的四柱干支（流年/流月/流日/流时）。每次请求重新计算。

两路输出在 State Engine 入口合并。

### 4.2 State Synthesizer Position

Knowledge Graph 输出后，数据流经 State Synthesizer 进行冲突消解与权重归一化，再分发给 Time Engine 和 Decision Engine。

```
Knowledge Graph (07)
    ↓
State Synthesizer (07A)  ← 冲突消解、权重归一化
    ↓
Time Engine (08)        Decision Engine (09)
    ↓                      ↓
Prompt Engine (10)  →  LLM / Output
```

## 5. Data Pipeline Architecture
INPUT → CALENDAR ENGINE → BAZI ENGINE → STATE ENGINE → KNOWLEDGE GRAPH → STATE SYNTHESIZER → TIME ENGINE → DECISION ENGINE → PROMPT ENGINE → LLM → OUTPUT

## 6. Real-Time Interaction Flow (Chat Mode)
Step 1: User asks question (e.g., 我适合换工作吗？)
Step 2: System calls State Engine (current capability) + Time Engine (current window) + Decision Engine (action)
Step 3: Prompt Engine assembles: current state + time + risk + opportunity + user question
Step 4: LLM outputs: structured answer + P0-P3 suggestions + action path

## 7. System States
State 1: Initialization（用户首次进入系统）
State 2: Analysis（生成命盘+状态）
State 3: Navigation（提供时间+决策）
State 4: Execution（用户执行建议）
State 5: Feedback Loop（记录结果→反哺系统）

## 8. Feedback Loop System
Decision → User Action → Outcome → Feedback → State Update。
目的：修正行为模型、优化建议权重、提升未来决策准确性。

## 9. System Boundaries
允许：结构化分析、行动建议、时间导航。
禁止：命运确定性、宿命论、情绪操控。

## 10. Module Independence Rules
1. Calendar Engine ≠ BaZi Engine
2. State Engine 不可反推命盘
3. Decision Engine 不可修改 State
4. Prompt Engine 不可生成逻辑，只能组织逻辑

## 11. Failure Handling System
Fail Case 1: Calendar Error → fallback to cached calendar data
Fail Case 2: BaZi Error → regenerate from Calendar Engine
Fail Case 3: Decision Conflict → prioritize Time Engine

## 12. Performance Architecture
End-to-end <3s (non-AI cache hit), AI response <5s, Decision generation <500ms。

## 13. Scalability Design
支持：单用户系统、多用户并发、企业批量分析、API调用扩展。

## 14. Observability System
必须记录：输入数据、中间状态、决策输出、用户反馈。

## 15. System Philosophy
把人生时间流转化为可计算决策系统。

## 16. Extension (V2)
多人生对比系统、AI模拟人生路径、决策回放系统、人生沙盘模拟器。

## 17. Historical Retrospective Flow

### 17.1 Purpose
提供以回顾为主体的系统调用路径，用户通过历史导航入口进入。

### 17.2 System Boot Sequence

Step 1: User enters Historical Navigation
Step 2: System loads completed luck cycles from BaZi Engine
Step 3: Time Engine generates T-1 (Historical Layer)
Step 4: Pattern Detection Engine analyzes cross-period patterns
Step 5: Frontend renders horizontal timeline with annotations
Step 6: User clicks period → loads that period's detailed state

### 17.3 Data Flow
```
Historical Navigation Entry
    ↓
BaZi Engine (completed luck cycles)
    ↓
Time Engine (T-1 generation)
    ↓
State Engine (historical state reconstruction)
    ↓
Pattern Detection
    ↓
Frontend Timeline Rendering
```

### 17.4 Key Difference from Standard Flow
- 不经过 Decision Engine（回顾不生成新决策）
- 不经过 Prompt Engine（回顾是结构化数据展示，非AI对话）
- 以 BaZi Engine + Time Engine 为主

### 17.5 System State
State: Retrospection
定义：用户处于历史回顾模式，系统只读历史数据，不生成新决策。
