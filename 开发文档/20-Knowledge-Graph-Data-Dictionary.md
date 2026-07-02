# Life Navigation System — Knowledge Graph Data Dictionary

> Version: 2.1 | Status: Rebuilt with Ontology Schemas + Relationship Dictionary + Evidence Format

## 1. Purpose

定义知识图谱中所有节点的统一数据结构、关系类型和质量标准。供数据库 Schema 设计、API 开发和 ETL 管线使用。

---

## 2. Base Schema（所有节点继承）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/base-node",
  "type": "object",
  "properties": {
    "id":              {"type": "string", "pattern": "^[A-Z]+-[0-9]{3,}$"},
    "type":            {"$ref": "#/definitions/EntityType"},
    "name":            {"type": "string"},
    "name_cn":         {"type": "string"},
    "version":         {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$", "default": "1.0.0"},
    "status":          {"$ref": "#/definitions/Status"},
    "source":          {"$ref": "#/definitions/Source"},
    "metadata":        {"$ref": "#/definitions/Metadata"},
    "relationships":   {"type": "array", "items": {"$ref": "#/definitions/Relationship"}},
    "created_at":      {"type": "string", "format": "date-time"},
    "updated_at":      {"type": "string", "format": "date-time"}
  },
  "required": ["id", "type", "name", "status", "source", "metadata"],
  "definitions": {
    "EntityType": {
      "type": "string",
      "enum": [
        "Foundation", "Rule", "TenGod", "Wuxing", "Shensha",
        "ModernMapping", "Capability", "Personality", "Career",
        "Wealth", "Relationship", "Health", "Event",
        "DecisionTemplate", "Action", "Evidence", "Case"
      ]
    },
    "Status": {
      "type": "string",
      "enum": ["draft", "verified", "deprecated"]
    },
    "Source": {
      "type": "object",
      "properties": {
        "type":          {"type": "string", "enum": ["classic_literature", "expert_knowledge", "empirical_data", "algorithm_derived"]},
        "reference":     {"type": "string"},
        "author":        {"type": "string"},
        "applicability": {"$ref": "#/definitions/Applicability"},
        "limitations":   {"type": "array", "items": {"type": "string"}},
        "verified_by":   {"type": "string"},
        "verified_at":   {"type": "string", "format": "date"}
      },
      "required": ["type", "reference"]
    },
    "Applicability": {
      "type": "object",
      "properties": {
        "scope":    {"type": "string"},
        "excludes": {"type": "array", "items": {"type": "string"}},
        "culture":  {"type": "string"}
      }
    },
    "Metadata": {
      "type": "object",
      "properties": {
        "confidence":         {"type": "number", "minimum": 0, "maximum": 1},
        "completeness":       {"type": "number", "minimum": 0, "maximum": 1},
        "verification_level": {"type": "string", "enum": ["unverified", "peer_reviewed", "expert_approved", "empirically_validated"]}
      },
      "required": ["confidence", "verification_level"]
    },
    "Relationship": {
      "type": "object",
      "properties": {
        "type":   {"$ref": "#/definitions/RelationType"},
        "target": {"type": "string"},
        "weight": {"type": "number", "minimum": 0, "maximum": 1},
        "note":   {"type": "string"}
      },
      "required": ["type", "target"]
    }
  }
}
```

---

## 3. Relationship Type Dictionary

### 3.1 层级关系

| Type | Direction | Semantic | Source | Target |
|------|-----------|----------|--------|--------|
| `IS_A` | → | 子类/实例 | 甲木 | 天干 |
| `PART_OF` | → | 组成部分 | 天干 | 干支系统 |
| `BELONGS_TO` | → | 归属层级 | 食神 | Layer 3 |

### 3.2 命理关系

| Type | Direction | Semantic | Source | Target |
|------|-----------|----------|--------|--------|
| `SHENG` | → | 五行相生 | 木 | 火 |
| `KE` | → | 五行相克 | 木 | 土 |
| `HE` | → | 合 | 甲 | 己 |
| `CHONG` | → | 冲 | 子 | 午 |
| `XING` | → | 刑 | 寅 | 巳 |
| `HAI` | → | 害 | 子 | 未 |
| `HAS_HIDDEN` | → | 地支藏干 | 子 | 癸 |
| `MAPS_TO` | → | 符号→行为 | 食神 | 表达能力 |
| `EXPRESSES_AS` | → | 符号→人格 | 偏印 | 研究型 |

### 3.3 应用关系

| Type | Direction | Semantic | Source | Target |
|------|-----------|----------|--------|--------|
| `SUPPORTS` | → | 能力支撑 | 表达能力 | 教学能力 |
| `SUITABLE_FOR` | → | 适合职业 | 创新能力 | 产品经理 |
| `HAS_RISK` | → | 存在风险 | 创业 | 财务波动 |
| `REQUIRES` | → | 前置条件 | 创业 | 资金储备 |
| `LEADS_TO` | → | 导致结果 | 执行力强 | 快速落地 |
| `CONTRADICTS` | → | 矛盾冲突 | 伤官 | 正官 |
| `AMPLIFIES` | → | 相互增强 | 食神 | 偏财 |
| `REDUCES` | → | 相互减弱 | 正印 | 伤官 |
| `GENERATES` | → | 产生 | 命理计算 | 证据 |
| `DERIVES_FROM` | → | 推导来源 | 证据 | 规则 |
| `REFERENCES` | → | 引用来源 | 节点 | 三命通会 |

### 3.4 流程关系

| Type | Direction | Semantic | Source | Target |
|------|-----------|----------|--------|--------|
| `TRIGGERS` | → | 触发动作 | 高能量 | 行动窗口 |
| `RESOLVES_TO` | → | 决策输出 | 决策模板 | 建议列表 |
| `FOLLOWED_BY` | → | 时间顺序 | 大运甲 | 大运乙 |

### 3.5 质量关系

| Type | Direction | Semantic | Source | Target |
|------|-----------|----------|--------|--------|
| `VALIDATED_BY` | → | 被验证 | 规则 | 专家审核 |
| `DEPRECATES` | → | 替代旧版 | 规则v2 | 规则v1 |

### 3.6 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/relation-type",
  "type": "string",
  "enum": [
    "IS_A", "PART_OF", "BELONGS_TO",
    "SHENG", "KE", "HE", "CHONG", "XING", "HAI",
    "HAS_HIDDEN", "MAPS_TO", "EXPRESSES_AS",
    "SUPPORTS", "SUITABLE_FOR", "HAS_RISK", "REQUIRES",
    "LEADS_TO", "CONTRADICTS", "AMPLIFIES", "REDUCES",
    "GENERATES", "DERIVES_FROM", "REFERENCES",
    "TRIGGERS", "RESOLVES_TO", "FOLLOWED_BY",
    "VALIDATED_BY", "DEPRECATES"
  ]
}
```

---

## 4. Domain Schemas（点 10）

### 4.1 Foundation Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/foundation",
  "allOf": [{"$ref": "lns://knowledge/base-node"}],
  "properties": {
    "type": {"const": "Foundation"},
    "category": {
      "type": "string",
      "enum": ["tiangan", "dizhi", "wuxing", "jieqi", "yinyang", "nayin", "hidden_stem", "twelve_stage", "kongwang"]
    },
    "code": {"type": "string"},
    "attributes": {"type": "object"},
    "relations": {"type": "array", "items": {"$ref": "lns://knowledge/base-node#/definitions/Relationship"}}
  },
  "required": ["category", "code"]
}
```

**示例：**

```json
{
  "id": "TG-01",
  "type": "Foundation",
  "name": "jia_wood",
  "name_cn": "甲",
  "version": "1.0.0",
  "status": "verified",
  "category": "tiangan",
  "code": "jia",
  "attributes": {"wuxing": "木", "yinyang": "阳", "direction": "东", "season": "春", "body": "胆"},
  "relations": [
    {"type": "HE", "target": "TG-06", "weight": 1.0, "note": "甲己合土"},
    {"type": "KE", "target": "TG-05", "weight": 1.0, "note": "甲克戊"}
  ],
  "source": {"type": "classic_literature", "reference": "《渊海子平》卷一", "verified_by": "LNS Expert Team", "verified_at": "2026-06-01"},
  "metadata": {"confidence": 0.98, "completeness": 1.0, "verification_level": "expert_approved"},
  "created_at": "2026-06-01T00:00:00Z",
  "updated_at": "2026-06-01T00:00:00Z"
}
```

### 4.2 Rule Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/rule",
  "allOf": [{"$ref": "lns://knowledge/base-node"}],
  "properties": {
    "type": {"const": "Rule"},
    "rule_category": {
      "type": "string",
      "enum": ["wang_shuai", "geju", "ten_god_calc", "tiaohou", "yongshen", "xishen", "jishen",
               "shensha", "dayun", "liunian", "liuyue", "hehua", "chong_xing_hai", "cong_hua"]
    },
    "priority":   {"type": "integer", "minimum": 1, "maximum": 10},
    "weight":     {"type": "number", "minimum": 0, "maximum": 1},
    "condition":  {"type": "string"},
    "inputs":     {"type": "array", "items": {"$ref": "#/definitions/IOField"}},
    "output":     {"type": "object"},
    "exceptions": {"type": "array", "items": {"$ref": "#/definitions/Exception"}},
    "conflict":   {"type": "array", "items": {"$ref": "#/definitions/Conflict"}},
    "examples":   {"type": "array", "items": {"type": "object"}}
  },
  "required": ["rule_category", "priority", "weight", "condition", "inputs", "output"],
  "definitions": {
    "IOField": {
      "type": "object",
      "properties": {
        "name":     {"type": "string"},
        "type":     {"type": "string"},
        "required": {"type": "boolean"}
      },
      "required": ["name", "type"]
    },
    "Exception": {
      "type": "object",
      "properties": {
        "condition": {"type": "string"},
        "rule_id":   {"type": "string"},
        "action":    {"type": "string", "enum": ["delegate", "override", "skip"]}
      },
      "required": ["condition", "rule_id"]
    },
    "Conflict": {
      "type": "object",
      "properties": {
        "rule_id":    {"type": "string"},
        "type":       {"type": "string", "enum": ["override", "conditional", "mutual_exclusive"]},
        "resolution": {"type": "string"}
      },
      "required": ["rule_id", "type", "resolution"]
    }
  }
}
```

**示例：**

```json
{
  "id": "RULE-005",
  "type": "Rule",
  "name": "season_energy_rule",
  "name_cn": "季节旺衰判断规则",
  "version": "1.2.0",
  "status": "verified",
  "rule_category": "wang_shuai",
  "priority": 1,
  "weight": 0.8,
  "condition": "日干生于当令之月",
  "inputs": [
    {"name": "month_branch", "type": "dizhi", "required": true},
    {"name": "day_stem", "type": "tiangan", "required": true}
  ],
  "output": {"energy_level": "string", "score": "number"},
  "exceptions": [
    {"condition": "从格", "rule_id": "RULE-099", "action": "delegate"}
  ],
  "conflict": [
    {"rule_id": "RULE-017", "type": "override", "resolution": "从格判定优先于旺衰判定"}
  ],
  "examples": [
    {"input": {"month_branch": "寅", "day_stem": "甲"}, "output": {"energy_level": "旺", "score": 85}}
  ],
  "source": {"type": "classic_literature", "reference": "《子平真诠》卷三·旺衰章", "verified_by": "首席命理架构师", "verified_at": "2026-06-15"},
  "metadata": {"confidence": 0.90, "completeness": 0.85, "verification_level": "expert_approved"},
  "created_at": "2026-06-10T00:00:00Z",
  "updated_at": "2026-06-15T00:00:00Z"
}
```

### 4.3 TenGod Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/ten-god",
  "allOf": [{"$ref": "lns://knowledge/base-node"}],
  "properties": {
    "type": {"const": "TenGod"},
    "category": {"type": "string", "enum": ["same_energy", "produce", "control", "consume"]},
    "definition":  {"type": "string"},
    "condition":   {"type": "string"},
    "strength": {
      "type": "object",
      "properties": {
        "high": {"type": "object", "properties": {"behavior": "array", "capability": "array", "risk": "array"}},
        "low":  {"type": "object", "properties": {"behavior": "array", "capability": "array", "risk": "array"}}
      }
    },
    "xi":   {"type": "object"},
    "ji":   {"type": "object"},
    "career":      {"type": "array", "items": {"type": "string"}},
    "wealth":      {"type": "array", "items": {"type": "string"}},
    "relationship":{"type": "array", "items": {"type": "string"}},
    "health":      {"type": "array", "items": {"type": "string"}}
  },
  "required": ["category", "definition", "condition"]
}
```

**示例：**

```json
{
  "id": "TG-SS",
  "type": "TenGod",
  "name": "shang_god",
  "name_cn": "伤官",
  "version": "2.1.0",
  "status": "verified",
  "category": "consume",
  "definition": "日干所生之异性五行",
  "condition": "日干生天干，阴阳异性",
  "strength": {
    "high": {"behavior": ["挑战规则", "创新表达", "强主观性"], "capability": ["创新能力", "表达能力"], "risk": ["冲突管理弱", "过度理想化"]},
    "low":  {"behavior": ["循规蹈矩", "表达受限"], "capability": ["分析能力弱"], "risk": ["缺乏主动性"]}
  },
  "xi":   {"career": ["创意行业", "科技创新"], "wealth": ["知识付费", "内容创作"]},
  "ji":   {"career": ["行政岗位", "循规管理工作"], "risk": ["被规则压制"]},
  "career": ["创业", "创意行业", "科技创新", "产品经理"],
  "wealth": ["IP打造", "知识付费", "内容创作"],
  "relationship": ["需要结构约束", "适合自由协作"],
  "health": ["情绪波动", "心火旺盛"],
  "source": {"type": "classic_literature", "reference": "《子平真诠》· 伤官章", "verified_by": "首席命理架构师", "verified_at": "2026-06-20"},
  "metadata": {"confidence": 0.88, "completeness": 0.82, "verification_level": "expert_approved"},
  "relationships": [
    {"type": "MAPS_TO", "target": "CAP-003", "weight": 0.9, "note": "伤官映射到创新能力"},
    {"type": "CONTRADICTS", "target": "TG-ZG", "weight": 0.7, "note": "伤官与正官相克"}
  ],
  "created_at": "2026-06-01T00:00:00Z",
  "updated_at": "2026-07-02T00:00:00Z"
}
```

### 4.4 Capability Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/capability",
  "allOf": [{"$ref": "lns://knowledge/base-node"}],
  "properties": {
    "type": {"const": "Capability"},
    "parent": {"type": "string"},
    "description": {"type": "string"},
    "level": {"type": "string", "enum": ["basic", "intermediate", "advanced"]},
    "indicators": {"type": "array", "items": {"type": "string"}},
    "linked_gods": {"type": "array", "items": {"type": "string"}},
    "linked_elements": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["description", "level"]
}
```

**示例：**

```json
{
  "id": "CAP-003",
  "type": "Capability",
  "name": "innovation_ability",
  "name_cn": "创新能力",
  "version": "1.0.0",
  "status": "verified",
  "parent": "thinking",
  "description": "突破现有框架，提出新解决方案的能力",
  "level": "advanced",
  "indicators": ["经常提出新想法", "擅长解决问题", "不满足于现状"],
  "linked_gods": ["伤官", "食神", "偏印"],
  "linked_elements": ["火", "水"],
  "source": {"type": "expert_knowledge", "reference": "LNS Capability Framework v2", "verified_by": "首席产品架构师", "verified_at": "2026-06-25"},
  "metadata": {"confidence": 0.82, "completeness": 0.75, "verification_level": "peer_reviewed"},
  "created_at": "2026-06-20T00:00:00Z",
  "updated_at": "2026-07-02T00:00:00Z"
}
```

### 4.5 Career Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/career",
  "allOf": [{"$ref": "lns://knowledge/base-node"}],
  "properties": {
    "type": {"const": "Career"},
    "industry": {"type": "string"},
    "role": {"type": "string"},
    "matched_gods": {"type": "array", "items": {"type": "string"}},
    "matched_elements": {"type": "array", "items": {"type": "string"}},
    "skills": {"type": "array", "items": {"type": "string"}},
    "entry_barrier": {"type": "string", "enum": ["低", "中", "高"]},
    "salary_range": {"type": "object", "properties": {"min": "integer", "max": "integer"}},
    "growth_path": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["industry", "role"]
}
```

**示例：**

```json
{
  "id": "CAR-012",
  "type": "Career",
  "name": "product_manager",
  "name_cn": "产品经理",
  "version": "1.0.0",
  "status": "verified",
  "industry": "互联网",
  "role": "产品经理",
  "matched_gods": ["伤官", "正印", "偏财"],
  "matched_elements": ["水", "火"],
  "skills": ["需求分析", "产品设计", "数据分析", "跨部门沟通"],
  "entry_barrier": "中",
  "salary_range": {"min": 15000, "max": 60000},
  "growth_path": ["产品助理 → 产品经理 → 高级产品经理 → 产品总监 → CPO"],
  "source": {"type": "empirical_data", "reference": "2026年中国互联网行业薪酬报告", "verified_by": "HR 数据团队", "verified_at": "2026-06-01"},
  "metadata": {"confidence": 0.78, "completeness": 0.70, "verification_level": "peer_reviewed"},
  "created_at": "2026-06-20T00:00:00Z",
  "updated_at": "2026-07-02T00:00:00Z"
}
```

### 4.6 Evidence Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/evidence",
  "allOf": [{"$ref": "lns://knowledge/base-node"}],
  "properties": {
    "type": {"const": "Evidence"},
    "conclusion": {"type": "string"},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "chain": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "step":       {"type": "integer"},
          "type":       {"type": "string", "enum": ["knowledge", "rule", "calculation", "conclusion", "confidence"]},
          "source_id":  {"type": "string"},
          "content":    {"type": "string"},
          "weight":     {"type": "number", "minimum": 0, "maximum": 1}
        },
        "required": ["step", "type", "content"]
      },
      "minItems": 3
    }
  },
  "required": ["conclusion", "confidence", "chain"]
}
```

**示例：**

```json
{
  "id": "EVI-20260702-001",
  "type": "Evidence",
  "name": "career_action_evidence",
  "name_cn": "职业行动建议证据链",
  "version": "1.0.0",
  "status": "verified",
  "conclusion": "当前适合主动推进职业选择",
  "confidence": 0.83,
  "chain": [
    {"step": 1, "type": "knowledge", "source_id": "TG-SS",   "content": "伤官旺则创新与表达能力强", "weight": 0.35},
    {"step": 2, "type": "rule",      "source_id": "RULE-042", "content": "伤官生财格局，大运逢财星则行动窗口开启", "weight": 0.30},
    {"step": 3, "type": "calculation", "source_id": "STATE-ENG", "content": "能量等级 H / 风险等级 M / 窗口状态 开启", "weight": 0.20},
    {"step": 4, "type": "conclusion",  "source_id": null,       "content": "当前适合主动推进职业选择", "weight": 0.15}
  ],
  "source": {"type": "algorithm_derived", "reference": "LNS Evidence Assembly Pipeline", "verified_by": "系统自动", "verified_at": "2026-07-02"},
  "metadata": {"confidence": 0.83, "completeness": 0.90, "verification_level": "expert_approved"},
  "created_at": "2026-07-02T09:30:00Z",
  "updated_at": "2026-07-02T09:30:00Z"
}
```

### 4.7 Personality Node

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/personality",
  "allOf": [{"$ref": "lns://knowledge/base-node"}],
  "properties": {
    "type": {"const": "Personality"},
    "traits": {"type": "array", "items": {"type": "string"}},
    "matched_gods": {"type": "array", "items": {"type": "string"}},
    "matched_elements": {"type": "array", "items": {"type": "string"}},
    "career_fit": {"type": "array", "items": {"type": "string"}},
    "relationship_style": {"type": "string"},
    "risk": {"type": "array", "items": {"type": "string"}},
    "advice": {"type": "string"}
  },
  "required": ["traits", "matched_gods"]
}
```

**示例：**

```json
{
  "id": "PER-004",
  "type": "Personality",
  "name": "research_type",
  "name_cn": "研究型",
  "version": "1.0.0",
  "status": "verified",
  "traits": ["深度思考", "信息驱动", "喜欢钻研", "独立工作"],
  "matched_gods": ["偏印", "正印"],
  "matched_elements": ["金", "水"],
  "career_fit": ["研究员", "分析师", "算法工程师", "数据科学家"],
  "relationship_style": "适合独立协作，需要被理解和尊重专业边界",
  "risk": ["过于理想化", "行动不足", "社交能量消耗快"],
  "advice": "需要搭配执行力强的伙伴，定期让自己走出研究状态",
  "source": {"type": "expert_knowledge", "reference": "LNS Personality Framework v1", "verified_by": "首席产品架构师", "verified_at": "2026-06-28"},
  "metadata": {"confidence": 0.75, "completeness": 0.72, "verification_level": "peer_reviewed"},
  "created_at": "2026-06-25T00:00:00Z",
  "updated_at": "2026-07-02T00:00:00Z"
}
```

---

## 5. Graph Edge Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "lns://knowledge/edge",
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "source": {"type": "string"},
    "target": {"type": "string"},
    "relationship": {"$ref": "lns://knowledge/relation-type"},
    "weight": {"type": "number", "minimum": 0, "maximum": 1},
    "version": {"type": "string"},
    "status": {"$ref": "lns://knowledge/base-node#/definitions/Status"},
    "metadata": {"$ref": "lns://knowledge/base-node#/definitions/Metadata"},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"}
  },
  "required": ["id", "source", "target", "relationship"]
}
```

---

## 6. Graph Query Templates

### 6.1 Cypher 示例

```cypher
// 根据十神推荐职业（深度2）
MATCH (tg:TenGod {id: 'TG-SS'})
  -[:MAPS_TO]-> (:Capability)
  -[:SUPPORTS|SUITABLE_FOR*1..2]-> (c:Career)
RETURN c.name_cn AS career, c.metadata.confidence AS score
ORDER BY score DESC
LIMIT 5
```

```cypher
// 查找矛盾关系
MATCH (a)-[:CONTRADICTS]->(b)
WHERE a.id IN ['TG-SS']
RETURN a.name_cn, b.name_cn
```

### 6.2 REST API 示例（建议）

```
GET /v1/knowledge/node/:id
    → Base Node + domain-specific fields

GET /v1/knowledge/query
    ?source=TG-SS
    &relation=MAPS_TO,SUPPORTS
    &depth=2
    → {nodes: [], edges: []}
```

---

## 7. State → Action 静态路由表

### 7.1 路由机制

采用「三维向量位掩码（Vector Bitmask）」建立静态路由表，将状态组合确定性地映射到 Action ID。

### 7.2 路由输入向量

```
Router_Key = [Dominant_Structure_ID] + [Energy_Level] + [Time_Dimension_Scale]
```

- Dominant_Structure_ID: 01(比肩)/02(劫财)/03(伤官)/04(食神)/05(正财)/06(偏财)/07(正官)/08(七杀)/09(正印)/10(偏印)
- Energy_Level: H(高)/M(中)/L(低)
- Time_Dimension_Scale: T0(日)/T1(月)/T2(年)/T3(大运)

### 7.3 MVP 示例

```json
{
  "03_H_T0": {"actions": ["Action-003", "Action-011"], "source_rules": ["RULE-042", "RULE-088"]},
  "05_L_T1": {"actions": ["Action-022", "Action-008"], "source_rules": ["RULE-031"]}
}
```

### 7.4 执行规则

- 每个 Router_Key 必须至少映射 1 个 Action ID
- 路由条目必须标注来源 Rule ID
- 路由表由首席命理架构师维护，每次知识图谱版本更新同步审计

---

## 8. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-29 | LNS Team | Initial frozen release |
| 2.0 | 2026-07-02 | LNS Team | Added Layer 4-15 schemas |
| **2.1** | **2026-07-02** | **LNS Team** | **Full JSON Schema for all 8 domains + Edge schema + Relation dictionary + Evidence format** |
