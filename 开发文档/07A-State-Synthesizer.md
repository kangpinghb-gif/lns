# Life Navigation System — State Synthesizer

> Version: 1.0 | Status: Core Integration Layer (追加冻结)

## 1. Purpose
State Synthesizer 位于 Knowledge Graph 与 Time Engine / Decision Engine 之间。它的职责是：对 KG 输出的多重符号映射进行**权重归一化与冲突消解**，输出一份内部逻辑自洽的合成状态对象。

## 2. Why Needed
知识图谱的映射是 1:1 的（一个符号→一组标签）。但真实命盘中十神是复合出现的（如正官+伤官同时强旺），导致 KG 输出包含完全矛盾的标签（「顺从规则」+「打破规则」）。必须有一层代码逻辑消解这些矛盾，否则 Prompt Engine 收到的数据是自相矛盾的。

## 3. Input Contract
```json
{
  "ten_gods": {
    "dominant": ["zhengguan", "shangguan"],
    "weights": {"zhengguan": 0.6, "shangguan": 0.4, ...}
  },
  "five_elements": {
    "dominant": ["fire", "metal"],
    "distribution": {"fire": 3, "metal": 2, ...}
  },
  "raw_kg_behavior": [],
  "raw_kg_career": [],
  "raw_kg_risk": []
}
```

## 4. Conflict Detection & Resolution Rules

### 4.1 十神矛盾检测
检测以下已知的冲突对同时出现时触发消解：
| 冲突对 | 冲突类型 | 消解策略 |
|--------|---------|---------|
| 正官 + 伤官 | 规则型 vs 突破型 | 按命中率权重分配，主导结构做基调，次结构做补充注明 |
| 正印 + 偏印 | 传统型 vs 独创型 | 按五行环境选择，木火环境偏印优先，土金环境正印优先 |
| 正财 + 偏财 | 保守型 vs 机会型 | 若五行中土金旺则正财优先，木火旺则偏财优先 |
| 比肩 + 劫财 | 独立型 vs 竞争型 | 按 energy_level 判断：high→劫财优先，low→比肩优先 |

### 4.2 消解算法

```python
def resolve_ten_god_conflict(weights, five_elements, energy):
    """
    核心消解函数。返回合成后的行为标签集合。
    算法：
    1. 计算各十神的命中率权重占比
    2. 对冲突对，按消解策略选择主导结构
    3. 主导结构标签占输出的 70%，次结构标签占 30%
    4. 风险标签取冲突双方的并集（宁多勿漏）
    5. 输出 deduplicated 标签数组
    """
```

### 4.3 输出规则
- 每个维度（behavior/career/risk）最多保留 5 个标签
- 冲突消解后标签不可自相矛盾
- 消解日志写入 `synthesizer_log` 表用于审计

## 5. Output Contract
```json
{
  "synthesized_behavior": ["标签1", "标签2"],
  "synthesized_career": ["职业A", "职业B"],
  "synthesized_risk": ["风险X", "风险Y"],
  "dominant_profile": "规则突破混合型",
  "confidence_score": 0.85,
  "conflict_log": [
    {"pair": "zhengguan+shangguan", "strategy": "权重分配", "resolution": "正官70%主导+伤官30%补充"}
  ]
}
```

## 6. Position in Pipeline
```
Knowledge Graph (07)
    ↓
State Synthesizer (07A)  ← 新增
    ↓
Time Engine (08) / Decision Engine (09)
```

## 7. Dependency Rule
State Synthesizer 依赖 Knowledge Graph 的输出为唯一输入源。它只做代码逻辑运算，不调用 LLM。

## 8. Extension (V2)
- 权重自适应（用户反馈数据训练）
- 冲突数据库自动扩展
- 多流派消解策略支持

---
