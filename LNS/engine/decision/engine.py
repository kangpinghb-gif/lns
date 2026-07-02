"""
Decision Engine (09) — 决策引擎

职责：将「状态+时间+风险+机会」转化为 P0-P3 可执行优先级。
是整个系统的最终收敛点：分析→结构→时间→决策→行动。

核心公式：
  Decision Score = (0.3 × Opportunity) - (0.4 × Risk) + (0.1 × Match) + (0.2 × Time)

风控（Risk）权重强制最高（0.4），践行「不制造焦虑但绝对提示风险」的底层原则。

依赖：State Engine + Time Engine + Knowledge Graph。
"""


from models.core import (
    StateOutput, TimeOutput, SynthesizedOutput,
    DecisionOutput, PriorityAction,
)


class DecisionEngine:
    """
    Decision Engine — 行动优先级排序引擎。

    支持基于用户反馈的权重调整。
    当反馈评分平均值低于 3 时，自动提高 Risk 权重、降低 Opportunity 权重。
    """

    # 基础权重
    BASE_WEIGHTS = {
        "opportunity": 0.3,
        "risk": 0.4,
        "match": 0.1,
        "time": 0.2,
    }

    def __init__(self, feedback_adjust=False):
        self.feedback_adjust = feedback_adjust
        self.weights = dict(self.BASE_WEIGHTS)

    def set_weights_from_feedback(self, avg_score, total_count):
        """
        根据反馈统计调整权重。

        Args:
            avg_score: 平均评分 (1-5)
            total_count: 反馈总数
        """
        if total_count < 5:
            return  # 数据量不足，不调整

        self.weights = dict(self.BASE_WEIGHTS)

        if avg_score < 3.0:
            # 评分低 → 用户觉得建议不靠谱 → 提高风险控制权重，降低机会权重
            self.weights["risk"] = min(0.5, self.weights["risk"] + 0.1)
            self.weights["opportunity"] = max(0.2, self.weights["opportunity"] - 0.1)
        elif avg_score > 4.5:
            # 评分高 → 用户信任建议 → 略微降低风险权重，提高机会权重
            self.weights["risk"] = max(0.3, self.weights["risk"] - 0.05)
            self.weights["opportunity"] = min(0.4, self.weights["opportunity"] + 0.05)

        # 保持总和为 1.0
        total = sum(self.weights.values())
        if total != 1.0:
            self.weights["match"] = max(0.05, self.weights["match"] + (1.0 - total))

    def process(self, state: StateOutput,
                time_output: TimeOutput,
                synthesized: SynthesizedOutput) -> DecisionOutput:
        """
        生成 P0-P3 决策输出。

        Args:
            state: 当前人生状态
            time_output: 时间分析输出
            synthesized: 合成知识图谱

        Returns: DecisionOutput (P0-P3 行动+逻辑)
        """
        result = DecisionOutput()

        # 收集所有潜在行动
        all_actions = []

        # 1. 从时间引擎的 focus 中提取
        focus_scores = []

        # T0 focus
        for fa in time_output.T0.recommended_focus:
            focus_scores.append((fa, self._score_focus(fa, state, time_output, "T0")))
        for fa in time_output.T0.avoid_actions:
            score = self._score_focus(fa, state, time_output, "T0")
            focus_scores.append((fa, score))

        # T1 focus
        for fa in time_output.T1.recommended_focus:
            focus_scores.append((fa, self._score_focus(fa, state, time_output, "T1")))
        for op in time_output.T1.opportunities:
            focus_scores.append((op, self._score_focus(op, state, time_output, "T1")))

        # T2 focus
        for fa in time_output.T2.strategic_focus:
            focus_scores.append((fa, self._score_focus(fa, state, time_output, "T2")))

        # T3 strategy
        for fa in time_output.T3.strategic_path:
            focus_scores.append((fa, self._score_focus(fa, state, time_output, "T3")))

        # 风险
        for risk in time_output.T0.risk:
            focus_scores.append((f"注意：{risk}", 30 - 20))  # 高风险低分

        # 2. 排序
        focus_scores.sort(key=lambda x: x[1], reverse=True)

        # 3. 分配到 P0-P3
        p0_targets = []
        p1_targets = []
        p2_targets = []
        p3_targets = []

        for action_text, score in focus_scores:
            # 去重
            all_action_texts = [a.description for a in
                                p0_targets + p1_targets + p2_targets + p3_targets]
            if action_text in all_action_texts:
                continue

            action = PriorityAction(
                description=action_text,
                reason=self._generate_reason(action_text, state, time_output),
                risk_note=self._risk_note(action_text, state),
                time_scale=self._detect_time_scale(action_text),
            )

            if score >= 70:
                p0_targets.append(action)
            elif score >= 50:
                p1_targets.append(action)
            elif score >= 30:
                p2_targets.append(action)
            else:
                p3_targets.append(action)

            if len(p0_targets + p1_targets + p2_targets + p3_targets) >= 8:
                break

        result.P0 = p0_targets
        result.P1 = p1_targets
        result.P2 = p2_targets
        result.P3 = p3_targets

        # 决策逻辑
        result.decision_logic = {
            "risk_weight": 0.4,
            "opportunity_weight": 0.3,
            "time_weight": 0.2,
            "match_weight": 0.1,
            "risk_level": state.risk_level,
            "energy_level": state.energy_level,
        }

        # 优先级理由
        reasoning = []
        if p0_targets:
            reasoning.append(f"P0: 立即执行项共{len(p0_targets)}项，需即刻关注")
        if p1_targets:
            reasoning.append(f"P1: 重要项共{len(p1_targets)}项，影响1-3个月结构")
        if state.risk_level == "high":
            reasoning.append("当前整体风险较高，P0优先关注风险控制")
        elif state.risk_level == "elevated":
            reasoning.append("当前风险偏高，决策中以风控为优先")

        result.priority_reasoning = reasoning

        return result

    def _score_focus(self, action: str, state: StateOutput,
                     time_output: TimeOutput, time_scale: str) -> float:
        """
        行动评分。
        Decision Score = (W_Opp × Opportunity) - (W_Risk × Risk) + (W_Match × Match) + (W_Time × Time)
        权重来自 self.weights（受反馈调整）
        """
        w = self.weights
        score = 50.0  # 基础分

        # 时间维度权重
        time_weights = {"T0": 1.0, "T1": 0.7, "T2": 0.5, "T3": 0.3}
        time_w = time_weights.get(time_scale, 0.5)
        score += 20 * time_w * w["time"]

        # 机会检测
        opportunity_keywords = ["推进", "主动", "启动", "攻克", "利用", "推出"]
        has_opportunity = any(kw in action for kw in opportunity_keywords)
        if has_opportunity:
            score += 15 * w["opportunity"]

        # 风险检测
        risk_keywords = ["避免", "减少", "注意", "风险", "降低", "缓冲"]
        has_risk = any(kw in action for kw in risk_keywords)
        if has_risk:
            score -= 20 * w["risk"]

        # 能量匹配
        if state.energy_level == "high" and "高强度" in action:
            score += 10  # Match 因子
        elif state.energy_level == "low" and "减少" in action:
            score += 10

        # 风险等级调整
        if state.risk_level == "high" and has_risk:
            score += 20  # 高风险期风险建议更重要
        elif state.risk_level == "high" and has_opportunity:
            score -= 15  # 高风险期降低机会优先级

        return max(10, min(100, score))

    def _generate_reason(self, action: str, state: StateOutput,
                         time_output: TimeOutput) -> str:
        """生成行动理由"""
        if "风险" in action or "注意" in action:
            return f"当前{state.risk_level}风险状态"
        if "能量" in action or "精力" in action:
            return f"当前能量{state.energy_level}"
        if "推进" in action or "启动" in action:
            return f"当前处于{state.current_stage}，适合推进"
        return f"基于当前{state.dominant_structure}结构建议"

    def _risk_note(self, action: str, state: StateOutput) -> str:
        """风险说明"""
        if state.risk_level == "high":
            return "高风险期，执行需谨慎"
        return ""

    def _detect_time_scale(self, action: str) -> str:
        """检测行动的时间尺度"""
        if "今日" in action or "今天" in action:
            return "T0"
        if "月" in action:
            return "T1"
        if "年" in action:
            return "T2"
        if "长期" in action:
            return "T3"
        return "T0"
