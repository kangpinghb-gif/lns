# Life Navigation System — Database Design

> Version: 1.0 | Status: Core Data Layer (Frozen)

## 1. Purpose
将人生计算结果结构化存储，使系统具备长期记忆+可回溯+可演化能力。

## 2. Core Principle
数据库不存结论。只存：原始输入、结构化中间态、时间序列状态、决策记录、行为反馈。

## 3. Database Architecture
PostgreSQL (Core Structured Data) → Redis (State Cache) → Vector DB (Semantic Memory - V2 optional) → Object Storage (Reports/JSON/PDF)

## 4. Core Tables

### 4.1 users
CREATE TABLE users (id UUID PK, birth_date DATE NOT NULL, birth_time TIME NOT NULL, birth_place TEXT NOT NULL, timezone TEXT, created_at TIMESTAMP)

### 4.2 calendar_data
CREATE TABLE calendar_data (user_id UUID, solar_datetime TIMESTAMP, lunar_datetime TEXT, solar_term TEXT, latitude FLOAT, longitude FLOAT)

### 4.3 bazi_chart
CREATE TABLE bazi_chart (user_id UUID, year_pillar TEXT, month_pillar TEXT, day_pillar TEXT, hour_pillar TEXT, ten_gods JSONB, five_elements JSONB, hidden_stems JSONB, luck_cycles JSONB)

### 4.4 life_state
CREATE TABLE life_state (user_id UUID, current_stage TEXT, energy_level TEXT, risk_level TEXT, capability_profile JSONB, behavior_patterns JSONB, updated_at TIMESTAMP)

### 4.5 time_analysis
CREATE TABLE time_analysis (user_id UUID, t0 JSONB, t1 JSONB, t2 JSONB, t3 JSONB, generated_at TIMESTAMP)

### 4.6 decisions
CREATE TABLE decisions (id UUID PK, user_id UUID, p0 JSONB, p1 JSONB, p2 JSONB, p3 JSONB, decision_logic TEXT, created_at TIMESTAMP)

### 4.7 chat_sessions
CREATE TABLE chat_sessions (session_id UUID PK, user_id UUID, messages JSONB, created_at TIMESTAMP, updated_at TIMESTAMP)

### 4.8 reports
CREATE TABLE reports (id UUID PK, user_id UUID, report_type TEXT, content TEXT, actions JSONB, created_at TIMESTAMP)

## 5. Data Relationships
users → calendar_data → bazi_chart → life_state → time_analysis → decisions → reports

## 6. Data Flow Rules
1. 所有数据必须从 users 开始
2. bazi_chart 不能直接生成，必须来自 Calendar Engine
3. life_state 只能来自 State Engine
4. decisions 只能来自 Decision Engine
5. chat_sessions 不允许污染核心结构数据

## 7. State Caching Strategy
Redis 用于：当前状态缓存、T0/T1快速读取、最近决策缓存。

## 8. Versioning Strategy
所有核心表必须支持：历史版本、时间戳追踪、状态回溯。

## 9. Data Integrity Rules
1. 不可覆盖原则：命盘数据不可修改，只能新增版本
2. 状态可更新：life_state 可以更新，但必须保留历史
|3. 决策可追踪：所有 decision 必须可回溯来源
|4. 版本断代规则（重新校准）：用户重新校准出生时间时，将当前活跃的 `bazi_chart` 记录的 `is_active` 置为 `false`，写入 `deactivated_at`；旧版快照完整投递至 `bazi_chart_history` 表；写入全新 `bazi_chart` 记录，`version` 递增，`is_active` 置为 `true`。

## 10. 版本与断代设计

### 10.1 bazi_chart 版本控制

```sql
ALTER TABLE bazi_chart ADD COLUMN version TEXT DEFAULT '1.0.0';
ALTER TABLE bazi_chart ADD COLUMN is_active BOOLEAN DEFAULT true;
ALTER TABLE bazi_chart ADD COLUMN deactivated_at TIMESTAMP;
```

### 10.2 bazi_chart_history 表
```sql
CREATE TABLE bazi_chart_history (
  id UUID PRIMARY KEY,
  bazi_chart_id UUID,
  user_id UUID,
  year_pillar TEXT, month_pillar TEXT, day_pillar TEXT, hour_pillar TEXT,
  ten_gods JSONB, five_elements JSONB, hidden_stems JSONB, luck_cycles JSONB,
  version TEXT, deactivated_at TIMESTAMP, archived_at TIMESTAMP
);
```

### 10.3 Runtime 规则
前端 Dashboard 与 AI 问答在 runtime 阶段只读取 `is_active == true` 的最新结构体。

## 11. Event Logging System
user_input → engine_output → decision → feedback，必须记录完整链路。

## 12. Knowledge Graph Storage

### 12.1 存储决策（V1）
Knowledge Graph 在 V1 中以 **JSON 文件** 存储，**不占用 PostgreSQL 核心用户数据表**。

理由：
- 知识图谱是静态配置数据，非用户生成数据
- 总条目不超过 200 条，JSON 文件加载内存后查询速度比数据库快
- JSON 文件可直接 Git 管理，改动有版本记录，团队协作更方便
- V2 需要支持用户反馈修正、AI 自动优化权重时，再迁移到数据库

### 12.2 文件结构
```
knowledge/
  ten_gods/           ← 10个JSON文件
  five_elements/      ← 5个JSON文件
  shensha/            ← 神煞JSON文件
  actions/
    action_library.json  ← 所有Action模板
```

### 12.3 加载机制
1. 系统启动时从 JSON 文件加载全部知识图谱到内存
2. 写入 Redis 作为热点缓存
3. 知识图谱更新 → 重新加载配置文件（支持热更新）
4. Engine 运行时通过缓存读取，不直接读文件

### 12.4 版本追踪表
```sql
CREATE TABLE knowledge_graph_versions (
  id UUID PRIMARY KEY,
  version TEXT NOT NULL,
  deployed_at TIMESTAMP,
  changelog TEXT,
  file_hash TEXT
);
```

### 12.5 与 20 号文档的关系
数据结构定义详见 `20-Knowledge-Graph-Data-Dictionary.md`，本文件只定义存储架构。

## 13. Analytics Layer (V2 Ready)
未来支持：用户行为分析、决策效果回测、人生路径统计。

## 14. Storage Strategy
结构化数据→PostgreSQL，状态缓存→Redis，报告文件→Object Storage，AI语义记忆→Vector DB（未来）。

## 15. Performance Requirements
写入 <50ms，查询 <100ms，状态读取 <20ms（Redis）。

## 16. Security Rules
禁止用户数据跨账号访问、命盘数据篡改、决策结果覆盖。

## 17. Design Philosophy
把人生计算过程变成可追溯数据系统。

## 18. Extension (V2)
人生时间序列数据库（Life Time Series DB）、决策回溯系统、AI自学习数据库。
