"""
State Synthesizer (07A) — 冲突消解与权重归一化

职责：对 KG 输出的多重符号映射进行冲突消解与权重归一化。
纯代码逻辑，不调用 LLM。

V2.1 改进：
- 移除硬编码 TEN_GOD_DATA，改用 KG Loader 从 JSON 读取
- 冲突消解逻辑保留，数据来源改为动态加载
- 输出携带证据链和推理步骤
"""

from typing import List, Dict, Optional
from pathlib import Path

from models.core import KnowledgeGraphOutput, SynthesizedOutput
from engine.knowledge_graph.loader import KGDataLoader


# ── 冲突对定义（V2.1 保留，数据来源改为 KG Loader）────────

CONFLICT_PAIRS = [
    ("正官", "伤官", "rule_vs_break"),
    ("正印", "偏印", "tradition_vs_innovation"),
    ("正财", "偏财", "conservative_vs_opportunistic"),
    ("比肩", "劫财", "independent_vs_competitive"),
]

PROFILE_MAP = {
    "独立决策": "自主决策型", "稳定输出": "稳定输出型",
    "挑战规则": "创新突破型", "快速行动": "行动驱动型",
    "稳定积累": "稳健积累型", "机会捕捉": "机会驱动型",
    "遵守规则": "规则执行型", "高压力决策": "挑战驱动型",
    "深度研究": "学习研究型", "独立研究": "独立思考型",
}


class StateSynthesizer:
    """
    State Synthesizer — 冲突消解与权重归一化。
    V2.1 数据来源改为 KG Loader（不再硬编码）。
    """

    def __init__(self, knowledge_dir=None):
        if knowledge_dir is None:
            knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
        self.loader = KGDataLoader(knowledge_dir)
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            self.loader.load_all()
            self._loaded = True

    def _get_ten_god_data(self) -> dict:
        """从 KG Loader 获取十神数据"""
        self._ensure_loaded()
        data_list = self.loader.get("ten_gods/ten_gods", [])
        result = {}
        for item in data_list:
            name = item.get("name_cn", "")
            if name:
                result[name] = item
        return result

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
        reasoning_steps = []
        evidence_chain = []

        # 从 KG Loader 读取十神数据（替代硬编码 TEN_GOD_DATA）
        ten_god_data = self._get_ten_god_data()

        # 提取十神权重
        weights = kg_output.ten_god_weights
        active_gods = list(weights.keys())

        reasoning_steps.append(f"[冲突消解] 输入十神: {active_gods}")

        resolved_behaviors: List[str] = []
        resolved_careers: List[str] = []
        resolved_risks = set()

        # 1. 冲突对检测
        for god_a, god_b, conflict_type in CONFLICT_PAIRS:
            if god_a in active_gods and god_b in active_gods:
                strategy = self._resolve_pair(
                    god_a, god_b, conflict_type, weights, five_elements, energy_level
                )
                conflict_log.append(strategy)
                reasoning_steps.append(
                    f"[冲突] {god_a}+{god_b} → {strategy['strategy']} → 主导: {strategy['dominant']}"
                )

                dominant = strategy["dominant"]
                subordinate = strategy["subordinate"]

                gd = ten_god_data.get(dominant, {})
                resolved_behaviors.extend(gd.get("behavior", [])[:2])
                resolved_careers.extend(gd.get("career", [])[:2])
                resolved_risks.update(gd.get("risk", []))

                if subordinate in ten_god_data and strategy.get("ratio") == "70/30":
                    sd = ten_god_data.get(subordinate, {})
                    resolved_behaviors.extend(sd.get("behavior", [])[:1])
                    resolved_careers.extend(sd.get("career", [])[:1])

                if god_a in active_gods:
                    active_gods.remove(god_a)
                if god_b in active_gods:
                    active_gods.remove(god_b)

        # 2. 未冲突的十神
        for god in active_gods:
            gd = ten_god_data.get(god, {})
            resolved_behaviors.extend(gd.get("behavior", [])[:2])
            resolved_careers.extend(gd.get("career", [])[:1])
            resolved_risks.update(gd.get("risk", []))
            reasoning_steps.append(f"[直接映射] {god}: {gd.get('behavior', [])[:2]}")

        # 3. 去重 + 截断
        result.synthesized_behavior = list(set(resolved_behaviors))[:5]
        result.synthesized_career = list(set(resolved_careers))[:5]
        result.synthesized_risk = list(resolved_risks)[:5]

        # 4. 主导画像
        result.dominant_profile = self._derive_profile(result.synthesized_behavior)

        # 5. 置信度
        total_gods = len(kg_output.ten_god_weights)
        conflict_ratio = len(conflict_log) / max(total_gods, 1)
        result.confidence_score = round(1.0 - conflict_ratio * 0.3, 2)

        # 6. 冲突日志
        result.conflict_log = conflict_log

        # V2.1: 证据链
        evidence_chain.append({
            "step": 1, "type": "knowledge", "source_layer": 3,
            "content": f"输入十神: {list(kg_output.ten_god_weights.keys())}",
            "weight": 0.3,
        })
        if conflict_log:
            for cl in conflict_log:
                evidence_chain.append({
                    "step": len(evidence_chain) + 1,
                    "type": "rule",
                    "source_layer": 2,
                    "content": f"冲突消解: {cl['pair']} → {cl['strategy']} → {cl['dominant']}",
                    "weight": 0.5,
                })
        evidence_chain.append({
            "step": len(evidence_chain) + 1,
            "type": "conclusion",
            "source_layer": 14,
            "content": f"合成画像: {result.dominant_profile}, 置信度: {result.confidence_score}",
            "weight": 0.2,
        })
        result.evidence_chain = evidence_chain
        result.reasoning_steps = reasoning_steps

        return result

    def _resolve_pair(self, god_a: str, god_b: str,
                       conflict_type: str,
                       weights: Dict,
                       five_elements: Dict,
                       energy: str) -> Dict:
        """
        消解策略（标椎规则，保留 V1 逻辑）。
        """
        w_a = weights.get(god_a, 0.5)
        w_b = weights.get(god_b, 0.5)

        if conflict_type == "rule_vs_break":
            if w_a >= w_b:
                return {"pair": f"{god_a}+{god_b}", "strategy": "权重分配",
                        "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}
            return {"pair": f"{god_a}+{god_b}", "strategy": "权重分配",
                    "dominant": god_b, "subordinate": god_a, "ratio": "70/30"}

        elif conflict_type == "tradition_vs_innovation":
            f = five_elements
            wood_fire = (f.get("wood", 0) + f.get("fire", 0)) >= (f.get("metal", 0) + f.get("earth", 0))
            if wood_fire:
                return {"pair": f"{god_a}+{god_b}", "strategy": "五行环境选择",
                        "dominant": god_b, "subordinate": god_a, "ratio": "70/30"}
            return {"pair": f"{god_a}+{god_b}", "strategy": "五行环境选择",
                    "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}

        elif conflict_type == "conservative_vs_opportunistic":
            f = five_elements
            if f.get("earth", 0) + f.get("metal", 0) >= f.get("wood", 0) + f.get("fire", 0):
                return {"pair": f"{god_a}+{god_b}", "strategy": "五行环境选择",
                        "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}
            return {"pair": f"{god_a}+{god_b}", "strategy": "五行环境选择",
                    "dominant": god_b, "subordinate": god_a, "ratio": "70/30"}

        elif conflict_type == "independent_vs_competitive":
            if energy == "high":
                return {"pair": f"{god_a}+{god_b}", "strategy": "能量等级判断",
                        "dominant": god_b, "subordinate": god_a, "ratio": "70/30"}
            return {"pair": f"{god_a}+{god_b}", "strategy": "能量等级判断",
                    "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}

        return {"pair": f"{god_a}+{god_b}", "strategy": "默认权重分配",
                "dominant": god_a, "subordinate": god_b, "ratio": "70/30"}

    def _derive_profile(self, behaviors: List[str]) -> str:
        """从行为标签推导主导画像"""
        if not behaviors:
            return "均衡发展型"

        for b in behaviors:
            if b in PROFILE_MAP:
                return PROFILE_MAP[b]
        return f"{behaviors[0]}导向型"
