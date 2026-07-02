"""
State Synthesizer (07A) — 冲突消解与权重归一化

职责：对 KG 输出的多重符号映射进行冲突消解与权重归一化。
纯代码逻辑，不调用 LLM。

位置：Knowledge Graph → State Synthesizer → Time Engine / Decision Engine

核心算法：
1. 检测已知十神冲突对
2. 按消解策略选择主导结构（70%主导 + 30%补充）
3. 风险标签取并集（宁多勿漏）
4. 每个维度最多保留5个标签
"""

from typing import List, Dict

from models.core import KnowledgeGraphOutput, SynthesizedOutput


# ── 冲突对定义 ─────────────────────────────────────────

CONFLICT_PAIRS = [
    ("正官", "伤官", "rule_vs_break"),      # 规则型 vs 突破型
    ("正印", "偏印", "tradition_vs_innovation"),  # 传统型 vs 独创型
    ("正财", "偏财", "conservative_vs_opportunistic"),  # 保守型 vs 机会型
    ("比肩", "劫财", "independent_vs_competitive"),    # 独立型 vs 竞争型
]

# 十神→行为/能力/职业/风险（来源：knowledge/ten_gods.json）
TEN_GOD_DATA = {
    "比肩": {"behavior": ["独立决策", "抗拒控制", "自主执行"], "career": ["创业", "自由职业", "项目负责人"], "risk": ["孤立决策", "人际冲突"]},
    "劫财": {"behavior": ["快速行动", "资源竞争", "高风险决策"], "career": ["销售", "投资", "创业合伙"], "risk": ["冲动决策", "财务波动"]},
    "食神": {"behavior": ["稳定输出", "创造表达", "内容生产"], "career": ["内容创作", "教育", "产品设计"], "risk": ["过度舒适区"]},
    "伤官": {"behavior": ["挑战规则", "创新表达", "强主观性"], "career": ["创业", "创意行业", "科技创新"], "risk": ["冲突管理弱"]},
    "正财": {"behavior": ["稳定积累", "长期规划"], "career": ["金融", "运营", "管理"], "risk": ["增长缓慢"]},
    "偏财": {"behavior": ["机会捕捉", "灵活决策"], "career": ["投资", "贸易", "副业"], "risk": ["波动性高"]},
    "正官": {"behavior": ["遵守规则", "计划执行", "稳健决策"], "career": ["公务员", "管理", "法务"], "risk": ["灵活性不足"]},
    "七杀": {"behavior": ["高压力决策", "竞争导向", "不畏惧冲突"], "career": ["创业", "项目管理", "危机处理"], "risk": ["冲动", "压力过载"]},
    "正印": {"behavior": ["深度研究", "知识积累", "系统化思考"], "career": ["教育", "研究", "顾问"], "risk": ["行动迟缓"]},
    "偏印": {"behavior": ["独立研究", "跨界思考", "非主流路径"], "career": ["科研", "技术开发", "创新行业"], "risk": ["与社会脱节"]},
}


class StateSynthesizer:
    """
    State Synthesizer — 冲突消解与权重归一化。
    """

    def process(self, kg_output: KnowledgeGraphOutput,
                five_elements: Dict,
                energy_level: str = "medium") -> SynthesizedOutput:
        """
        处理 KG 输出，消解冲突。

        Args:
            kg_output: Knowledge Graph 原始输出
            five_elements: 五行分布数据
            energy_level: 能量级别 high / medium / low

        Returns: 消解后的合成状态
        """
        result = SynthesizedOutput()
        conflict_log = []

        # 提取十神权重
        weights = kg_output.ten_god_weights
        active_gods = list(weights.keys())

        # 1. 冲突检测与消解
        resolved_behaviors: List[str] = []
        resolved_careers: List[str] = []
        resolved_risks = set()

        # 检测冲突对
        for god_a, god_b, conflict_type in CONFLICT_PAIRS:
            if god_a in active_gods and god_b in active_gods:
                strategy = self._resolve_pair(
                    god_a, god_b, conflict_type, weights, five_elements, energy_level
                )
                conflict_log.append(strategy)

                dominant = strategy["dominant"]
                subordinate = strategy["subordinate"]

                kg = TEN_GOD_DATA
                if dominant in kg:
                    resolved_behaviors.extend(kg[dominant]["behavior"][:2])
                    resolved_careers.extend(kg[dominant]["career"][:2])
                    resolved_risks.update(kg[dominant].get("risk", []))
                if subordinate in kg and strategy.get("ratio") == "70/30":
                    resolved_behaviors.extend(kg[subordinate]["behavior"][:1])
                    resolved_careers.extend(kg[subordinate]["career"][:1])

                # 标记已处理
                if god_a in active_gods:
                    active_gods.remove(god_a)
                if god_b in active_gods:
                    active_gods.remove(god_b)

        # 2. 未冲突的十神正常添加
        for god in active_gods:
            kg = TEN_GOD_DATA
            if god in kg:
                resolved_behaviors.extend(kg[god]["behavior"][:2])
                resolved_careers.extend(kg[god]["career"][:1])
                resolved_risks.update(kg[god].get("risk", []))

        # 3. 去重 + 截断
        result.synthesized_behavior = list(set(resolved_behaviors))[:5]
        result.synthesized_career = list(set(resolved_careers))[:5]
        result.synthesized_risk = list(resolved_risks)[:5]

        # 4. 主导画像
        result.dominant_profile = self._derive_profile(result.synthesized_behavior)

        # 5. 置信度
        total_gods = len(weights)
        conflict_ratio = len(conflict_log) / max(total_gods, 1)
        result.confidence_score = round(1.0 - conflict_ratio * 0.3, 2)

        # 6. 冲突日志
        result.conflict_log = conflict_log

        return result

    def _resolve_pair(self, god_a: str, god_b: str,
                       conflict_type: str,
                       weights: Dict,
                       five_elements: Dict,
                       energy: str) -> Dict:
        """
        消解策略。

        规则：
        - 正官+伤官：按权重分配
        - 正印+偏印：木火偏印优先，土金正印优先
        - 正财+偏财：土金正财优先，木火偏财优先
        - 比肩+劫财：high→劫财，low→比肩
        """
        w_a = weights.get(god_a, 0.5)
        w_b = weights.get(god_b, 0.5)

        if conflict_type == "rule_vs_break":
            if w_a >= w_b:
                return {"pair": f"{god_a}+{god_b}", "strategy": "权重分配", "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}
            return {"pair": f"{god_a}+{god_b}", "strategy": "权重分配", "dominant": god_b, "subordinate": god_a, "ratio": "70/30"}

        elif conflict_type == "tradition_vs_innovation":
            f = five_elements
            wood_fire = (f.get("wood", 0) + f.get("fire", 0)) >= (f.get("metal", 0) + f.get("earth", 0))
            if wood_fire:
                return {"pair": f"{god_a}+{god_b}", "strategy": "五行环境选择", "dominant": god_b, "subordinate": god_a, "ratio": "70/30"}
            return {"pair": f"{god_a}+{god_b}", "strategy": "五行环境选择", "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}

        elif conflict_type == "conservative_vs_opportunistic":
            f = five_elements
            if f.get("earth", 0) + f.get("metal", 0) >= f.get("wood", 0) + f.get("fire", 0):
                return {"pair": f"{god_a}+{god_b}", "strategy": "五行环境选择", "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}
            return {"pair": f"{god_a}+{god_b}", "strategy": "五行环境选择", "dominant": god_b, "subordinate": god_a, "ratio": "70/30"}

        elif conflict_type == "independent_vs_competitive":
            if energy == "high":
                return {"pair": f"{god_a}+{god_b}", "strategy": "能量等级判断", "dominant": god_b, "subordinate": god_a, "ratio": "70/30"}
            return {"pair": f"{god_a}+{god_b}", "strategy": "能量等级判断", "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}

        return {"pair": f"{god_a}+{god_b}", "strategy": "默认权重分配", "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}

    def _derive_profile(self, behaviors: List[str]) -> str:
        """从行为标签推导主导画像"""
        if not behaviors:
            return "均衡发展型"

        profile_map = {
            "独立决策": "自主决策型", "稳定输出": "稳定输出型",
            "挑战规则": "创新突破型", "快速行动": "行动驱动型",
            "稳定积累": "稳健积累型", "机会捕捉": "机会驱动型",
            "遵守规则": "规则执行型", "高压力决策": "挑战驱动型",
            "深度研究": "学习研究型", "独立研究": "独立思考型",
        }

        for b in behaviors:
            if b in profile_map:
                return profile_map[b]
        return f"{behaviors[0]}导向型"
