# Life Navigation System — UI/UX Guideline

> Version: 1.0 | Status: Design System Layer (Frozen)

## 1. Purpose
定义整个 LNS 系统的视觉语言、交互规则与信息表达方式。确保一致性、可读性、低认知负担、强决策导向。

## 2. Core Design Philosophy

### Principle 1：工具感优先
UI 必须像 Apple Health / Google Maps / Notion，而不是占卜/命理/神秘系统。

### Principle 2：信息即结构
所有UI必须表达：状态、时间、决策。

### Principle 3：减少解释成本
用户不应该理解UI，而是直接使用UI做决策。

## 3. Color System
Primary Blue #2F6BFF, Success Green #22C55E, Warning Yellow #F59E0B, Danger Red #EF4444, Neutral Gray #64748B。
Blue→核心路径/导航, Green→正向机会, Yellow→注意/变化, Red→风险/警告, Gray→背景信息。

## 4. Typography System
Primary: Inter/SF Pro/PingFang SC, Monospace: JetBrains Mono。
Hierarchy: H1 28-32px 页面标题, H2 20-24px 模块标题, H3 16-18px 卡片标题, Body 14-16px 正文, Caption 12px 辅助说明。

## 5. Layout System
8pt spacing system, Mobile-first layout, 最大宽度420px。Spacing: 4px/8px/16px/24px/32px。

## 6. Card System
- State Card: 当前阶段、能量状态、风险等级
- Time Card: T0/T1/T2/T3、趋势箭头、机会/风险
- Decision Card: P0/P1/P2/P3、行动描述、优先级标签

## 7. Interaction Design
- 一步决策：所有页面回答下一步做什么
- 减少点击层级：最多3层以内
- 默认推荐：系统默认提供P0行动和今日建议

## 8. Information Density
Level 1（首页）：极低密度，只显示关键状态。
Level 2（分析页）：中等密度，展示结构。
Level 3（专业模式）：高密度，全量数据。

## 9. Navigation System
Bottom Nav: Home | Time | Decision | Chat | Report。永远不超过5个入口，核心路径优先。

## 10. Animation Rules
允许：Fade in, Slide up, Progress bar, Trend line animation。
禁止：炫酷动画、命理风水动画、无意义动效。

## 11. Icon System
Line Icons, Minimal, Consistent stroke width。
Icon含义：📍当前状态, ⚡能量, ⚠️风险, 🎯行动, ⏳时间。

## 12. Language System
所有语言必须中性、可执行、无恐吓、无宿命。
❌命中注定 → ✅当前结构倾向于。

## 13. Component Rules
必须组件化：StateCard, TimeCard, DecisionCard, RiskBadge, ActionTag。

## 14. 专业模式视觉边界（ADR-010）

### 14.1 允许展示（科学数据结构）
- 五行生克矩阵图
- 能量分布柱状图
- 干支作用关系动态连线（生、克、合、冲，使用带红蓝方向的工业箭头）
- 专业模式整体定位为「硬核人生数据仪表盘」

### 14.2 严禁展示（神秘/焦虑符号）
- 复古罗盘刻度盘
- 太极八卦图
- 神煞迷信标签（如「血刃」「吊客」「亡神」等字眼）

### 14.3 规范来源
本规范对应 ADR-010，详见 00A-ADR.md。

## 15. Accessibility Rules
对比度≥4.5:1，支持暗黑模式(V2)，字体可缩放，色盲友好。

## 16. Performance Rules
UI渲染 <16ms/frame，页面加载 <1s，图表渲染 <500ms。

## 17. Design Philosophy
把复杂人生系统变成低认知负担的决策界面。

## 18. Extension (V2)
Life Map（人生地图UI）、时间流动画系统、决策模拟器UI、多人生对比模式。
