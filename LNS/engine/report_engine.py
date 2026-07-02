"""
LNS 报告生成器 — Report Engine

参考 17-Output-Specification.md（L4 报告输出）。

报告类型：
  - 日报 (daily)：今日状态 + 行动建议
  - 月报 (monthly)：月度趋势 + 机会风险
  - 年报 (yearly)：年度方向 + 结构变化
  - 大运报告 (decade)：10年人生结构
"""
from datetime import datetime
from typing import Optional, List, Dict, Any


class ReportEngine:
    """报告生成器 — 将上游引擎数据组装为结构化报告"""

    def generate(self, state, time_output, decision, synthesized,
                 report_type="daily", target_date=None):
        """
        生成报告。

        Args:
            state: StateOutput
            time_output: TimeOutput
            decision: DecisionOutput
            synthesized: SynthesizedOutput
            report_type: daily / monthly / yearly / decade
            target_date: 目标日期

        Returns: dict 报告内容
        """
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")

        generators = {
            "daily": self._daily_report,
            "monthly": self._monthly_report,
            "yearly": self._yearly_report,
            "decade": self._decade_report,
        }

        gen = generators.get(report_type)
        if not gen:
            return {"error": f"Unknown report type: {report_type}"}

        return gen(state, time_output, decision, synthesized, target_date)

    def _daily_report(self, state, time_output, decision, synthesized, target_date):
        """日报生成"""
        T0 = time_output.T0
        T1 = time_output.T1
        T2 = time_output.T2

        content = {
            "title": f"人生导航日报 · {target_date}",
            "generated_at": datetime.now().isoformat(),
            "type": "daily",
            "overview": {
                "stage": state.current_stage,
                "energy": T0.energy_state,
                "risk": state.risk_level,
                "dominant": state.dominant_structure,
            },
            "daily_state": {
                "energy_state": T0.energy_state,
                "focus_areas": T0.recommended_focus,
                "avoid_actions": T0.avoid_actions,
                "risks": T0.risk,
            },
            "actions": {
                "P0": [{"description": a.description, "reason": a.reason} for a in decision.P0],
                "P1": [{"description": a.description, "reason": a.reason} for a in decision.P1],
                "P2": [{"description": a.description, "reason": a.reason} for a in decision.P2],
            },
            "monthly_context": {
                "trend": T1.monthly_trend,
                "opportunities": T1.opportunities,
                "monthly_risks": T1.risks,
            },
            "profile": {
                "dominant_profile": synthesized.dominant_profile,
                "behaviors": synthesized.synthesized_behavior,
            },
            "reasoning": decision.priority_reasoning,
        }
        return content

    def _monthly_report(self, state, time_output, decision, synthesized, target_date):
        """月报生成"""
        T1 = time_output.T1
        T2 = time_output.T2
        year_month = target_date[:7]

        content = {
            "title": f"人生导航月报 · {year_month}",
            "generated_at": datetime.now().isoformat(),
            "type": "monthly",
            "overview": {
                "stage": state.current_stage,
                "energy": state.energy_level,
                "risk": state.risk_level,
                "dominant": state.dominant_structure,
            },
            "monthly_trend": {
                "trend": T1.monthly_trend,
                "opportunities": T1.opportunities,
                "risks": T1.risks,
                "recommended_focus": T1.recommended_focus,
            },
            "yearly_context": {
                "direction": T2.yearly_direction,
                "strategic_focus": T2.strategic_focus,
            },
            "actions": {
                "P0": [a.description for a in decision.P0],
                "P1": [a.description for a in decision.P1],
                "P2": [a.description for a in decision.P2],
            },
            "profile": {
                "capabilities": state.capability_profile,
                "behaviors": state.behavior_patterns,
                "environment": state.environment_tendency,
            },
            "reasoning": decision.priority_reasoning,
        }
        return content

    def _yearly_report(self, state, time_output, decision, synthesized, target_date):
        """年报生成"""
        T2 = time_output.T2
        T3 = time_output.T3
        year = target_date[:4]

        content = {
            "title": f"人生导航年报 · {year}年",
            "generated_at": datetime.now().isoformat(),
            "type": "yearly",
            "overview": {
                "stage": state.current_stage,
                "energy": state.energy_level,
                "risk": state.risk_level,
                "dominant": state.dominant_structure,
            },
            "yearly_direction": {
                "direction": T2.yearly_direction,
                "structural_shift": T2.structural_shift,
                "strategic_focus": T2.strategic_focus,
                "avoidance": T2.avoidance_strategy,
            },
            "decade_context": {
                "life_stage": T3.life_stage,
                "long_term_direction": T3.long_term_direction,
                "strategic_path": T3.strategic_path,
            },
            "key_actions": {
                "P0": [a.description for a in decision.P0],
                "P1": [a.description for a in decision.P1],
            },
            "capability_analysis": {
                "capabilities": state.capability_profile,
                "luck_cycle_theme": state.luck_cycle_theme,
            },
            "risk_analysis": {
                "level": state.risk_level,
                "constraints": state.constraints,
                "synthesized_risks": synthesized.synthesized_risk,
            },
        }
        return content

    def _decade_report(self, state, time_output, decision, synthesized, target_date):
        """大运报告（10年）"""
        T3 = time_output.T3
        T_minus_1 = time_output.T_minus_1

        content = {
            "title": f"人生导航大运报告 · 10年结构分析",
            "generated_at": datetime.now().isoformat(),
            "type": "decade",
            "overview": {
                "stage": state.current_stage,
                "stage_derivation": state.stage_derivation,
                "dominant": state.dominant_structure,
                "luck_cycle_theme": state.luck_cycle_theme,
            },
            "decade_structure": {
                "life_stage": T3.life_stage,
                "long_term_direction": T3.long_term_direction,
                "structural_advantage": T3.structural_advantage,
                "structural_risk": T3.structural_risk,
                "strategic_path": T3.strategic_path,
            },
            "historical_retrospect": {
                "timeline": [{
                    "period": item.period,
                    "life_stage": item.life_stage,
                    "key_theme": item.key_theme,
                } for item in (T_minus_1.timeline if hasattr(T_minus_1, 'timeline') else [])],
                "repeating_patterns": T_minus_1.repeating_patterns,
                "path_summary": T_minus_1.path_summary,
            },
            "capability_evolution": {
                "capabilities": state.capability_profile,
                "behaviors": state.behavior_patterns,
                "development_direction": state.development_direction,
            },
            "long_term_strategy": T3.strategic_path,
        }
        return content
