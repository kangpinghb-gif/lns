"""
Knowledge Graph (07) — 语义转换中枢

职责：命理符号→行为→能力→职业→风险→建议。
从 JSON 文件加载知识数据到内存。所有映射可追溯。

V2.1 改进：
- 硬编码 risk 分类改为数据驱动（从 ten_gods.json 读取）
- 新增 Evidence Chain 输出（Knowledge → Rule → Calculation → Conclusion → Confidence）
- 新增 Reasoning Steps 日志
- 输出携带 version / confidence

依赖：State Engine Output 为输入。
"""
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from models.core import (
    BaZiOutput, StateOutput, KnowledgeGraphInput, KnowledgeGraphOutput,
)
from models.constants import STEMS_TO_ELEMENT, BRANCHES_TO_ELEMENT
from engine.knowledge_graph.loader import KGDataLoader, build_router_key, ROUTER_TABLE, DEFAULT_ROUTES


class KnowledgeGraph:
    """
    Knowledge Graph — 命理符号系统到人类可理解的映射。
    V2.1 增加证据链和推理步骤。
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

    def process(self, kg_input):
        """
        完整知识图谱映射。输出携带证据链。
        """
        self._ensure_loaded()
        output = KnowledgeGraphOutput()
        evidence_chain = []
        reasoning_steps = []

        ten_gods_data = self._load_indexed("ten_gods/ten_gods", "name_cn")
        element_data = self._load_indexed("five_elements/five_elements", "element")
        career_data = self._load_indexed("career/career", "category")

        ten_gods = kg_input.ten_gods
        active_gods = set(ten_gods.values()) if ten_gods else set()

        # ── 1. 十神映射 → 行为 ──────────────────────────
        behaviors = []
        for god in active_gods:
            if god in ten_gods_data:
                god_data = ten_gods_data[god]
                god_behaviors = god_data.get("behavior", [])
                behaviors.extend(god_behaviors)
                reasoning_steps.append(f"[十神→行为] {god} → {god_behaviors}")
                evidence_chain.append({
                    "step": len(evidence_chain) + 1,
                    "type": "knowledge",
                    "source_layer": 3,
                    "source_id": god_data.get("id", god),
                    "source_name": god,
                    "content": f"{god} → 行为: {god_behaviors}",
                    "weight": 1.0 / len(active_gods) if active_gods else 0,
                })
        output.behavior_model = list(set(behaviors))[:5]

        # ── 2. 十神映射 → 能力 ──────────────────────────
        capabilities = []
        for god in active_gods:
            if god in ten_gods_data:
                caps = ten_gods_data[god].get("capability", [])
                capabilities.extend(caps)
        ne = kg_input.normalized_elements
        dominant_elem = max(ne, key=ne.get) if ne else "earth"
        if dominant_elem in element_data:
            elem_caps = element_data[dominant_elem].get("capability", [])
            capabilities.extend(elem_caps)
            reasoning_steps.append(f"[五行→能力] 主导五行 {dominant_elem} → {elem_caps}")
        output.capability_model = list(set(capabilities))[:5]

        # ── 3. 职业映射 ──────────────────────────────────
        careers = []
        career_evidence = ""
        for god in active_gods:
            if god in ten_gods_data:
                careers.extend(ten_gods_data[god].get("career", []))
        if dominant_elem in element_data:
            careers.extend(element_data[dominant_elem].get("career", []))
        output.career_mapping = list(set(careers))[:5]
        if output.career_mapping:
            career_evidence = f"匹配职业: {', '.join(output.career_mapping[:3])}"
            evidence_chain.append({
                "step": len(evidence_chain) + 1,
                "type": "calculation",
                "source_layer": 7,
                "source_id": "career",
                "content": career_evidence,
                "weight": 0.7,
            })

        # ── 4. 风险模型（数据驱动，不再硬编码分类） ──────
        risks = {"financial_risk": [], "career_risk": [],
                 "emotional_risk": [], "relationship_risk": []}
        for god in active_gods:
            if god in ten_gods_data:
                god_data = ten_gods_data[god]
                god_risks = god_data.get("risk", [])
                # 从数据字段 risk_category 读取风险分类，兼容旧字段通过 god 名称推断
                god_risk_type = god_data.get("risk_category", "")
                if god_risk_type:
                    cat = god_risk_type
                elif god in ("正财", "偏财"):
                    cat = "financial_risk"
                elif god in ("七杀", "劫财"):
                    cat = "career_risk"
                elif god in ("伤官",):
                    cat = "relationship_risk"
                else:
                    cat = "emotional_risk"
                if cat in risks:
                    risks[cat].extend(god_risks)
                    reasoning_steps.append(f"[风险] {god} → {cat}: {god_risks}")
        if dominant_elem in element_data:
            for r in element_data[dominant_elem].get("risk", []):
                risks["emotional_risk"].append(r)
        output.risk_model = {k: v[:3] for k, v in risks.items()}

        # ── 5. 建议模板（含路由表） ──────────────────────
        advices = []
        for god in active_gods:
            if god in ten_gods_data:
                advices.append(ten_gods_data[god].get("action", ""))

        state_ctx = kg_input.state_context
        if state_ctx.get("risk_level") == "high":
            advices.append("当前风险较高，建议优先做风险控制")
        if state_ctx.get("energy_level") == "low":
            advices.append("当前能量偏低，建议聚焦核心任务")

        struct_desc = state_ctx.get("dominant_structure", "")
        energy = state_ctx.get("energy_level", "medium")
        action_ids = self._route_actions(struct_desc, energy, "T0")
        action_lib = self.loader.get("actions/action_library", [])
        action_map = {a.get("id", ""): a for a in action_lib}
        for aid in action_ids:
            if aid in action_map:
                advices.append(action_map[aid].get("description", ""))

        output.advice_templates = list(set([a for a in advices if a]))[:5]

        # ── 6. 十神权重 ──────────────────────────────────
        output.ten_god_weights = {g: 1.0 / len(active_gods) for g in active_gods} if active_gods else {}

        # ── 7. Evidence Chain 最终结论 ──────────────────
        risk_level = state_ctx.get("risk_level", "normal")
        energy_level = state_ctx.get("energy_level", "medium")
        conclusion_text = f"当前能量{energy_level}，风险{risk_level}，建议{'积极行动' if energy_level != 'low' else '保守行事'}"
        evidence_chain.append({
            "step": len(evidence_chain) + 1,
            "type": "conclusion",
            "source_layer": 14,
            "source_id": "evidence",
            "content": conclusion_text,
            "weight": 1.0,
        })

        # 可信度计算：知识来源权重 × 完整度
        confidence_scores = [e.get("weight", 0.5) for e in evidence_chain if e.get("weight")]
        output.output_confidence = round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0.5

        evidence_chain.append({
            "step": len(evidence_chain) + 1,
            "type": "confidence",
            "source_layer": 14,
            "source_id": "confidence",
            "content": f"整体可信度 {output.output_confidence}",
            "score": output.output_confidence,
        })

        output.evidence_chain = evidence_chain
        output.reasoning_steps = reasoning_steps
        output.output_version = "2.1.0"

        return output

    def _load_indexed(self, key, index_field):
        """加载 JSON 列表并按字段创建索引字典"""
        data_list = self.loader.get(key, [])
        result = {}
        for item in data_list:
            idx = item.get(index_field, "")
            if idx:
                result[idx] = item
        return result

    def _route_actions(self, dominant_structure, energy_level, time_scale="T0"):
        """通过静态路由表获取行动 ID"""
        router_key = build_router_key(dominant_structure, energy_level, time_scale)
        routes = ROUTER_TABLE.get(router_key)
        if routes:
            return routes
        return DEFAULT_ROUTES.get(time_scale, DEFAULT_ROUTES["T0"])

    def load_json(self, knowledge_dir):
        """手动指定加载目录"""
        self.loader = KGDataLoader(knowledge_dir)
        self.loader.load_all()
        self._loaded = True
