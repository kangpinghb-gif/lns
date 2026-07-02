# Life Navigation System — Knowledge Graph Engine

> Version: 2.1 | Status: Rebuilt with Ontology + Graph Model + Reasoning Chain

---

## 1. Purpose

将命理符号系统转换为可计算、可追溯、可验证的知识图谱。AI 不推理命理，所有输出基于结构化节点 + 标准化关系 + 证据链。

---

## 2. Core Principles

1. **不解释命运** — 只做映射：符号 → 行为 → 能力 → 职业 → 风险 → 建议
2. **可追溯** — 每个结论必须有完整证据链（Knowledge → Rule → Calculation → Conclusion → Confidence）
3. **禁止 AI 自由推断** — 所有映射从知识库检索，不从 Prompt 生成
4. **Graph First** — 所有知识表达为节点 + 关系，不依赖目录结构
5. **版本化** — 每个节点/关系/规则有版本和状态，支持 deprecation

---

## 3. Knowledge Graph Ontology（点 1）

### 3.1 Entity Types

```
┌─ Root（抽象基类）──────────────────────────────────┐
│  id / name / version / status / source / metadata  │
└────────────────────────────────────────────────────┘
        │
        ├── FoundationNode         L1 基础事实（天干、地支、五行、节气...）
        │     is_abstract=false
        │
        ├── RuleNode               L2 推理规则（旺衰、格局、用神...）
        │     ├─ priority / weight / conflict / applicability
        │     └─ status: draft | verified | deprecated
        │
        ├── BaZiNode               L3 命理知识
        │     ├─ TenGodNode         十神
        │     ├─ WuxingNode         五行
        │     └─ ShenshaNode        神煞
        │
        ├── ModernMappingNode      L4 现代解释映射
        │     └─ source / domain / modern_term
        │
        ├── CapabilityNode         L5 能力模型
        │     └─ level / indicators / sub_capabilities[]
        │
        ├── PersonalityNode        L6 人格模型
        │     └─ traits / matched_gods[]
        │
        ├── CareerNode             L7 职业模型
        │     └─ industry / role / skills / growth_path
        │
        ├── WealthNode             L8 财富路径
        │     └─ type / income_range / risk_level
        │
        ├── RelationshipNode       L9 关系模型
        │     └─ relation_type / strengths / risks
        │
        ├── HealthNode             L10 健康管理
        │     └─ body_parts / stress_sources / advice
        │
        ├── EventNode              L11 人生事件
        │     └─ preconditions / risk_factors / timing
        │
        ├── DecisionTemplateNode   L12 决策模板
        │     └─ question / factors / output_template
        │
        ├── ActionNode             L13 建议
        │     └─ category / conditions / priority / tracking
        │
        ├── EvidenceNode           L14 证据链
        │     └─ conclusion / confidence / chain[]
        │
        └── CaseNode               L15 案例
              └─ profile / decision / outcome / feedback
```

### 3.2 Base Attributes（所有节点继承）

```json
{
  "id": "",
  "type": "",
  "name": "",
  "name_cn": "",
  "version": "1.0.0",
  "status": "draft | verified | deprecated",
  "source": {
    "author": "",
    "reference": "",
    "applicability": "",
    "verified_by": "",
    "verified_at": ""
  },
  "metadata": {
    "confidence": 0.0,
    "completeness": 0.0,
    "verification_level": "unverified | peer_reviewed | expert_approved | empirically_validated"
  },
  "created_at": "",
  "updated_at": ""
}
```

---

## 4. Relationship Dictionary（点 2）

所有关系必须从此列表选择。**禁止随意新增**。新增需版本升级审批。

### 4.1 层级关系

| 关系 | 方向 | 语义 | 示例 |
|------|------|------|------|
| `IS_A` | → | 子类/实例 | 甲木 `IS_A` 天干 |
| `PART_OF` | → | 组成部分 | 天干 `PART_OF` 干支系统 |
| `BELONGS_TO` | → | 归属层级 | 食神 `BELONGS_TO` Layer 3 |

### 4.2 命理关系

| 关系 | 方向 | 语义 | 示例 |
|------|------|------|------|
| `SHENG` | → | 五行相生 | 木 `SHENG` 火 |
| `KE` | → | 五行相克 | 木 `KE` 土 |
| `HE` | → | 天干五合 / 地支六合 | 甲 `HE` 己 |
| `CHONG` | → | 地支六冲 | 子 `CHONG` 午 |
| `XING` | → | 地支三刑 | 寅 `XING` 巳 |
| `HAI` | → | 地支六害 | 子 `HAI` 未 |
| `HAS_HIDDEN` | → | 地支藏干 | 子 `HAS_HIDDEN` 癸 |
| `MAPS_TO` | → | 符号→行为 | 食神 `MAPS_TO` 表达能力 |
| `EXPRESSES_AS` | → | 符号→人格 | 偏印 `EXPRESSES_AS` 研究型 |

### 4.3 应用关系

| 关系 | 方向 | 语义 | 示例 |
|------|------|------|------|
| `SUPPORTS` | → | 能力支撑 | 表达能力 `SUPPORTS` 教学能力 |
| `SUITABLE_FOR` | → | 适合职业 | 创新能力 `SUITABLE_FOR` 产品经理 |
| `HAS_RISK` | → | 存在风险 | 创业 `HAS_RISK` 财务波动 |
| `REQUIRES` | → | 前置条件 | 创业 `REQUIRES` 资金储备 |
| `LEADS_TO` | → | 导致结果 | 执行力强 `LEADS_TO` 快速落地 |
| `CONTRADICTS` | → | 矛盾冲突 | 伤官 `CONTRADICTS` 正官 |
| `AMPLIFIES` | → | 相互增强 | 食神 `AMPLIFIES` 偏财 |
| `REDUCES` | → | 相互减弱 | 正印 `REDUCES` 伤官 |
| `GENERATES` | → | 产生 | 命理计算 `GENERATES` 证据 |
| `DERIVES_FROM` | → | 推导来源 | 证据 `DERIVES_FROM` 规则 |
| `REFERENCES` | → | 引用来源 | 节点 `REFERENCES` 三命通会 |

### 4.4 流程关系

| 关系 | 方向 | 语义 | 示例 |
|------|------|------|------|
| `TRIGGERS` | → | 触发动作 | 高能量 `TRIGGERS` 行动窗口 |
| `RESOLVES_TO` | → | 决策输出 | 决策模板 `RESOLVES_TO` 建议列表 |
| `FOLLOWED_BY` | → | 时间顺序 | 大运甲 `FOLLOWED_BY` 大运乙 |

### 4.5 质量关系

| 关系 | 方向 | 语义 | 示例 |
|------|------|------|------|
| `VALIDATED_BY` | → | 被验证 | 规则 `VALIDATED_BY` 专家审核 |
| `DEPRECATES` | → | 替代旧版 | 规则 v2 `DEPRECATES` 规则 v1 |

---

## 5. Rule Standardization（点 3）

每条 Rule 必须包含以下字段：

```json
{
  "id": "RULE-001",
  "type": "wang_shuai | geju | tiaohou | yongshen | ...",
  "name": "season_energy_rule",
  "name_cn": "季节旺衰判断规则",
  "version": "1.2.0",
  "status": "verified",
  "priority": 1,
  "weight": 0.8,
  "conflict": [
    {"rule_id": "RULE-017", "type": "override | conditional | mutual_exclusive", "resolution": "当条件A满足时RULE-017优先"}
  ],
  "source": {
    "author": "LNS Expert Team",
    "reference": "《子平真诠》卷三·旺衰章",
    "applicability": "仅适用于正格命盘",
    "verified_by": "首席命理架构师",
    "verified_at": "2026-06-15"
  },
  "condition": "日干生于当令之月且无破格",
  "inputs": [
    {"name": "month_branch", "type": "dizhi", "required": true},
    {"name": "day_stem", "type": "tiangan", "required": true}
  ],
  "output": {
    "energy_level": "旺 | 相 | 休 | 囚 | 死",
    "score": 80,
    "description": "日干处于当令旺地"
  },
  "exceptions": [
    {"condition": "从格", "rule_id": "RULE-099", "action": "delegate"}
  ],
  "examples": [
    {"input": {"month_branch": "寅", "day_stem": "甲"}, "output": {"energy_level": "旺", "score": 85}}
  ]
}
```

---

## 6. Evidence Standardization（点 4）

每个结论必须有 5 步链：

```
Knowledge（知识）→ Rule（规则）→ Calculation（计算）→ Conclusion（结论）→ Confidence（可信度）
```

```json
{
  "evidence_id": "EVI-20260702-001",
  "conclusion": "当前适合主动推进职业选择",
  "chain": [
    {
      "step": 1,
      "type": "knowledge",
      "source_layer": 3,
      "source_id": "TG-SS",
      "content": "食神旺则表达与创造能力强",
      "knowledge_ref": "《子平真诠》"
    },
    {
      "step": 2,
      "type": "rule",
      "rule_id": "RULE-042",
      "content": "食神生财格局，大运流年逢财星则行动窗口开启",
      "priority": 2,
      "weight": 0.8
    },
    {
      "step": 3,
      "type": "calculation",
      "engine": "State Engine",
      "input": {"day_stem": "丙", "month_branch": "寅", "current_luck": "庚午"},
      "output": {"energy_level": "H", "dominant_structure": "伤官", "risk_level": "M"},
      "formula": "energy_score = wang_shuai(dry, mb) × luck_bonus(cur_luck)"
    },
    {
      "step": 4,
      "type": "conclusion",
      "content": "当前适合主动推进职业选择",
      "recommended_actions": ["Action-003", "Action-011"]
    },
    {
      "step": 5,
      "type": "confidence",
      "score": 0.83,
      "factors": [
        {"name": "知识可信度", "score": 0.90, "source": "经典命理文献"},
        {"name": "规则准确度", "score": 0.85, "source": "专家验证"},
        {"name": "输入完整度", "score": 0.75, "source": "用户提供完整命盘"}
      ]
    }
  ]
}
```

---

## 7. Reasoning Chain（点 5）

完整推理链取代单一的 Rule 输出。

```
用户输入
    │
    ▼
┌─ L1 Foundation ───────────────┐
│  天干 → 地支 → 五行 → 阴阳 → │
│  节气 → 纳音 → 藏干 → 空亡   │
└───────────────┬───────────────┘
                │
                ▼
┌─ L2 Rules ────────────────────┐
│  旺衰 → 格局 → 十神 → 调候 → │
│  用神 → 神煞 → 大运 → 流年   │
└───────────────┬───────────────┘
                │
                ▼
┌─ L3 BaZi Knowledge ───────────┐
│  十神解读 → 五行能量 → 结构分析│
└───────────────┬───────────────┘
                │
                ▼
┌─ L4 Modern Interpretation ────┐
│  传统术语 → 现代语言映射       │
└───────────────┬───────────────┘
                │
                ▼
┌─ L5–L6 Profile ──────────────┐
│  能力评估 → 人格画像           │
└───────────────┬───────────────┘
                │
                ▼
┌─ L7–L13 Application ─────────┐
│  职业 → 财富 → 关系 → 健康 →  │
│  事件 → 决策 → 建议            │
└───────────────┬───────────────┘
                │
                ▼
┌─ L14 Evidence ───────────────┐
│  证据链组装 → 可信度计算       │
└───────────────┬───────────────┘
                │
                ▼
           最终输出
```

每条推理链在 `L14 Evidence` 阶段完成可信度汇总。最终输出附加完整链条供追溯。

---

## 8. Knowledge Source（点 6）

每个知识节点必须包含来源信息。不可追溯的知识节点不得上线。

```json
{
  "source": {
    "type": "classic_literature | expert_knowledge | empirical_data | algorithm_derived",
    "reference": "《滴天髓》卷X·章X·节X",
    "author": "刘伯温 / LNS Expert Team",
    "applicability": {
      "scope": "仅适用于子平法正格",
      "excludes": ["从格", "化格"],
      "culture": "汉文化命理体系"
    },
    "limitations": [
      "不适用于其他命理体系（紫微斗数/西洋占星）",
      "现代职业映射部分基于 2026 年中国职场数据"
    ],
    "verified_by": "首席命理架构师",
    "verified_at": "2026-07-01"
  }
}
```

---

## 9. Version & Status（点 7）

### 9.1 版本规则

```
格式：MAJOR.MINOR.PATCH
MAJOR: 架构变更 / 新增层级 / 关系类型变更
MINOR: 新增节点 / 规则调整 / 字段新增
PATCH: 修正错误 / 补充来源 / 质量分数调整
```

### 9.2 状态规则

```
draft       → 开发中，未上生产
verified    → 经专家审核，可上生产
deprecated  → 被新版本替代，但为兼容性保留
             └── 必须指定 deprecates_by（替代节点ID）
```

### 9.3 节点示例

```json
{
  "id": "TG-SS",
  "version": "2.1.0",
  "status": "verified",
  "previous_version": "1.0.0",
  "deprecates_by": null,
  "changelog": [
    {"version": "2.1.0", "date": "2026-07-02", "change": "增加财富路径映射"},
    {"version": "2.0.0", "date": "2026-06-30", "change": "重组为15级知识库"},
    {"version": "1.0.0", "date": "2026-06-29", "change": "初始版本"}
  ]
}
```

---

## 10. Quality Metadata（点 8）

### 10.1 字段定义

| 字段 | 范围 | 含义 |
|------|------|------|
| `confidence` | 0.0–1.0 | 知识准确性置信度 |
| `completeness` | 0.0–1.0 | 该节点覆盖领域的完整度 |
| `verification_level` | enum | 验证深度 |

### 10.2 Verification Levels

```
unverified                 → 未经验证
peer_reviewed              → 同行评审
expert_approved            → 专家审批
empirically_validated      → 实证验证（有用户反馈数据支持）
```

### 10.3 计算规则

- 根节点（L1 Foundation）：confidence ≥ 0.95（可精确验证的事实）
- 规则节点（L2 Rule）：confidence ≥ 0.80（经典理论，专家已验证）
- 应用节点（L5–L13）：confidence ≥ 0.65（现代映射，有实证基础）
- 新节点（draft 状态）：可低于阈值，但不可用于生产推理

---

## 11. Graph Model（点 9）

以节点 + 关系替代目录结构。所有知识表达为有向图。

### 11.1 图结构示例

```
传统写法（不推荐）：
  careers/
  ├── education/
  │   ├── primary
  │   └── teacher

Graph 写法（推荐）：
  食神 ──MAPS_TO──→ 表达能力
  表达能力 ──SUPPORTS──→ 教学能力
  教学能力 ──SUITABLE_FOR──→ 教师
  教师 ──IS_A──→ 教育行业岗位
  教育行业岗位 ──BELONGS_TO──→ Layer 7 Career
```

### 11.2 查询示例

```cypher
// 某用户食神旺，推荐什么职业？
MATCH (tg:TenGod {id: 'TG-SS'})
  -[:MAPS_TO]-> (cap:Capability)
  -[:SUPPORTS*1..2]-> (career:Career)
RETURN career.name, career.confidence
ORDER BY career.confidence DESC
```

### 11.3 可视化

```
[食神] ─MAPS_TO─→ [表达能力] ─SUPPORTS─→ [教学能力] ─SUITABLE_FOR─→ [教师]
  │                  │                        │
  ▼                  ▼                        ▼
[创造力]         [内容输出]               [产品经理]
  │                                         │
  ▼                                         ▼
[内容行业]                               [互联网行业]
```

---

## 12. Data Flow（Updated）

```
User Input
    │
    ▼
┌─ BaZi Engine ────────────────────────┐
│  排出四柱 → 大运 → 流年 → 神煞       │
└───────────────┬───────────────────────┘
                │
                ▼
┌─ State Engine ───────────────────────┐
│  计算能量 → 风险 → 阶段 → 主导结构   │
└───────────────┬───────────────────────┘
                │
                ▼
┌─ Knowledge Graph (07) ──────────────┐
│  Layer 1–3 → 基础知识与规则          │
│  Layer 4–6 → 现代映射与画像          │
│  Layer 7–13 → 应用建议               │
│  Layer 14   → 证据链组装             │
│  Layer 15   → 案例检索 (RAG)         │
└───────────────┬───────────────────────┘
                │
                ▼
┌─ State Synthesizer (07A) ───────────┐
│  融合 → 排序 → 剪枝 → 输出           │
└───────────────┬───────────────────────┘
                │
                ▼
┌─ Decision Engine ───────────────────┐
│  匹配路由 → 决策模板 → 建议列表      │
└───────────────┬───────────────────────┘
                │
                ▼
            User Output
```

---

## 13. Graph Construction Rules

1. 每新增一个节点必须指定 `type`（从 Ontology 选择）
2. 每新增一条边必须指定 `relationship`（从 Relationship Dictionary 选择）
3. 每个节点必须有 `source` 和 `metadata`
4. 每个节点在 verified 状态前不得用于生产推理
5. 一条证据链至少包含 3 步：Knowledge → Rule → Conclusion
6. 所有 deprecate 的节点必须标注替代节点

---

## 14. Design Philosophy

把命理系统变成可计算、可追溯、可验证的知识图谱。命理符号仅作为索引，输出的是有证据支撑的人类语言。

---

## 15. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-29 | LNS Team | Initial release |
| 2.0 | 2026-07-02 | LNS Team | 15-level architecture |
| **2.1** | **2026-07-02** | **LNS Team** | **Ontology + Graph Model + Relationship Dictionary + Evidence Standard + Reasoning Chain + Source/Version/Quality** |
