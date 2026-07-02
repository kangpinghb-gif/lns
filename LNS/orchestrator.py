"""
System Orchestrator (15) — 系统编排与调用链

职责：将 Calendar/BaZi/State/KG/Time/Decision/Prompt 串联为完整闭环。

核心数据流（双模式）：
  UserInput → Calendar(Birth) → BaZi(Birth) → StaticChart ──┐
              Calendar(Target) → BaZi(Target) → CurrentCycle ─┼─→ State → KG → Synthesizer
                                                                  → Time → Decision → Prompt → Output
"""

from datetime import datetime, date
from typing import Optional, List

from models.core import (
    UserInput, TargetTime, BirthPlace,
    CalendarOutput, BaZiOutput, StateOutput,
    KnowledgeGraphInput, KnowledgeGraphOutput,
    SynthesizedOutput, TimeOutput, DecisionOutput,
    PromptInput,
)
from engine.calendar.engine import CalendarEngine
from engine.bazi.engine import BaZiEngine
from engine.state.engine import StateEngine
from engine.knowledge_graph.engine import KnowledgeGraph
from engine.state_synthesizer.engine import StateSynthesizer
from engine.time.engine import TimeEngine
from engine.decision.engine import DecisionEngine
from engine.prompt.engine import PromptEngine


class LNSError(Exception):
    """LNS 系统异常"""
    def __init__(self, code: str, message: str, stage: str = ""):
        self.code = code
        self.message = message
        self.stage = stage
        super().__init__(f"[{code}] {message} (stage: {stage})")


class LNSTracer:
    """LNS 请求追踪器"""

    def __init__(self):
        self.trace_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.logs: List[dict] = []

    def log(self, stage: str, status: str, data: any = None):
        self.logs.append({
            "stage": stage,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "data_preview": str(data)[:100] if data else "",
        })

    def summary(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "steps": len(self.logs),
            "logs": self.logs,
        }


class LNSOrchestrator:
    """
    LNS 系统编排器 — 所有引擎的入口和调度器。

    使用方式：
        orchestrator = LNSOrchestrator()
        result = orchestrator.full_analysis(user_input)
    """

    def __init__(self):
        self.calendar = CalendarEngine()
        self.bazi = BaZiEngine()
        self.state = StateEngine()
        self.knowledge_graph = KnowledgeGraph()
        self.synthesizer = StateSynthesizer()
        self.time = TimeEngine()
        self.decision = DecisionEngine()
        self.prompt = PromptEngine()

    def full_analysis(self, user_input: UserInput,
                      target_time: Optional[TargetTime] = None,
                      age: float = 25.0,
                      use_professional_mode: bool = False) -> dict:
        """
        完整人生分析流水线。

        流程：
        1. Calendar Engine (Birth) → 出生时间标准化
        2. BaZi Engine (Birth) → 静态命盘
        3. Calendar Engine (Target) → 目标时间标准化
        4. BaZi Engine (Target) → 当前流年/流日
        5. State Engine → 人生状态
        6. Knowledge Graph → 语义映射
        7. State Synthesizer → 冲突消解
        8. Time Engine → 时间分析 (T0-T3)
        9. Decision Engine → P0-P3
        10. Prompt Engine → AI Prompt

        Returns: dict 包含所有中间数据和最终输出
        """
        tracer = LNSTracer()

        try:
            # ── Step 1: Calendar Birth ─────────────────────
            cal_birth = self.calendar.process(
                birth_date=user_input.birth_date,
                birth_time=user_input.birth_time,
                birth_place=user_input.birth_place,
                timezone_str=user_input.timezone,
                use_true_solar=use_professional_mode,
            )
            tracer.log("calendar_birth", "ok", cal_birth.solar_datetime)

            # ── Step 2: BaZi Birth ─────────────────────────
            bazi_birth = self.bazi.process(cal_birth, user_input.gender)
            tracer.log("bazi_birth", "ok",
                       f"{bazi_birth.four_pillars.year.heavenly_stem}{bazi_birth.four_pillars.year.earthly_branch}")

            # ── Step 3: Calendar Target ────────────────────
            if target_time is None:
                target_time = TargetTime(
                    date=datetime.now().strftime("%Y-%m-%d"),
                    time=datetime.now().strftime("%H:%M"),
                )
            cal_target = self.calendar.process(
                birth_date=target_time.date,
                birth_time=target_time.time,
                birth_place=user_input.birth_place,
                timezone_str=user_input.timezone,
                use_true_solar=False,
            )
            tracer.log("calendar_target", "ok", cal_target.solar_datetime)

            # ── Step 4: BaZi Target ────────────────────────
            bazi_target = self.bazi.process(cal_target, user_input.gender)
            tracer.log("bazi_target", "ok",
                       f"{bazi_target.four_pillars.year.heavenly_stem}{bazi_target.four_pillars.year.earthly_branch}")

            # ── Step 5: State Engine ───────────────────────
            state_result = self.state.process(bazi_birth, age=age)
            tracer.log("state", "ok", state_result.current_stage)

            # ── Step 6: Knowledge Graph ────────────────────
            kg_input = KnowledgeGraphInput(
                four_pillars=bazi_birth.four_pillars,
                ten_gods=bazi_birth.ten_gods,
                five_elements=bazi_birth.five_elements,
                normalized_elements=bazi_birth.normalized_elements,
                hidden_stems=bazi_birth.hidden_stems,
                luck_cycles=bazi_birth.luck_cycles,
                state_context={
                    "current_stage": state_result.current_stage,
                    "energy_level": state_result.energy_level,
                    "risk_level": state_result.risk_level,
                    "dominant_structure": state_result.dominant_structure,
                },
            )
            kg_result = self.knowledge_graph.process(kg_input)
            tracer.log("knowledge_graph", "ok", f"{len(kg_result.behavior_model)} behaviors")

            # ── Step 7: State Synthesizer ──────────────────
            synth_result = self.synthesizer.process(
                kg_result,
                bazi_birth.normalized_elements,
                state_result.energy_level,
            )
            tracer.log("synthesizer", "ok", synth_result.dominant_profile)

            # ── Step 8: Time Engine ────────────────────────
            time_result = self.time.process(
                birth_state=state_result,
                current_bazi=bazi_target,
                target_date=target_time.date,
                behavior_patterns=state_result.behavior_patterns,
            )
            tracer.log("time", "ok",
                       f"T0_energy={time_result.T0.energy_state}")

            # ── Step 9: Decision Engine ────────────────────
            decision_result = self.decision.process(
                state=state_result,
                time_output=time_result,
                synthesized=synth_result,
            )
            tracer.log("decision", "ok",
                       f"P0={len(decision_result.P0)} P1={len(decision_result.P1)}")

            # ── Step 10: Prompt Engine (optional) ──────────
            prompt_input = PromptInput(
                state=state_result,
                time=time_result,
                decision=decision_result,
                knowledge_graph=synth_result,
            )
            prompt = self.prompt.process(prompt_input)
            tracer.log("prompt", "ok", f"prompt length: {len(prompt)}")

            # ── 聚合结果 ──────────────────────────────────
            result = {
                "success": True,
                "trace_id": tracer.trace_id,
                "tracer": tracer.summary(),
                "data": {
                    "calendar_birth": self._calendar_to_dict(cal_birth),
                    "bazi_birth": self._bazi_to_dict(bazi_birth),
                    "state": self._state_to_dict(state_result),
                    "knowledge_graph": self._kg_to_dict(kg_result),
                    "synthesized": self._synth_to_dict(synth_result),
                    "time": self._time_to_dict(time_result),
                    "decision": self._decision_to_dict(decision_result),
                },
                "prompt": prompt,
                "system_status": "ready",
            }
            return result

        except Exception as e:
            tracer.log("error", "failed", str(e))
            return {
                "success": False,
                "trace_id": tracer.trace_id,
                "tracer": tracer.summary(),
                "error": {
                    "code": "PIPELINE_ERROR",
                    "message": str(e),
                    "stage": tracer.logs[-1]["stage"] if tracer.logs else "unknown",
                },
            }

    def chat(self, user_input: UserInput,
             message: str,
             target_time: Optional[TargetTime] = None,
             age: float = 25.0) -> dict:
        """
        AI 对话入口。
        """
        # 先做完整分析
        analysis = self.full_analysis(user_input, target_time, age)
        if not analysis["success"]:
            return analysis

        # 检测意图
        intent = self.prompt.detect_intent(message)

        if intent == "emotion":
            # 情绪分流模式
            emotion_response = self.prompt.format_emotion_response(
                StateOutput(**analysis["data"]["state"])
                if isinstance(analysis["data"]["state"], dict)
                else analysis["data"]["state"]
            )
            return {
                "success": True,
                "mode": "emotion_triage",
                "response": emotion_response,
                "footer": self.prompt.format_ai_footer(),
            }

        # 标准决策模式
        analysis["data"]["user_query"] = message
        return analysis

    # ── 序列化辅助方法 ─────────────────────────────────

    def _calendar_to_dict(self, cal: CalendarOutput) -> dict:
        return {
            "solar_datetime": cal.solar_datetime,
            "lunar_datetime": cal.lunar_datetime,
            "timezone": cal.timezone,
            "solar_term": {
                "name": cal.solar_term.name,
                "transition_timestamp": cal.solar_term.transition_timestamp,
                "is_before_transition": cal.solar_term.is_before_transition,
            },
        }

    def _bazi_to_dict(self, bazi: BaZiOutput) -> dict:
        return {
            "four_pillars": {
                "year": {"stem": bazi.four_pillars.year.heavenly_stem, "branch": bazi.four_pillars.year.earthly_branch},
                "month": {"stem": bazi.four_pillars.month.heavenly_stem, "branch": bazi.four_pillars.month.earthly_branch},
                "day": {"stem": bazi.four_pillars.day.heavenly_stem, "branch": bazi.four_pillars.day.earthly_branch},
                "hour": {"stem": bazi.four_pillars.hour.heavenly_stem, "branch": bazi.four_pillars.hour.earthly_branch},
            },
            "day_master": bazi.day_master,
            "ten_gods": bazi.ten_gods,
            "normalized_elements": bazi.normalized_elements,
            "luck_cycles": [
                {
                    "age_range": cycle.age_range,
                    "pillar": cycle.pillar,
                    "heavenly_stem": cycle.heavenly_stem,
                    "earthly_branch": cycle.earthly_branch,
                }
                for cycle in bazi.luck_cycles
            ],
            "start_age": bazi.start_age,
            "deities": bazi.deities,
        }

    def _state_to_dict(self, state: StateOutput) -> dict:
        return {
            "current_stage": state.current_stage,
            "energy_level": state.energy_level,
            "risk_level": state.risk_level,
            "dominant_structure": state.dominant_structure,
            "capability_profile": state.capability_profile,
            "behavior_patterns": state.behavior_patterns,
            "luck_cycle_theme": state.luck_cycle_theme,
        }

    def _kg_to_dict(self, kg: KnowledgeGraphOutput) -> dict:
        return {
            "behavior_model": kg.behavior_model,
            "capability_model": kg.capability_model,
            "career_mapping": kg.career_mapping,
            "risk_model": kg.risk_model,
            "evidence_chain": kg.evidence_chain,
            "reasoning_steps": kg.reasoning_steps,
            "output_version": kg.output_version,
            "output_confidence": kg.output_confidence,
        }

    def _synth_to_dict(self, synth: SynthesizedOutput) -> dict:
        return {
            "synthesized_behavior": synth.synthesized_behavior,
            "synthesized_career": synth.synthesized_career,
            "synthesized_risk": synth.synthesized_risk,
            "dominant_profile": synth.dominant_profile,
            "confidence_score": synth.confidence_score,
            "evidence_chain": synth.evidence_chain,
            "reasoning_steps": synth.reasoning_steps,
        }

    def _time_to_dict(self, time_output: TimeOutput) -> dict:
        return {
            "T0": {
                "energy_state": time_output.T0.energy_state,
                "recommended_focus": time_output.T0.recommended_focus,
                "risk": time_output.T0.risk,
            },
            "T1": {
                "monthly_trend": time_output.T1.monthly_trend,
                "opportunities": time_output.T1.opportunities,
                "risks": time_output.T1.risks,
            },
            "T2": {
                "yearly_direction": time_output.T2.yearly_direction,
                "strategic_focus": time_output.T2.strategic_focus,
                "risk_level": time_output.T2.risk_level,
            },
            "T3": {
                "life_stage": time_output.T3.life_stage,
                "long_term_direction": time_output.T3.long_term_direction,
                "strategic_path": time_output.T3.strategic_path,
            },
        }

    def _decision_to_dict(self, decision: DecisionOutput) -> dict:
        return {
            "P0": [a.description for a in decision.P0],
            "P1": [a.description for a in decision.P1],
            "P2": [a.description for a in decision.P2],
            "P3": [a.description for a in decision.P3],
            "decision_logic": decision.decision_logic,
            "priority_reasoning": decision.priority_reasoning,
        }

    def simulate(self, user_input, scenarios):
        """
        What-if 模拟器：对同一出生信息，在不同时间场景下分别分析。

        Args:
            user_input: UserInput — 基准出生信息
            scenarios: 列表，每个元素为 {"label": "场景名", "target_time": TargetTime, "age": float}

        Returns: {
            "baseline": dict,        # 当前时间
            "scenarios": [           # 每个场景的对比数据
                {"label": str, "time": dict, "state": dict, "decision": dict},
            ]
        }
        """
        baseline = self.full_analysis(user_input, age=scenarios[0].get("age", 35) if scenarios else 35)
        if not baseline["success"]:
            return {"success": False, "error": baseline.get("error")}

        result = {
            "success": True,
            "baseline": {
                "target_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "bazi": self._bazi_to_dict_simple(baseline["data"]["bazi_birth"]),
                "state": baseline["data"]["state"],
                "time": baseline["data"]["time"],
                "decision": baseline["data"]["decision"],
            },
            "scenarios": [],
        }

        for sc in scenarios:
            label = sc.get("label", "场景")
            target = sc.get("target_time", TargetTime())
            age = sc.get("age", 35)

            user_input.target_time = target
            sc_result = self.full_analysis(user_input, age=age)

            if sc_result["success"]:
                result["scenarios"].append({
                    "label": label,
                    "target_time": f"{target.date} {target.time}",
                    "bazi": self._bazi_to_dict_simple(sc_result["data"]["bazi_birth"]),
                    "state": sc_result["data"]["state"],
                    "time": sc_result["data"]["time"],
                    "decision": sc_result["data"]["decision"],
                })
            else:
                result["scenarios"].append({
                    "label": label,
                    "error": sc_result.get("error"),
                })

        return result

    def _bazi_to_dict_simple(self, bazi_data):
        return {
            "four_pillars": bazi_data.get("four_pillars", {}),
            "day_master": bazi_data.get("day_master", ""),
            "ten_gods": bazi_data.get("ten_gods", {}),
            "normalized_elements": bazi_data.get("normalized_elements", {}),
            "deities": bazi_data.get("deities", []),
        }
