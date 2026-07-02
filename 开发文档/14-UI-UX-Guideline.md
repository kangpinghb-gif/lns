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

### 4.1 Mobile App 字号边界
在 420-430px 移动端容器内，视觉权重必须服务于决策路径，而不是展示感。

- 命盘锚点条：12px，`rgba(242,246,255,.32)`，字重 400，不使用 letter-spacing。
- 首页用户姓名：32-34px，字重不超过 760。
- State Card 能量大数字：44-48px，字重不超过 760。
- Action Card 标题：18px / 600；只有真正的页面主标题才允许使用 28px 以上。
- Mini Card 数值：优先统一为数字、百分比或同一量纲标签，避免一侧长词、一侧单字造成视觉重量失衡。

判断标准：如果某个元素不是用户下一步行动的入口，就不应成为首屏最醒目的元素。

## 5. Layout System
8pt spacing system, Mobile-first layout, 最大宽度420px。Spacing: 4px/8px/16px/24px/32px。

### 5.1 表单密度
出生信息页属于任务型表单，不是营销页；字段应保持紧凑、稳定、易扫描。

- Input / Select 高度建议 48-50px。
- Segmented control 与普通 input 高度必须一致。
- 日期与时间并排时，不得使用过高字段导致表单密度过低。
- 主按钮可以高于输入框，但文字必须与按钮背景满足 AA 对比度。

## 6. Card System
- State Card: 当前阶段、能量状态、风险等级
- Time Card: T0/T1/T2/T3、趋势箭头、机会/风险
- Decision Card: P0/P1/P2/P3、行动描述、优先级标签

### 6.1 Card 内部层级
- State Card 中数字、标签、状态胶囊必须有明确主次；状态胶囊不得与主数字争抢视觉中心。
- Action Card 使用高饱和背景时，标题字重应降低，避免整卡形成视觉噪音。
- Mini Card 左右并列时，指标表达方式必须可比较；风险等级建议显示为 `33%` 这类数值，详细解释放到 note。

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

### 9.1 底部导航可见性
底部导航的非激活态仍然是可点击入口，对比度不得低到不可识别。

- 非激活态文字与图标建议不低于 `rgba(242,246,255,.52)`。
- 激活态使用 Primary Blue。
- 图标和文字必须同时可辨识，不能只依赖颜色表达当前状态。

## 10. Animation Rules
允许：Fade in, Slide up, Progress bar, Trend line animation。
禁止：炫酷动画、命理风水动画、无意义动效。

## 11. Icon System
Line Icons, Minimal, Consistent stroke width。
Icon含义：📍当前状态, ⚡能量, ⚠️风险, 🎯行动, ⏳时间。

## 12. Language System
所有语言必须中性、可执行、无恐吓、无宿命。
❌命中注定 → ✅当前结构倾向于。

### 12.1 开发占位文案
开发说明、接口占位、调试提示不得直接暴露给最终用户。

- 禁止在页面默认态显示「将调用真实接口」「测试数据」「开发中」等工程说明。
- 表单状态节点默认应为空或隐藏，仅在提交中、成功、失败时显示用户可理解的反馈。
- 对用户可见的错误文案必须说明下一步操作，而不是暴露后端或接口细节。

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
