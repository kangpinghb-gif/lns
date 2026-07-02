# Life Navigation System — Decision Engine

> Version: 1.0 | Status: Decision Core Layer (Frozen)

## 1. Purpose
将「状态+时间+风险+机会」转化为可执行的行动优先级。是整个系统的最终收敛点：分析→结构→时间→决策→行动。

## 2. Core Principle
不解释人生。只回答一个问题：现在应该做什么？

## 3. Input Contract
{current_state, time_layers:{T0,T1,T2,T3}, risk_model, capability_profile, opportunity_model}

## 4. Output Contract
{P0[], P1[], P2[], P3[], decision_logic, priority_reasoning[]}

## 5. System Workflow
State Engine → Time Engine → Risk Aggregation → Opportunity Detection → Constraint Filtering → Priority Scoring → Decision Ranking → Action Output (P0-P3)

## 6. Decision Model

### 6.1 决策公式（核心）
```
Decision Score = (0.3 × Opportunity) - (0.4 × Risk) + (0.1 × Match) + (0.2 × Time)
```
执行红线：风控（Risk）权重强制锁定最高（0.4），践行「不制造焦虑但绝对提示风险」的底层原则。最终得分统一做归一化（0–100）处理。

### 6.2 权重规则
- 时间匹配 0.2 > 机会大小 0.3（按乘法因子实际匹配排序）
- 风险控制 0.4 > 收益潜力 0.3
- 能力匹配 0.1 > 外部机会 0.2（能力作为调节因子而非主因子）

## 7. Priority System

### P0（立即执行）
必须现在做，否则损失不可逆。时间窗口极短、高影响、高确定性。

### P1（重要任务）
影响未来1-3个月结构。中高影响、中期窗口、需要规划。

### P2（优化项）
提升效率或能力。长期价值、非紧急、可延迟。

### P3（可选探索）
兴趣或低确定性机会。低风险、不影响核心路径。

## 8. Decision Rules
1. 不做分析输出：禁止解释命理/输出状态描述/讲故事，必须直接输出行动
2. 必须排序：所有建议必须排序、分级、有优先级
3. 必须时间化：所有决策关联T0/T1/T2/T3
4. 必须可执行：禁止模糊建议（如「注意机会」），必须明确行动（如「开始准备X」）

## 9. Risk Integration Layer
高风险→降级或删除，中风险→降低优先级，低风险→正常保留。风险类型：财务风险、职业风险、情绪风险、关系风险。

## 10. Opportunity Integration Layer
机会=时间窗口×状态匹配×能力可执行性。无时间窗口→忽略，无能力匹配→降级，高风险→延迟执行。

## 11. Capability Matching System
能力匹配度=当前能力vs任务需求。高匹配→P0/P1，中匹配→P1/P2，低匹配→P2/P3。

## 12. Decision Explanation System
必须输出：状态依据、时间依据、风险依据、能力依据。

## 13. Conflict Resolution
冲突优先级：时间>风险>能力>机会。

## 14. Output Example
{P0: [立即执行任务A], P1: [重要任务B], P2: [优化任务C], P3: [探索任务D], decision_logic, priority_reasoning}

## 15. System Constraints
- 不允许输出建议理解，必须输出行动指令
- 不允许情绪化表达
- 不允许预测未来事件

## 16. Dependency Rule
Decision Engine 依赖 State Engine、Time Engine、Knowledge Graph。

## 17. Design Philosophy
把复杂人生信息压缩为可执行优先级列表。

## 18. Extension (V2)
自动任务生成器、用户行为反馈闭环、决策模拟器（What-if）、多路径人生优化系统。
