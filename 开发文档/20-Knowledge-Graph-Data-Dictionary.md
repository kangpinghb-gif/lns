# Life Navigation System — Knowledge Graph Data Dictionary

> Version: 1.0 | Status: Frozen

## 1. Purpose

定义知识图谱中所有节点的统一数据结构。AI 不思考命理，全部查阅本字典。建议拆为数据库存储。

## 2. Directory Structure

```
knowledge/: ten_gods/, five_elements/, stems/, branches/, hidden_stems/, relations/, shensha/, career/, wealth/, relationship/, health/, learning/, risk/, actions/
```

## 3. TenGod Object Schema

```
{
  id,
  code,
  name_cn,
  name_en,
  category,
  keywords,
  description,
  strength,
  weakness,
  behavior,
  career,
  wealth,
  relationship,
  health,
  learning,
  management,
  entrepreneur,
  investment,
  risk,
  action,
  modern_translation,
  prompt_template,
  embedding_keywords,
  priority,
  version
}
```

## 4. Five Element Object Schema

```
{
  element,
  traits,
  emotion,
  career,
  health,
  wealth,
  learning,
  relationship,
  behavior,
  positive,
  negative,
  actions
}
```

## 5. ShenSha Object Schema

```
{
  id,
  name,
  type,
  condition,
  positive_score,
  negative_score,
  effect,
  career,
  wealth,
  relationship,
  health,
  risk,
  action,
  priority
}
```

## 6. Relation Schema

```
{
  relation,
  display_name,
  description,
  risk,
  opportunity,
  behavior_change,
  recommended_actions
}
```

## 7. Action Library

每条建议不是 AI 编，而是知识图谱已有模板。

```
{
  id,
  category,
  description,
  applicable_conditions[],
  risk_level,
  priority
}
```

**Examples:**

- **Action001**: 学习→开始系统学习。适用于木增强、印增强、学习窗口开启。风险低，P1。
- **Action002**: 职业→完善简历。适用于职业变化窗口。风险低，P0。

Decision Engine 输出 Action ID，AI 仅渲染为自然语言。

## 8. State → Action 静态路由表

### 8.1 路由机制
采用「三维向量位掩码（Vector Bitmask）」建立静态路由表，将状态组合确定性地映射到 Action ID。

### 8.2 路由输入向量
Router_Key = [Dominant_Structure_ID] + [Energy_Level] + [Time_Dimension_Scale]

- Dominant_Structure_ID: 01(比肩)/02(劫财)/03(伤官)/04(食神)/05(正财)/06(偏财)/07(正官)/08(七杀)/09(正印)/10(偏印)
- Energy_Level: H(高)/M(中)/L(低)
- Time_Dimension_Scale: T0(日)/T1(月)/T2(年)/T3(大运)

### 8.3 MVP 前 50 条硬编码示例
```json
{
  "03_H_T0": ["Action_03", "Action_11"],
  "05_L_T1": ["Action_22", "Action_08"]
}
```
注："03_H_T0" = 伤官主导结构 + 高能量 + T0 日级 → 启动创新任务与言语安全阀模板

### 8.4 执行规则
- 每个 Router_Key 必须至少映射 1 个 Action ID
- 路由表由首席命理架构师维护
- 每次知识图谱版本更新同步审计路由表

## 9. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-29 | LNS Team | Initial frozen release |
