"""
Time Engine (08) — 时间分析系统

职责：在人生状态模型基础上，构建时间驱动的变化系统。
回答「你在不同时间尺度下如何变化」。

核心原则：
- 不做预测命运。只做时间节奏分析、状态变化模拟、趋势结构表达。
- 输出 focus areas（关注领域），不输出 P0-P3（由 Decision Engine 负责）。
- 时间漏斗机制：T3→T2→T1→T0 自上而下约束投影。

数据流：
  StateOutput + BaZiOutput(current) → LuckCycleEngine → TemporalMappingEngine
  → TrendDetectionEngine → OpportunityAnalyzer → RiskAnalyzer
  → TimeLayerOutput(T0-T3)
"""

from datetime import datetime, date
from typing import Optional

from models.core import (
    StateOutput, BaZiOutput, TimeOutput,
    T0Layer, T1Layer, T2Layer, T3Layer,
    TMinus1Layer, TMinus1Item,
)
from models.constants import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES,
    STEMS_TO_ELEMENT, BRANCHES_TO_ELEMENT,
    HIDDEN_STEMS_WEIGHTS,
)


# ── 五行生克关系 ─────────────────────────────────────────

GENERATING_CYCLE = {"wood": "fire", "fire": "earth", "earth": "metal", "metal": "water", "water": "wood"}
OVERRIDING_CYCLE = {"wood": "earth", "earth": "water", "water": "fire", "fire": "metal", "metal": "wood"}


class TimeEngine:
    """
    Time Engine — 多时间尺度分析引擎。
    """

    def process(self, birth_state: StateOutput,
                current_bazi: BaZiOutput,
                target_date: Optional[str] = None,
                behavior_patterns: Optional[list] = None) -> TimeOutput:
        """
        生成完整时间分析。

        Args:
            birth_state: 用户状态（出生命盘状态）
            current_bazi: 当前时间的八字
            target_date: 目标日期 YYYY-MM-DD
            behavior_patterns: 行为模式

        Returns: TimeOutput (T-1, T0, T1, T2, T3)
        """
        result = TimeOutput()

        # T3: 10年大运层
        result.T3 = self._calc_T3(birth_state)

        # T2: 年层
        result.T2 = self._calc_T2(birth_state, current_bazi)

        # T1: 月层
        result.T1 = self._calc_T1(birth_state, current_bazi)

        # T0: 日层
        result.T0 = self._calc_T0(birth_state, current_bazi)

        # T-1: 历史回顾层
        result.T_minus_1 = self._calc_T_minus_1(birth_state)

        # 应用时间漏斗约束
        self._apply_funnel_constraint(result)

        return result

    def _calc_T3(self, state: StateOutput) -> T3Layer:
        """大运层 (10年)"""
        layer = T3Layer()
        layer.life_stage = state.current_stage

        # 长期方向
        direction = state.development_direction
        layer.long_term_direction = direction.get("recommended_direction", [])[:3]

        # 结构优势
        if state.dominant_structure:
            layer.long_term_direction.append(f"当前{state.dominant_structure}结构")

        # 结构风险
        if state.risk_level == "high":
            layer.strategic_path.append("降低风险敞口")
            layer.strategic_path.append("建立缓冲机制")
        elif state.risk_level == "elevated":
            layer.strategic_path.append("平衡风险与机会")
            layer.strategic_path.append("关注结构性问题")

        # 长期策略
        if state.energy_level == "high":
            layer.strategic_path.append("利用高能量期推进核心目标")
        elif state.energy_level == "low":
            layer.strategic_path.append("聚焦精力，减少分散投入")

        return layer

    def _calc_T2(self, state: StateOutput, current_bazi: BaZiOutput) -> T2Layer:
        """年层"""
        layer = T2Layer()

        # 年度方向来自状态
        year_pillar = current_bazi.four_pillars.year
        year_stem_elem = STEMS_TO_ELEMENT.get(year_pillar.heavenly_stem, "")
        year_branch_elem = BRANCHES_TO_ELEMENT.get(year_pillar.earthly_branch, "")

        # 年度方向
        direction_parts = []
        if year_stem_elem == year_branch_elem:
            elem_cn = {"wood": "木", "fire": "火", "earth": "土", "metal": "金", "water": "水"}
            direction_parts.append(f"{elem_cn.get(year_stem_elem, '')}能量主导年")
        else:
            direction_parts.append(f"{year_pillar.heavenly_stem}{year_pillar.earthly_branch}年份")

        # 结构变化检测
        luck_theme = state.luck_cycle_theme
        if luck_theme:
            direction_parts.append(f"当前大运主题：{'/'.join(luck_theme)}")

        layer.yearly_direction = "，".join(direction_parts)
        layer.risk_level = state.risk_level

        # 战略关注
        if state.risk_level == "high":
            layer.strategic_focus.append("风险管控优先")
            layer.avoidance_strategy.append("避免重大扩张决策")
        elif state.risk_level == "elevated":
            layer.strategic_focus.append("结构优化")
            layer.avoidance_strategy.append("减少高风险投入")
        else:
            if state.energy_level == "high":
                layer.strategic_focus.append("积极推进核心计划")
            else:
                layer.strategic_focus.append("稳步积累，寻求突破")

        return layer

    def _calc_T1(self, state: StateOutput, current_bazi: BaZiOutput) -> T1Layer:
        """月层"""
        layer = T1Layer()
        month_pillar = current_bazi.four_pillars.month

        month_stem_elem = STEMS_TO_ELEMENT.get(month_pillar.heavenly_stem, "")
        month_branch_elem = BRANCHES_TO_ELEMENT.get(month_pillar.earthly_branch, "")

        # 月度趋势
        # 天干地支五行生克关系判断趋势
        if month_stem_elem and month_branch_elem:
            # 生入日主→向上
            if month_stem_elem == month_branch_elem:
                layer.monthly_trend = "up"
                layer.opportunities.append(f"{month_stem_elem}能量集中，适合推进相关事务")
            # 相生→稳定
            elif GENERATING_CYCLE.get(month_stem_elem) == month_branch_elem:
                layer.monthly_trend = "stable"
            # 相克→波动
            elif OVERRIDING_CYCLE.get(month_stem_elem) == month_branch_elem:
                layer.monthly_trend = "down"
                layer.risks.append("月中结构冲突，注意决策节奏")

        # 基于状态补充
        if state.energy_level == "high":
            layer.opportunities.append("能量充沛期，适合攻克难点")
        elif state.energy_level == "low":
            layer.risks.append("能量偏低，建议减少非必要消耗")

        return layer

    def _calc_T0(self, state: StateOutput, current_bazi: BaZiOutput) -> T0Layer:
        """日层"""
        layer = T0Layer()
        day_pillar = current_bazi.four_pillars.day

        # 日柱分析
        day_stem_elem = STEMS_TO_ELEMENT.get(day_pillar.heavenly_stem, "")
        day_branch_elem = BRANCHES_TO_ELEMENT.get(day_pillar.earthly_branch, "")

        # 能量状态（与状态引擎一致）
        layer.energy_state = state.energy_level

        # 关注领域
        if state.energy_level == "high":
            layer.recommended_focus.append("启动需要高强度投入的任务")
            layer.recommended_focus.append("主动推进关键决策")
        elif state.energy_level == "low":
            layer.recommended_focus.append("优先完成高优先级事项")
            layer.recommended_focus.append("减少社交性消耗")
        else:
            layer.recommended_focus.append("按计划推进常规事务")

        # 风险提示
        if state.risk_level == "high":
            layer.risk.append("整体风险较高，今日避免重大决策")
        elif state.risk_level == "elevated":
            layer.risk.append("需注意风险信号，重要事项需多方确认")

        # 避免行动
        if state.energy_level == "low":
            layer.avoid_actions.append("避免多任务并行")
            layer.avoid_actions.append("避免冲动决策")

        return layer

    def _calc_T_minus_1(self, state: StateOutput) -> TMinus1Layer:
        """
        历史回顾层 (T-1)。

        职责：不预测、不做事后算命。
        只做：已走过大运的结构化回顾、关键转折点标注、人生路径模式识别。
        """
        layer = TMinus1Layer()
        # V1 简化实现
        if state.luck_cycle_theme:
            theme = state.luck_cycle_theme[0]
            layer.timeline.append(TMinus1Item(
                period="当前大运",
                life_stage=state.current_stage,
                key_theme=theme,
                structural_shift=False,
            ))
        return layer

    def _apply_funnel_constraint(self, output: TimeOutput) -> None:
        """
        时间漏斗约束：宏观约束微观。
        T3→T2→T1→T0 自上而下。
        """
        # T2 高风险 → T0 风险级别不低于 T2
        if output.T2.risk_level == "high":
            if not output.T0.risk:
                output.T0.risk.append("年度高风险期，注意整体节奏控制")
        elif output.T2.risk_level == "elevated":
            output.T0.risk.append("年度处于结构性调整期")

        # T3 冲突期 → T0 必须包含 T3 风险提示
        if output.T3.structural_risk:
            for r in output.T3.structural_risk[:1]:
                output.T0.risk.append(f"长期提醒：{r}")
