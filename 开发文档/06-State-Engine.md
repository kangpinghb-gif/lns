# Life Navigation System — State Engine

> Version: 1.0 | Status: Core Interpretation Layer (Frozen)

## 1. Purpose
将 BaZi Engine 输出的结构化命盘数据，转换为人生状态模型（Life State Model）。从「计算结果」到「人类状态」的转换层。

## 2. Core Principle
State Engine 不做预测。只做结构化解释：状态、能力、风险、阶段、趋势。

## 3. Input Contract
从 BaZi Engine 接收 {four_pillars, ten_gods, five_elements, luck_cycles, deities}

其中 `luck_cycles` 包含：
- `ten_year_cycles`: [{age_range: "0-10", pillar: "甲子"}]
- `start_age`: 用户的实际起运年龄（大运起始岁数）

## 4. Output Contract
{current_state: {stage, energy_level, risk_level, dominant_structure, constraints, **luck_cycle_stage**, **stage_derivation**: "age_based|luck_based"}, capability_profile[], behavior_patterns[], environment_tendency[], development_direction[], **luck_cycle_theme**: []}

## 5. System Workflow
BaZi Engine Output → Element Balance Analysis → Ten Gods Pattern Analysis → Structural Dominance Detection → Life Stage Mapping → Risk Pattern Extraction → Capability Modeling → State Assembly

## 6. Life Stage System

### 6.1 基本原则
生命周期阶段的划分以 **大运起运年龄为锚点**，而非固定物理年龄。物理年龄边界仅作为无大运数据时的降级默认值。

### 6.2 起运年龄规则
```python
def get_life_stage(age, luck_cycles):
    \"\"\"
    1. 从 luck_cycles 中获取用户的实际起运年龄 start_age
    2. 若 start_age 存在，每个大运周期（10年）为一个 stage 单位：
       - 第 1 个大运：基础塑造期
       - 第 2 个大运：发展探索期
       - 第 3 个大运：结构建立期
       - 第 4 个大运：稳定发展期
       - 第 5 个大运起：成熟优化期
    3. 计算用户当前所在的大运周期索引 = floor((age - start_age) / 10)
    4. 根据索引确定当前人生阶段
    5. 若起运年龄不可用（start_age 缺失），降级为物理年龄默认值
    \"\"\"
```

### 6.3 物理年龄降级默认值（仅当起运年龄缺失时）
0-12=基础形成期, 13-18=性格塑造期, 19-25=路径探索期, 26-35=结构建立期, 36-50=稳定发展期, 50+=收敛优化期。

### 6.4 Stage Mapping Rule
根据十神结构、五行强弱、大运趋势对以上基础划分进行修正。修正优先于默认划分。

### 6.5 Luck Cycle Theme
State Engine 从大运干支推导每个大运周期的语义主题（如「甲子」→「生长积累期」），替代原 BaZi Engine 中的 `theme` 字段。BaZi Engine 不再输出语义层数据。

## 7. Energy Model（能量模型）
{high: 行动驱动型, medium: 平衡型, low: 内收型}。火/木旺→高能量，土平衡→中能量，金/水偏弱→内收型。

## 8. Risk Model（风险结构）
风险来源：五行失衡、十神冲突、大运压制、结构过载。输出：{financial_risk, relationship_risk, career_risk, emotional_risk}

## 9. Capability Model（能力模型）
六种能力分类：执行能力、思考能力、创造能力、社交能力、结构能力、风险控制能力。映射基于十神结构、五行主导、日主强弱。

## 10. Behavioral Patterns（行为模式）
示例：高执行低规划、强表达型、长期主义型、风险驱动型、稳定积累型、机会捕捉型。

## 11. Environment Tendency（环境倾向）
定义：用户更容易适应或失败的环境类型。包括竞争环境、稳定环境、高变化环境、资源密集环境、规则密集环境。

## 12. Development Direction（发展方向）
输出：{recommended_direction[], avoid_direction[], optimal_environment[]}

## 13. Pattern Detection Rules
- 五行主导：木→成长导向，火→表达导向，土→稳定导向，金→规则导向，水→流动导向
- 十神主导：比劫→自主驱动，食伤→输出驱动，财→资源驱动，官杀→规则驱动，印→支撑驱动
- 结构冲突：多系统冲突→高风险状态，单系统极端→极化状态

## 14. Output Rules
必须输出当前状态、能力结构、风险结构、行为模式、发展方向。禁止吉凶判断、命运结论、玄学语言。

## 15. Dependency Rule
State Engine 必须依赖 BaZi Engine Output ONLY。禁止Calendar Engine、AI直接推导、Prompt输入。

## 16. Design Philosophy
把命盘翻译成人类可以理解的心理与行为结构。

## 17. Extension (V2)
多人格状态模型、动态状态更新、行为预测模型、用户反馈修正系统。
