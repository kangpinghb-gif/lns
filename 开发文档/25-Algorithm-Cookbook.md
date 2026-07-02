# Life Navigation System — Algorithm Cookbook

> Version: 1.0 | Status: Frozen Execution Standard (追加冻结)

---

## 一、5 个工程黑洞的完全固化方案

### 1. 历法基准锚点与「夜子时」分界裁决

#### 起始锚点（Epoch）
系统时间转换与干支递推统一以 **公历 1900 年 1 月 31 日（农历正月初一）为「甲午日」** 作为底层数学递推的绝对基准。开发团队校验算法库时必须与此锚点对齐。

#### 夜子时裁决（ADR-009）
LNS 统一采用 **「早夜子时分界法」**（子平正宗流派）：
- **早子时（00:00–01:00）**：属于当日，干支使用当日日干
- **夜子时（23:00–24:00）**：属于当日，**日柱干支不进位**（仍算当天），但**时柱干支必须进位**（使用次日的时干支来推算时柱）

### 2. State Engine → Action Library 静态路由表

采用 **「三维向量位掩码（Vector Bitmask）」** 建立静态路由表。

#### 路由输入向量
```
Router_Key = [Dominant_Structure_ID] + [Energy_Level] + [Time_Dimension_Scale]
```

#### MVP 前 50 条硬编码规范示例
```json
{
  "03_H_T0": ["Action_03", "Action_11"],
  "05_L_T1": ["Action_22", "Action_08"]
}
```
注：`03_H_T0` 代表：伤官主导结构 + 高能量 + T0 日级 → 路由至：启动创新任务与言语安全阀模板。

### 3. 评分模型量化权重（Decision Score Weight）

#### 确定性公式
```
Decision Score = (0.3 × Opportunity) - (0.4 × Risk) + (0.1 × Match) + (0.2 × Time)
```

#### 执行红线
风控（Risk）权重强制锁定最高（0.4）。最终得分统一做归一化（0–100）处理。

### 4. 数据库「重新校准」的版本断代逻辑

用户重新校准出生时间（精确到分）时：

1. 将当前活跃的 `bazi_chart` 记录的 `is_active` 状态置为 `false`，并写入 `deactivated_at` 时间戳
2. 将该旧版快照完整投递备份至 `bazi_chart_history` 表
3. 写入全新计算的 `bazi_chart` 记录，`version` 递增（如 v1.0.0 → v1.1.0），`is_active` 置为 `true`

**执行红线**：前端 Dashboard 与 AI 问答在 runtime 阶段只读取 `is_active == true` 的最新结构体。

### 5. Golden Dataset 的绝对通过标准

#### 执行红线
彻底放弃对齐外部商业网站，将 **《三命通会》与《子平真诠》古典数理逻辑化后的算法** 作为唯一绝对标准答案。

#### 边界判定
凡交接点在 1 秒以内的边界盘，一律以 Calendar Engine 基于紫金山天文台历法数据推导出的真太阳时为准。Expected Output 由首席命理架构师人工锁定，不匹配则直接阻塞系统上线。

---

## 二、3 个逻辑悖论的闭环重构

### 悖论 1：千人千面闲聊与禁止 AI 自由发挥的冲突

#### 情绪分流机制（Emotion Triage Router）
在 Prompt Engine 中追加双轨意图分类器：

- 若 `Intent == 寻求决策` → 走标准流程（State → Decision Engine，输出 P0–P3）
- 若 `Intent == 纯情绪宣泄/闲聊` → 触发 **Emotion Triage 模式**：绕过 Decision Engine，仅提取 State Engine 当前能量模型，LLM 限制仅输出 **「1 句客观状态解析 + 1 句同理心共情」**，且强制在 UI 层隐藏 P0–P3 结构块。

### 悖论 2：AI 质检（Output Validator）连续不合格时的系统出路

#### 三次重试熔断策略
1. 第 1–2 次不合格：携带格式错误信息，以极低温度（Temperature = 0.2）向 LLM 发起强约束修复请求
2. 第 3 次仍不合格：系统触发 **核心功能兜底熔断**。直接抛弃 LLM 文本生成，前端 UI 降级为 **「数据卡片模式」**——直接将 Decision Engine 输出的纯 JSON 数据（Action ID 对应的静态文本、风险项、机会项）直接渲染为标准卡片组件，并提示用户：*「主控系统已切换至安全数据决策模式」*

### 悖论 3：UI 禁止玄学符号与专业模式显示八字原盘的平衡

#### 视觉红线界定（ADR-010 追加）

**允许展示（科学数据结构）：**
- 五行生克矩阵图
- 能量分布柱状图
- 干支作用关系动态连线（生、克、合、冲，使用带红蓝方向的工业箭头）
- 专业模式定位为「硬核人生数据仪表盘」

**严禁展示（神秘/焦虑符号）：**
- 复古罗盘刻度盘
- 太极八卦图
- 神煞迷信标签（如「血刃」「吊客」「亡神」等字眼）

---

## 三、法律风险与免责条款的致命补充

### 全局免责声明
注入于 `00-README.md`、用户注册协议及 System Prompt 最高层：

> 「LNS 是一套基于古典时间建模与行为学映射的理性决策辅助工具。系统输出的所有建议、风险提示及趋势分析均基于结构化模型推演，**仅供用户参考，不构成任何具有法律效力的决策指令或投资建议。最终决定权与责任完全归用户所有。**」

### AI 输出强制注入（Footer Injection）
多端渲染 AI 问答或报告气泡时，在组件底部强制流式追加一段非 LLM 生成的、前端不可关闭的灰色字体：

> ⚖️ 导航员提示：本建议基于当前状态模型推演。人生最终决定权与风险完全由您掌控。

---

## Appendix: Implementation Lockdowns（实施锁定）

### Lockdown 1：情绪分流判定规则——关键词规则分类器

MVP 阶段强制采用 **「关键词规则分类器」**（非 LLM 判断），写入 `10-Prompt-Engine.md` 第 17.2 节。

**闲聊/情绪触发关键词库：**
```
['心情', '难受', '开心', '郁闷', '压力大', '累了', '烦', '没劲', '无聊', '不爽']
```

**决策触发关键词库：**
```
['工作', '换', '创业', '投资', '感情', '学习', '建议', '选择', '辞职', '分手', '结婚', '买房', '跳槽', '方向', '迷茫']
```

**分类规则：**
- 命中决策库 → 走标准流程（State → Decision Engine，输出 P0-P3）
- 命中情绪库且未命中决策库 → 走 Emotion Triage 模式
- 两者都命中或都未命中 → **默认走决策流程**（宁可严肃，不可放纵闲聊导致失控）

### Lockdown 2：真太阳时与节气计算的确定性算法库

强制锁定计算库，写入 `04-Calendar-Engine.md`：

| 计算类型 | 强制锁定库 | 版本约束 |
|---------|-----------|---------|
| 太阳时与节气精确计算 | `Skyfield`（搭载 NASA JPL DE440 星历） | ≥ 1.46 |
| 农历转换 | `lunar-python` | ≥ 2.0.5 |

**执行红线**：禁止引入 `ephem`、`astropy`、`lunardate` 或其他天文库。Golden Dataset 回归测试时，Calendar Engine 输出必须与以上两个库的接口输出对齐。

### Lockdown 3：城市转时区/经纬度的离线降级方案

构建 **`cities.json` 静态映射表**，写入 `04-Calendar-Engine.md` 第 7.1 节（Timezone Resolver）。

- V1 覆盖 **500+ 全球核心城市**，嵌入代码库
- 系统启动时**优先读静态表**，命中后绝不调用外部 API
- 未覆盖的城市：允许调用外部地理编码 API，设置 **3 秒超时**
- 超时后**回退至 UTC+0**，并提示用户手动选择时区
- 写入 `15-System-Orchestration.md` 第 11 节（Failure Handling）作为 Fail Case 4

### Lockdown 4：历史导航（T-1）模式识别的硬编码规则

V1 阶段模式识别严格定义为 **「硬编码逻辑对比」**，写入 `08-Time-Engine.md` 第 12.6 节。

**对比方式：**
对比相邻两个大运周期的 `[日主五行, 十神主导结构]`。

**判定标准：**
- 若连续两个周期的结构相似度 > 80%（如都是「火土+正印」）→ 标注为 **「稳定积累型路径」**
- 若相反（如金→火）→ 标注为 **「结构转型型路径」**
- 其他情况 → 标注为 **「混合演进型路径」**

**执行红线：** 禁止 AI 参与模式归纳。V1 只做硬编码二元对比，不做聚类或 NLP。

---

## Appendix B: Architecture Retrofit（架构修复补丁）

### Patch 1：Time Engine 数据流断层修复

**问题：** 单向管道只有用户出生时间，Time Engine 计算 T0/T1 时缺少当前时间八字。

**修复：**
- 03-System-Architecture.md 和 11-API-Design.md 的输入契约新增 `target_time` 字段
- Calendar Engine 和 BaZi Engine 支持双模式：一次处理出生时间（静态命盘），一次处理当前时间（流日/流年）
- 08-Time-Engine.md 的输入契约扩展为接收 `birth_state` + `current_bazi` + `target_time` 三组数据
- 15-System-Orchestration.md 新增 §4.1 Dual-Mode Execution，明确两路计算路径

### Patch 2：夜子时边界溢出防护

**问题：** 基准锚点（1900-1-31）前 1 天夜子时，取次日日干会导致数组越界。

**修复：**
- 05-BaZi-Engine.md 新增 §6.4.2，定义下界防护（逆向推算）和上界防护（模 60 循环投影）
- Golden Dataset 第二层必须包含 4 个边界夜子时用例

### Patch 3：节气精度契约修复

**问题：** `solar_term` 仅为字符串，BaZi Engine 无法判断交节前后 1 分钟。

**修复：**
- 04-Calendar-Engine.md 输出契约中 `solar_term` 改为对象：`{name, transition_timestamp, is_before_transition}`
- `transition_timestamp` 为 ISO 8601 UTC 精确时间戳
- BaZi Engine 通过比对该时间戳与出生时间的先后顺序判断月柱归属

### Patch 4：真太阳时经纬度精度修复

**问题：** `{city, country}` 级输入导致跨经度城市（如重庆）误差达 8-10 分钟。

**修复：**
- 04-Calendar-Engine.md 输入契约扩展：`birth_place` 新增 `district`、`latitude`、`longitude` 可选字段
- 直辖市/跨经度城市建议传入精确区县或经纬度
- cities.json V1 标注跨经度城市列表，对未传精确经纬度的跨经度城市输出精度警告

### Patch 5：KG 冲突消解缺失修复

**问题：** 十神复合出现时（如正官+伤官），简单 Append 导致矛盾输出。

**修复：**
- 新增 **07A-State-Synthesizer.md**，位于 Knowledge Graph 与 Time Engine/Decision Engine 之间
- 定义 4 组冲突对消解策略（权重分配、五行环境选择、能量等级判断）
- 主导结构标签占输出 70%，次结构标签占 30%
- 消解日志写入审计表

### Patch 6：缓存策略缺失修复

**问题：** 10 节点超长流水线无缓存分层，200ms API 目标不可达。

**修复：**
- 新增 **12A-Caching-Strategy.md**，定义 5 层数据分类：静态（永久）/年运（365d）/月运（31d）/日运（不缓存）/AI问答（不缓存）
- Pipeline Short-Circuit 逻辑：每次请求先检查缓存再决定计算路径
- 性能达标：首次~1800ms、次日回访~300ms、同月多次回访~150ms、AI问答~800ms

---

### Patch 7：BaZi Engine 语义泄露修复

**问题：** BaZi Engine 自称纯数理计算层，但 Luck Cycle 输出含语义字段 `theme`。

**修复：**
- 05-BaZi-Engine.md §10 移除 `theme` 字段，输出改为纯数理结构 `{age_range, pillar}`
- `theme` 移交 06-State-Engine.md §6.5，由 State Engine 从大运干支推导语义主题
- 06-State-Engine.md 输出契约新增 `luck_cycle_theme` 字段

### Patch 8：KG 依赖规则修复

**问题：** KG 依赖规则写明仅接收 BaZi Engine 输出，禁止 State 输入，导致状态数据无法传递给 KG。

**修复：**
- 07-Knowledge-Graph.md §12 修正为依赖 **State Engine Output**
- 输入合同新增 `state_context`：`{current_stage, energy_level, risk_level, dominant_structure}`
- 数据流确认：BaZi → State → KG → State Synthesizer → Time/Decision

### Patch 9：Time Engine / Decision Engine 职责分离

**问题：** Time Engine 要求输出 P0-P3 行动排序，与 Decision Engine 的唯一职责完全重叠。

**修复：**
- 08-Time-Engine.md §4 输出中 `action: []` 改为 `recommended_focus: []`（关注领域，非优先级）
- 08-Time-Engine.md §14 改为 Focus Generation Rules，P0-P3 全部归 Decision Engine
- Time Engine 输出降级为 Decision Engine 的输入之一，不再重叠

### Patch 10：生命阶段以大运起运年龄为锚点

**问题：** Life Stage 基于固定物理年龄（0-12/13-18/…），与大运起运年龄（1岁上运 vs 9岁上运）数理冲突。

**修复：**
- 06-State-Engine.md §6 重写：生命周期以 **大运起运年龄为锚点**，每个大运周期（10年）为一个 stage
- 物理年龄降级为默认值（仅当起运年龄缺失时使用）
- 算法：`floor((age - start_age) / 10)` 确定当前大运周期索引

### Patch 11：时间漏斗机制（宏观约束微观）

**问题：** Time Engine 规定 T0 不依赖 T2，导致 T0 在宏观高风险期仍可能输出激进建议。

**修复：**
- 08-Time-Engine.md §7 Rule 2 改为「时间漏斗机制」：T3→T2→T1→T0 自上而下约束投影
- 若 T2 risk_level = high，T0 risk 不得低于 T2
- 若 T3 为结构冲突期，T0 必须包含 T3 风险提示
- 微观信号不得覆盖宏观信号

### Patch 12：五行权重常数表与归一化公式

**问题：** 「藏干计权重，日主归一化」无权重常数表、无数学公式，不可执行。

**修复：**
- 05-BaZi-Engine.md §8.1 新增 12 地支藏干权重常数表（本气 0.7 / 中气 0.2 / 余气 0.1）
- 05-BaZi-Engine.md §8.2 新增归一化公式：`score = (raw / max(raw)) * 10`
- 05-BaZi-Engine.md §8.3 与 Golden Dataset 100% 匹配要求
