"""
Knowledge Graph (07) — 语义转换中枢

职责：命理符号→行为→能力→职业→风险→建议。
从 JSON 文件加载知识数据到内存。

依赖：State Engine Output 为输入。

V2 改进：
- 数据从 knowledge/*.json 文件加载（非硬编码）
- 集成静态路由表（Router_Key → Action ID）
"""
from pathlib import Path
from typing import Optional, List, Dict

from models.core import (
    BaZiOutput, StateOutput, KnowledgeGraphInput, KnowledgeGraphOutput,
)
from models.constants import STEMS_TO_ELEMENT, BRANCHES_TO_ELEMENT
from engine.knowledge_graph.loader import KGDataLoader, build_router_key, ROUTER_TABLE, DEFAULT_ROUTES


class KnowledgeGraph:
    """
    Knowledge Graph — 命理符号系统到人类可理解的映射。

    V2 从 knowledge/*.json 加载数据，支持热更新。
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
        完整知识图谱映射。
        """
        self._ensure_loaded()
        output = KnowledgeGraphOutput()

        ten_gods_data = self._load_indexed("ten_gods/ten_gods", "name_cn")
        element_data = self._load_indexed("five_elements/five_elements", "element")
        career_data = self._load_indexed("career/career", "category")

        ten_gods = kg_input.ten_gods
        active_gods = set(ten_gods.values()) if ten_gods else set()

        # 1. 十神映射 → 行为
        behaviors = []
        for god in active_gods:
            if god in ten_gods_data:
                behaviors.extend(ten_gods_data[god].get("behavior", []))
        output.behavior_model = list(set(behaviors))[:5]

        # 2. 十神映射 → 能力
        capabilities = []
        for god in active_gods:
            if god in ten_gods_data:
                capabilities.extend(ten_gods_data[god].get("capability", []))
        ne = kg_input.normalized_elements
        dominant_elem = max(ne, key=ne.get) if ne else "earth"
        if dominant_elem in element_data:
            capabilities.extend(element_data[dominant_elem].get("capability", []))
        output.capability_model = list(set(capabilities))[:5]

        # 3. 职业映射
        careers = []
        for god in active_gods:
            if god in ten_gods_data:
                careers.extend(ten_gods_data[god].get("career", []))
        if dominant_elem in element_data:
            careers.extend(element_data[dominant_elem].get("career", []))
        output.career_mapping = list(set(careers))[:5]

        # 4. 风险模型
        risks = {"financial_risk": [], "career_risk": [], "emotional_risk": [], "relationship_risk": []}
        for god in active_gods:
            if god in ten_gods_data:
                for r in ten_gods_data[god].get("risk", []):
                    if god in ("正财", "偏财"):
                        risks["financial_risk"].append(r)
                    elif god in ("七杀", "劫财"):
                        risks["career_risk"].append(r)
                    elif god in ("伤官",):
                        risks["relationship_risk"].append(r)
                    else:
                        risks["emotional_risk"].append(r)
        if dominant_elem in element_data:
            for r in element_data[dominant_elem].get("risk", []):
                risks["emotional_risk"].append(r)
        output.risk_model = {k: v[:3] for k, v in risks.items()}

        # 5. 建议模板（含路由表）
        advices = []
        for god in active_gods:
            if god in ten_gods_data:
                advices.append(ten_gods_data[god].get("action", ""))

        state_ctx = kg_input.state_context
        if state_ctx.get("risk_level") == "high":
            advices.append("当前风险较高，建议优先做风险控制")
        if state_ctx.get("energy_level") == "low":
            advices.append("当前能量偏低，建议聚焦核心任务")

        # 路由表
        struct_desc = state_ctx.get("dominant_structure", "")
        energy = state_ctx.get("energy_level", "medium")
        action_ids = self._route_actions(struct_desc, energy, "T0")
        action_lib = self.loader.get("actions/action_library", [])
        action_map = {a.get("id", ""): a for a in action_lib}
        for aid in action_ids:
            if aid in action_map:
                advices.append(action_map[aid].get("description", ""))

        output.advice_templates = list(set([a for a in advices if a]))[:5]

        # 6. 十神权重
        output.ten_god_weights = {g: 1.0 / len(active_gods) for g in active_gods} if active_gods else {}

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
