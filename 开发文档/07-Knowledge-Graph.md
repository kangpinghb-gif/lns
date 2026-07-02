# Life Navigation System — Knowledge Graph Engine

> Version: 1.0 | Status: Semantic Core Layer (Frozen)

## 1. Purpose
将命理符号系统转换为人类可理解的行为与决策模型。是整个LNS系统的语义转换中枢。

## 2. Core Principle
不解释命运。只做映射：命理符号→行为模式→能力结构→职业→风险→建议。

## 3. Input Contract
From BaZi Engine: {four_pillars, ten_gods, five_elements, hidden_stems, luck_cycles}

## 4. Output Contract
{behavior_model[], capability_model[], career_mapping[], risk_model[], advice_templates[]}

## 5. Knowledge Graph Structure

### 5.1 十神→行为模型

**比肩**
- behavior: 独立决策, 抗拒控制, 自主执行
- capability: 执行力, 自驱能力
- career: 创业, 自由职业, 项目负责人
- risk: 孤立决策, 人际冲突
- advice: 适合主导型任务，但需强化协作能力

**劫财**
- behavior: 快速行动, 资源竞争, 高风险决策
- capability: 执行突破, 机会捕捉
- career: 销售, 投资, 创业合伙
- risk: 冲动决策, 财务波动
- advice: 适合高频行动，但必须强化风险控制

**食神**
- behavior: 稳定输出, 创造表达, 内容生产
- capability: 内容能力, 创造能力
- career: 内容创作, 教育, 产品设计
- risk: 过度舒适区
- advice: 适合长期输出型路径

**伤官**
- behavior: 挑战规则, 创新表达, 强主观性
- capability: 创新能力, 表达能力
- career: 创业, 创意行业, 科技创新
- risk: 冲突管理弱
- advice: 适合创新，但需结构约束

**正财**
- behavior: 稳定积累, 长期规划
- capability: 财务管理, 资源规划
- career: 金融, 运营, 管理
- risk: 增长缓慢
- advice: 适合长期稳定路径

**偏财**
- behavior: 机会捕捉, 灵活决策
- capability: 商业嗅觉, 资源整合
- career: 投资, 贸易, 副业
- risk: 波动性高
- advice: 适合机会驱动型路径

### 6. Five Elements → Capability System

**木（成长系统）**
- capability: 学习能力, 成长能力, 扩展能力
- behavior: 持续成长, 吸收信息
- career: 教育, 产品成长, 培训
- risk: 方向分散

**火（表达系统）**
- capability: 表达能力, 影响力
- behavior: 外向表达, 传播信息
- career: 媒体, 营销, 内容行业
- risk: 情绪波动

**土（结构系统）**
- capability: 稳定性, 结构能力
- behavior: 系统化思考, 长期执行
- career: 管理, 运营
- risk: 保守

**金（规则系统）**
- capability: 规则能力, 分析能力
- behavior: 理性判断, 标准执行
- career: 金融, 法律, 审计
- risk: 过度理性

**水（流动系统）**
- capability: 适应能力, 信息整合
- behavior: 灵活变化, 跨领域整合
- career: 咨询, 互联网, 跨界
- risk: 方向不稳定

### 7. Hidden Stems → 潜在行为系统
- {zi: behavior=信息敏感, risk=情绪波动}
- {chou: behavior=稳定执行, risk=固化结构}

### 8. Career Mapping Layer
- {startup: [伤官, 偏财]}
- {stable_job: [正财, 正官]}
- {creative: [食神, 火]}
- {technical: [金, 水]}
- {management: [土, 正官]}

### 9. Risk Model Layer
{financial_risk[], career_risk[], emotional_risk[], relationship_risk[]}

### 10. Advice Template System
状态判断 → 行为解释 → 风险提示 → 行动建议

### 11. Graph Construction Rules
1. 所有命理符号必须映射为行为
2. 禁止解释命运，必须解释行为结构
3. 所有职业映射必须基于行为，而不是符号
4. 风险必须来自结构冲突，而不是预测

## 12. Dependency Rule

### 12.1 输入来源
Knowledge Graph 的输入来源修正为：**State Engine Output**（非 BaZi Engine）。

修正原因：知识图谱的语义映射（十神→行为、五行→能力、神煞→状态）需要依赖 State Engine 已经计算好的状态化数据（能量等级、风险等级、人生阶段），而非原始的 BaZi 命盘符号。

### 12.2 数据流
```
BaZi Engine → State Engine → Knowledge Graph (07)
                                  ↓
                           State Synthesizer (07A)
                                  ↓
                           Time / Decision Engine
```

### 12.3 输入合同（更新）
```json
{
  "four_pillars": {},
  "ten_gods": {},
  "five_elements": {},
  "hidden_stems": {},
  "luck_cycles": [],
  "state_context": {
    "current_stage": "",
    "energy_level": "",
    "risk_level": "",
    "dominant_structure": ""
  }
}
```

### 12.4 禁止项
- 禁止 AI 自由生成映射
- 禁止 Prompt 推断语义
- 禁止逆向修改 BaZi Engine 或 State Engine 的输出

### 13. Design Philosophy
把命理系统变成人类行为数据库。

### 14. Extension (V2)
行业知识图谱（金融/创业/职业）、用户行为反馈修正、AI自动优化图谱权重。
