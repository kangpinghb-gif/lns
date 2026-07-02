# Life Navigation System — Frontend Specification

> Version: 1.0 | Status: UI/UX Core Layer (Frozen)

## 1. Purpose
将人生状态系统+时间系统+决策系统转化为可理解的视觉导航界面。核心目标：让用户像使用 Google Maps 一样理解自己的人生。

## 2. Core UI Philosophy
UI 不是装饰，而是：状态可视化、时间可视化、决策可视化。

## 3. UI Design Principles

### Principle 1：导航优先
所有页面必须回答：我现在在哪？我要去哪？

### Principle 2：信息分层
分三层：核心信息（必须看到）、辅助信息（可展开）、专业信息（隐藏）。

### Principle 3：减少命理感
禁止：罗盘、八卦、神秘符号。必须：卡片、时间轴、图表、路线图。

## 4. App Structure
Home（人生导航）→ Life Overview（人生总览）→ Time Navigation（时间导航）→ Historical Navigation（历史导航）→ Decision Center（决策中心）→ AI Chat Navigator → Report Center → Professional Mode

### 4.1 V1 静态页面实现
当前 V1 前端位于 `LNS/static/`，采用多页面静态骨架，由 Python 服务直接暴露 `/static/*`。

正式页面：
- `home.html`：移动端首页，展示当前锚点、姓名、今日能量、P0 行动、趋势与风险摘要。
- `create.html`：出生信息输入页，负责采集姓名、性别、出生日期、出生时间、出生地与高级选项。
- `kline.html`：人生 K 线总览页，展示能量值、风险值、趋势图、当前阶段判断与后续入口。
- `analysis.html`：命理透视页，展示四柱、五行、十神与结构解释。
- `year-detail.html`：流年详情页，展示年度分项、关键时间点与行动建议。

兼容入口：
- `index.html`：跳转到 `/static/home.html`。
- `dashboard_static.html`：跳转到 `/static/kline.html`。

共享资源：
- `ui-shell.css`：移动端页面主样式。
- `ui-shell.js`：页面初始化、localStorage 状态读取、API 调用与数据映射。
- `assets/lns-logo-icon.svg`、`assets/lns-logo-wordmark.svg`：品牌图形资源。

不应将设计稿、临时 mockup、系统元数据文件放入线上 `static/` 根目录；需要留档时应移动到文档或归档目录，避免被 `/static/*` 直接访问。

## 5. Home Page（核心页面）
3秒让用户知道自己当前状态。UI结构：📍当前人生阶段→⚡当前能量状态→⚠️当前风险提示→🎯今日建议(P0)→➡️进入人生导航。
视觉风格：Apple Health Dashboard + Notion Cards + Google Maps UI。

### 5.1 Home 移动端信息层级
首页首屏按视觉权重排序：

1. P0 行动卡：用户下一步要做什么。
2. State Card：今日能量、当前阶段、窗口提示。
3. 用户姓名与问候：建立个人化感知，但不能压过 State Card。
4. Mini Card：趋势与风险摘要。
5. 命盘锚点条：仅作为背景上下文，是页面里存在感最低的元素。

实现约束：
- 命盘锚点条使用低对比小字，避免抢占注意力。
- 首页姓名字号不得超过 34px；长姓名必须保持一行或自然换行，不得挤压状态卡。
- 能量值大数字控制在 44-48px 区间，避免撑开 State Card。
- Action Card 标题优先使用 18px / 600；蓝色背景上避免大字号重字重形成噪音。
- Mini Card 左右两侧数值表达应保持同一量纲；风险建议使用百分比或数值，不建议用单字等级与长词并列。

## 6. Life Overview Page
内容：人生阶段、能力结构、风险结构、行为模式。UI形式：雷达图（能力）、卡片（风险）、时间轴（阶段）。

## 7. Time Navigation Page
T0(日)→今日任务，T1(月)→月度趋势，T2(年)→年度变化，T3(大运)→长期结构。视觉：时间轴（horizontal timeline）、卡片流、趋势箭头。

## 8. Decision Center
P0：立即执行，P1：重要任务，P2：优化项，P3：可选探索。UI：增强版Todo List、优先级标签、时间窗口标记。

## 9. AI Chat Navigator
UI目标：ChatGPT + Google Maps + Notion AI。用户可问：我现在适合做什么？我要不要换工作？未来趋势？输出结构：当前状态→时间影响→风险→机会→行动建议(P0-P3)。

## 10. Report Center
报告类型：日报、周报、月报、年报、大运报告。UI形式：PDF下载、卡片浏览、时间趋势图。

## 11. Professional Mode
内容：八字原盘、十神结构、五行分布、大运流年。风格：技术性、数据驱动、不情绪化。

## 12. Navigation Design
Bottom Navigation: Home | Time | Decision | Chat | Report

## 13. Visual Language System
允许：Card、Timeline、Radar Chart、Flow Diagram、Priority Tags。禁止：八卦盘、风水罗盘、神秘符号、算命风格视觉。

## 14. Interaction Design
- 所有操作必须是下一步导向
- 所有页面必须有下一步建议
- 禁止信息堆叠，必须分层展示

## 15. Responsive Design
支持 Mobile（优先）、Web、Tablet。

## 16. Performance Requirements
页面加载 <1s，AI结果 <3s，图表渲染 <500ms。

## 17. Design Philosophy
把复杂人生模型变成可理解的视觉导航系统。

## 18. Historical Navigation Page

### 18.1 页面目标
让用户像回放人生时间线一样，回顾已走过的人生时段。

### 18.2 UI结构
```
📍 人生路径总览
   ↓
⏪ 已走大运时间轴（可左右滑动）
   ↓
🔍 关键转折点标注（点击展开详情）
   ↓
📊 模式识别摘要（跨周期对比）
   ↓
➡️ 回到当前导航
```

### 18.3 大运时间轴
- 水平时间轴，从出生到当前
- 每个大运周期为一个卡片段
- 已完成周期用灰色/低饱和度，当前周期高亮
- 周期标注：年龄范围 + 大运干支 + 核心主题

### 18.4 关键转折点
- 自动标注：大运切换点、五行结构变化、人生阶段跨越
- 点击展开：该转折点的结构说明
- 图标区分：🔄 大运切换、⚡ 结构变化、📍 阶段跨越

### 18.5 模式识别摘要
- 对比已走完的运气周期
- 识别重复出现的结构特征
- 一句话路径总结

### 18.6 交互规则
- 默认展示完整时间轴
- 点击任一周期可展开详情
- 底部提供「回到当前」按钮
- 支持从历史周期直接跳转到当前决策界面

### 18.7 UI形式
- 水平时间轴（horizontal timeline）
- 可折叠卡片
- 趋势线变化图

## 19. Extension (V2)
人生地图模式（Life Map UI）、时间轨迹动画、决策模拟可视化、多人生对比视图。
