"""
Prompt Engine (10) — AI 控制层

职责：将所有上游结构化数据（State / Time / Decision / Knowledge Graph）
转换为稳定、可控、不可胡说的 AI 输出。

核心原则：不创造知识。只做三件事：组织信息、限制输出、强制结构。

数据流：
  PromptInput → StateContextInjection → TimeContextInjection
  → DecisionContextInjection → KnowledgeGraphInjection
  → PromptAssembly → LLMGeneration → OutputValidator
"""

from typing import Optional

from models.core import (
    StateOutput, TimeOutput, DecisionOutput, SynthesizedOutput,
    PromptInput,
)


# ── 情绪分流关键词库 ─────────────────────────────────────

EMOTION_KEYWORDS = [
    "心情", "难受", "开心", "郁闷", "压力大", "累了",
    "烦", "没劲", "无聊", "不爽",
]

DECISION_KEYWORDS = [
    "工作", "换", "创业", "投资", "感情", "学习", "建议",
    "选择", "辞职", "分手", "结婚", "买房", "跳槽", "方向",
    "迷茫",
]


class PromptEngine:
    """
    Prompt Engine — AI 行为约束与输出格式控制。

    包含：
    - 四段式结构强制：当前状态 → 时间影响 → 行动建议 → 原因解释
    - 情绪分流（Emotion Triage Router）
    - 输出校验
    """

    def __init__(self):
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """系统提示层"""
        return """You are Life Navigation AI.
You are NOT a fortune teller.
You are NOT a mystic.
You are NOT a prophet.
You are a Life Navigator.

Your job:
- Explain current state based on structured data
- Explain time impact
- Provide decision actions with priorities (P0-P3)

CORE RULES:
1. NEVER give "吉/凶" (luck/unluck) judgments
2. NEVER say "命中注定" (fated) or "天命" (destiny)
3. NEVER scare users with predictions
4. ALWAYS provide actionable advice
5. ALWAYS explain the reasoning
6. NEVER free-interpret metaphysical concepts
7. All advice must be based on the data provided, not your own knowledge

OUTPUT FORMAT - Strict 4-part structure:
1. 当前状态 (Current State) — based on State Engine data
2. 时间影响 (Time Impact) — based on Time Engine data
3. 行动建议 P0-P3 (Action Recommendations) — based on Decision Engine data
4. 原因解释 (Reasoning) — why this advice makes sense

FORBIDDEN WORDS: 命中注定, 天命, 大凶, 必然, 一定发财, 一定离婚, 灾难, 倒霉, 走运"""

    def process(self, prompt_input: PromptInput) -> str:
        """
        组装完整 Prompt。

        Args:
            prompt_input: 包含 State/Time/Decision/KG/UserQuery 的综合输入

        Returns: 组装好的 Prompt（可直接发送给 LLM）
        """
        parts = []

        # System Prompt
        parts.append(self.system_prompt)

        # 状态数据
        parts.append(self._format_state(prompt_input.state))

        # 时间数据
        parts.append(self._format_time(prompt_input.time))

        # 决策数据
        parts.append(self._format_decision(prompt_input.decision))

        # 知识图谱数据
        parts.append(self._format_knowledge(prompt_input.knowledge_graph))

        # 用户问题
        if prompt_input.user_query:
            parts.append(f"\n## User Query\n{prompt_input.user_query}")

        return "\n\n".join(parts)

    def detect_intent(self, user_query: str) -> str:
        """
        情绪分流 - 意图检测。

        Returns:
            "decision" — 走标准决策流程
            "emotion" — 走情绪分流模式
        """
        query_lower = user_query.lower()

        has_decision = any(kw in user_query for kw in DECISION_KEYWORDS)
        has_emotion = any(kw in user_query for kw in EMOTION_KEYWORDS)

        if has_decision:
            return "decision"
        if has_emotion and not has_decision:
            return "emotion"
        # 两者都命中或都没命中 → 默认走决策流程
        return "decision"

    def format_emotion_response(self, state: StateOutput) -> str:
        """情绪分流模式输出（1句客观状态解析 + 1句共情）"""
        energy = state.energy_level
        stage = state.current_stage

        state_desc = {
            "high": "当前能量充沛",
            "medium": "当前能量状态平稳",
            "low": "当前能量偏内收",
        }.get(energy, "当前状态平稳")

        return f"""## 当前状态
{state_desc}，正处于{stage}。

## 温馨提示
理解您现在的感受。每个人都会有起伏，系统数据显示这只是阶段性的能量波动。状态的调整需要时间，建议先给自己一些空间。"""

    def format_ai_footer(self) -> str:
        """AI 输出强制免责注入"""
        return "> ⚖️ 导航员提示：本建议基于当前状态模型推演。人生最终决定权与风险完全由您掌控。"

    def _format_state(self, state: StateOutput) -> str:
        """格式化状态数据"""
        lines = ["## State Engine Data"]
        lines.append(f"- Current Stage: {state.current_stage}")
        lines.append(f"- Energy Level: {state.energy_level}")
        lines.append(f"- Risk Level: {state.risk_level}")
        lines.append(f"- Dominant Structure: {state.dominant_structure}")
        if state.capability_profile:
            lines.append(f"- Capabilities: {', '.join(state.capability_profile)}")
        if state.behavior_patterns:
            lines.append(f"- Behaviors: {', '.join(state.behavior_patterns)}")
        return "\n".join(lines)

    def _format_time(self, time_output: TimeOutput) -> str:
        """格式化时间数据"""
        lines = ["## Time Engine Data"]
        # T0
        lines.append(f"- T0 (Daily): energy={time_output.T0.energy_state}")
        if time_output.T0.recommended_focus:
            lines.append(f"  Focus: {', '.join(time_output.T0.recommended_focus)}")
        if time_output.T0.risk:
            lines.append(f"  Risks: {', '.join(time_output.T0.risk)}")
        # T1
        lines.append(f"- T1 (Monthly): trend={time_output.T1.monthly_trend}")
        if time_output.T1.opportunities:
            lines.append(f"  Opportunities: {', '.join(time_output.T1.opportunities)}")
        # T2
        lines.append(f"- T2 (Yearly): {time_output.T2.yearly_direction}")
        # T3
        lines.append(f"- T3 (Decade): stage={time_output.T3.life_stage}")
        return "\n".join(lines)

    def _format_decision(self, decision: DecisionOutput) -> str:
        """格式化决策数据"""
        lines = ["## Decision Engine Data"]
        if decision.P0:
            lines.append(f"- P0 (Immediate): {' | '.join(a.description for a in decision.P0)}")
        if decision.P1:
            lines.append(f"- P1 (Important): {' | '.join(a.description for a in decision.P1)}")
        if decision.P2:
            lines.append(f"- P2 (Optimization): {' | '.join(a.description for a in decision.P2)}")
        if decision.P3:
            lines.append(f"- P3 (Optional): {' | '.join(a.description for a in decision.P3)}")
        return "\n".join(lines)

    def _format_knowledge(self, kg: SynthesizedOutput) -> str:
        """格式化知识图谱数据"""
        lines = ["## Knowledge Graph Data"]
        if kg.synthesized_behavior:
            lines.append(f"- Behaviors: {', '.join(kg.synthesized_behavior)}")
        if kg.synthesized_career:
            lines.append(f"- Career paths: {', '.join(kg.synthesized_career)}")
        if kg.synthesized_risk:
            lines.append(f"- Risk factors: {', '.join(kg.synthesized_risk)}")
        lines.append(f"- Profile: {kg.dominant_profile}")
        return "\n".join(lines)

    def validate_output(self, text):
        """
        输出校验器。

        检查输出是否包含必要的决策导航元素。
        宽松策略：只要内容非空且有实质性内容就算通过。
        """
        if not text or len(text.strip()) < 10:
            return False

        text_lower = text.lower()
        checks = {
            "has_P0": any(p in text for p in ("P0", "P1", "P2", "P3", "立即", "重要", "优化", "探索")),
            "has_action": any(kw in text for kw in ("建议", "执行", "关注", "推荐", "行动",
                                                     "suggest", "recommend", "action")),
            "has_time": any(kw in text for kw in ("T0", "T1", "T2", "T3", "时间", "今日", "当前",
                                                   "每日", "每月", "每年")),
        }

        # 宽松：至少满足 1 项就算通过
        return any(checks.values())

    def build_data_card(self, decision):
        """
        兜底数据卡片模式
        """
        return {
            "mode": "data_card",
            "message": "主控系统已切换至安全数据决策模式",
            "data": {
                "P0": [a.description for a in decision.P0],
                "P1": [a.description for a in decision.P1],
                "P2": [a.description for a in decision.P2],
                "P3": [a.description for a in decision.P3],
            },
        }

    def chat_with_llm(self, prompt_input, llm_client, temperature=0.7, max_tokens=1024):
        """
        完整 AI 对话链：组装 Prompt → 调用 LLM → 校验输出 → 兜底

        Args:
            prompt_input: PromptInput (含 State/Time/Decision/KG)
            llm_client: LLMClient 实例
            temperature: 生成温度
            max_tokens: 最大生成长度

        Returns:
            {
                "mode": "llm" | "emotion_triage" | "data_card",
                "content": str,            AI 回复 / 情绪响应
                "llm_usage": dict,         tokens 用量
                "footer": str,             免责注入
            }
        """
        # 1. 意图检测
        intent = self.detect_intent(prompt_input.user_query)

        # 2. 情绪分流
        if intent == "emotion":
            emotion_resp = self.format_emotion_response(prompt_input.state)
            return {
                "mode": "emotion_triage",
                "content": emotion_resp,
                "llm_usage": {},
                "footer": self.format_ai_footer(),
            }

        # 3. 组装 Prompt
        full_prompt = self.process(prompt_input)

        # 4. 调用 LLM（带两次重试）
        last_error = None
        for attempt in range(2):
            resp = llm_client.chat(
                prompt_text=full_prompt,
                temperature=temperature if attempt == 0 else 0.2,
                max_tokens=max_tokens,
            )
            if resp["success"]:
                # 5. 输出校验
                if self.validate_output(resp["content"]):
                    return {
                        "mode": "llm",
                        "content": resp["content"],
                        "llm_usage": resp.get("usage", {}),
                        "footer": self.format_ai_footer(),
                    }
                else:
                    last_error = "输出格式校验失败"
                    # 第2次失败触发兜底
                    if attempt == 0:
                        continue
            else:
                last_error = resp.get("error", "LLM调用失败")
                break

        # 6. 兜底：数据卡片模式
        return {
            "mode": "data_card",
            "content": f"⚠ {last_error}",
            "data_card": self.build_data_card(prompt_input.decision),
            "llm_usage": {},
            "footer": self.format_ai_footer(),
        }
