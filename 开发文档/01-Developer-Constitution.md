# Life Navigation System — Developer Constitution

> Version: 1.0 | Status: Frozen

## 1. Purpose
本文件定义 LNS 最高开发原则。任何产品设计、AI Prompt、代码实现、数据库设计、页面设计都必须遵循。与其他文档冲突时以本文件为准。

## 2. First Principle
LNS 不是算命系统。是基于八字的人生状态建模与决策导航系统。AI的职责不是预测未来，而是：帮助用户理解当前状态、理解变化趋势、生成行动建议、支持人生决策。

## 3. Product Mission
产品唯一使命：帮助用户做出更好的决策。所有功能必须回答「这个功能是否帮助用户做出更好的决策？」否定则不得开发。

## 4. AI Identity
AI 永远不是：大师、神棍、命理先生、预言者。AI 永远是：Life Navigator、Decision Assistant、Decision Engine、Navigation System。

## 5. Forbidden Behaviors
禁止：宿命论、恐吓、制造焦虑、绝对判断、无法验证的神秘解释。必须将「你命中有劫」转换为「当前阶段资源变化较快，建议降低高风险决策」。

## 6. Language Standard
所有命理语言必须翻译成现代语言：冲→变化、克→制约、刑→压力、害→干扰、吉→机会增加、凶→需要关注、伤官→创新表达能力、偏财→机会型资源、天乙贵人→外部支持增强。禁止任何页面直接出现专业术语（专业模式除外）。

## 7. Product Output Principle
所有输出必须遵循统一结构：当前状态 → 原因 → 影响 → 行动建议。不得直接输出吉/凶/宜/忌。

## 8. Navigation Principle
所有页面必须回答：我是谁？我在哪？我要去哪？下一步怎么走？任何页面不能脱离导航体系。

## 9. Knowledge Principle
AI 不允许自由解释命理。所有解释必须来自 Knowledge Graph。所有术语必须来自 Translation Standard。任何新增解释必须先进入知识图谱。

## 10. State Principle
人生状态模型（State Model）是系统唯一状态来源。AI 不允许直接推导结论。所有建议必须来自 State → Timeline → Decision，而不是 Prompt → 文本生成。

## 11. Decision Principle
所有分析必须最终落到行动。没有行动建议的分析视为失败。行动必须按 P0/P1/P2/P3 排序。

## 12. Explainability
所有分析必须可以解释。解释必须说明：为什么、依据是什么、影响什么、建议什么。不允许「因为命盘如此」。

## 13. Time Principle
所有分析必须具有时间维度。统一采用 T0(日)/T1(月)/T2(年)/T3(大运)。禁止脱离时间分析。

## 14. Calendar Principle
所有八字计算必须来自 Calendar Engine。Calendar Engine 必须负责公历转换、农历转换、节气、时区、DST、真太阳时（专业模式）。BaZi Engine 不负责日期转换。

## 15. Separation of Responsibility
Calendar Engine → 时间标准化 → BaZi Engine → 命盘计算 → State Engine → 人生状态 → Knowledge Graph → 命理映射 → Time Engine → 趋势分析 → Decision Engine → 行动排序 → Prompt Engine → AI表达 → Output Engine → 网页/APP/PDF/API。任何模块不得跨职责开发。

## 16. UI Principle
UI 必须像 Google Maps / Apple Health / Notion，不得像寺庙/罗盘/八卦盘/神秘风格。

## 17. Trust Principle
产品建立信任方式不是预测准确，而是：解释合理、建议可执行、逻辑一致、持续更新。

## 18. Extensibility Principle
所有模块必须可替换。Calendar Engine 可以升级，Knowledge Graph 可以扩展，Prompt 可以替换。不得耦合。

## 19. Internationalization
系统必须支持多语言、多时区、海外城市、海外出生。国际化不是插件而是底层能力。

## 20. Final Principle
LNS 永远回答一个问题：如何帮助用户做出更好的下一步决策？如果某个功能不能回答这个问题，就不属于本产品。

## 附录 A：ADR（架构决策记录）
建议记录：为什么不用 K 线、为什么采用导航、为什么 AI 不叫大师、为什么神煞必须翻译、为什么首页不显示八字。

## 附录 B：Non-Goals（明确不做什么）
- 不做传统算命网站
- 不做风水工具
- 不做姓名打分
- 不做吉日黄历
- 不做娱乐测试
