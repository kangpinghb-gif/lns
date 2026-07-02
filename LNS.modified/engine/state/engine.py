"""
State Engine (06) — 人生状态建模引擎

职责：将 BaZi Engine 输出的结构化命盘数据转换为人生状态模型。
不做预测。只做结构化解释：状态、能力、风险、阶段、趋势。

依赖：BaZi Engine Output ONLY。

数据流：
  BaZiOutput → ElementBalanceAnalysis → TenGodsPatternAnalysis
  → StructuralDominanceDetection → LifeStageMapping → RiskPatternExtraction
  → CapabilityModeling → StateAssembly
"""

import math

from typing import List, Tuple
from models.core import BaZiOutput, StateOutput
from models.constants import (
    ELEMENTS, STEMS_TO_ELEMENT, STEMS_TO_YIN_YANG,
    EARTHLY_BRANCHES, BRANCHES_TO_ELEMENT,
)


# ── 人生阶段系统 ─────────────────────────────────────────

PHYSICAL_AGE_STAGES = [
    (0, 12, "基础形成期"),
    (13, 18, "性格塑造期"),
    (19, 25, "路径探索期"),
    (26, 35, "结构建立期"),
    (36, 50, "稳定发展期"),
    (50, 200, "收敛优化期"),
]

LUCK_CYCLE_STAGES = [
    "基础塑造期",
    "发展探索期",
    "结构建立期",
    "稳定发展期",
    "成熟优化期",
    "成熟优化期",
    "成熟优化期",
    "成熟优化期",
]


# ── 主导结构检测 ────────────────────────────────────────

# 十神对应的结构代码
TEN_GOD_STRUCTURE_MAP = {
    "比肩": "independent", "劫财": "competitive",
    "食神": "steady_output", "伤官": "innovative",
    "正财": "conservative", "偏财": "opportunistic",
    "正官": "rule_following", "七杀": "breakthrough",
    "正印": "learning_support", "偏印": "unique_thinking",
}

TEN_GOD_STRUCTURE_CN = {
    "independent": "自主独立型", "competitive": "竞争驱动型",
    "steady_output": "稳定输出型", "innovative": "创新突破型",
    "conservative": "稳健积累型", "opportunistic": "机会捕捉型",
    "rule_following": "规则执行型", "breakthrough": "挑战驱动型",
    "learning_support": "学习支撑型", "unique_thinking": "独立思考型",
}

# 五行主导
ELEMENT_DOMINANCE = {
    "wood": "成长导向", "fire": "表达导向",
    "earth": "稳定导向", "metal": "规则导向", "water": "流动导向",
}


class StateEngine:
    """
    State Engine — 将命盘转化为人生状态模型。
    """

    def process(self, bazi_output: BaZiOutput, age: float = 25.0) -> StateOutput:
        """
        从 BaZiOutput 生成人生状态。

        Args:
            bazi_output: BaZi Engine 输出的命盘
            age: 当前年龄

        Returns: StateOutput 人生状态模型
        """
        result = StateOutput()

        # 1. 能量模型
        result.energy_level = self._calc_energy_level(bazi_output)

        # 2. 人生阶段
        stage, derivation = self._calc_life_stage(age, bazi_output)
        result.current_stage = stage
        result.stage_derivation = derivation

        # 3. 主导结构
        result.dominant_structure = self._detect_dominant_structure(bazi_output)

        # 4. 大运主题
        result.luck_cycle_theme = self._calc_luck_cycle_theme(bazi_output)

        # 5. 能力模型
        result.capability_profile = self._calc_capability(bazi_output)

        # 6. 行为模式
        result.behavior_patterns = self._calc_behavior(bazi_output)

        # 7. 风险级别
        risk, constraints = self._calc_risk(bazi_output)
        result.risk_level = risk
        result.constraints = constraints

        # 8. 环境倾向
        result.environment_tendency = self._calc_environment(bazi_output)

        # 9. 发展方向
        result.development_direction = self._calc_direction(bazi_output)

        return result

    def _calc_energy_level(self, bazi: BaZiOutput) -> str:
        """计算能量级别。火/木旺→高，土平衡→中，金/水偏弱→内收。"""
        ne = bazi.normalized_elements
        if ne.get("fire", 0) >= 7 or ne.get("wood", 0) >= 7:
            return "high"
        if ne.get("water", 0) <= 3 and ne.get("metal", 0) <= 3 and ne.get("fire", 0) >= 5:
            return "high"
        # 土居中→中
        earth = ne.get("earth", 0)
        if 4 <= earth <= 6 or (ne.get("fire", 0) >= 4 and ne.get("earth", 0) >= 4):
            return "medium"
        # 金/水偏弱→低
        if ne.get("metal", 0) <= 3 and ne.get("water", 0) >= 6:
            return "low"
        if ne.get("water", 0) <= 2:
            return "low"
        return "medium"

    def _calc_life_stage(self, age: float, bazi: BaZiOutput) -> Tuple[str, str]:
        """计算人生阶段。优先使用大运起运年龄。"""
        # 尝试使用大运
        if bazi.luck_cycles and bazi.start_age >= 0:
            start_age = bazi.start_age
            cycle_index = max(0, math.floor((age - start_age) / 10))
            if cycle_index < len(LUCK_CYCLE_STAGES):
                stage = LUCK_CYCLE_STAGES[cycle_index]
                return stage, "luck_based"

        # 降级到物理年龄
        for start, end, stage in PHYSICAL_AGE_STAGES:
            if start <= age <= end:
                return stage, "age_based"
        return "收敛优化期", "age_based"

    def _detect_dominant_structure(self, bazi: BaZiOutput) -> str:
        """检测主导十神结构"""
        ten_gods = bazi.ten_gods

        # 统计四柱中出现的十神频率
        counts = {}
        for position, god in ten_gods.items():
            counts[god] = counts.get(god, 0) + 1

        # 结合五行补充判断
        ne = bazi.normalized_elements
        dominant_elem = max(ne, key=ne.get) if ne else "earth"
        elem_desc = ELEMENT_DOMINANCE.get(dominant_elem, "平衡型")

        if not counts:
            return f"{elem_desc}为主"

        # 找出现最多的十神
        max_count = max(counts.values())
        top_gods = [g for g, c in counts.items() if c == max_count]

        if len(top_gods) >= 2:
            names = [TEN_GOD_STRUCTURE_CN.get(TEN_GOD_STRUCTURE_MAP.get(g, ""), g) for g in top_gods]
            return f"{'与'.join(names)}"
        else:
            struct = TEN_GOD_STRUCTURE_MAP.get(top_gods[0], "")
            return TEN_GOD_STRUCTURE_CN.get(struct, top_gods[0])

    def _calc_luck_cycle_theme(self, bazi: BaZiOutput) -> List[str]:
        """从大运干支推导语义主题"""
        themes = []
        if not bazi.luck_cycles:
            return themes

        for cycle in bazi.luck_cycles[:1]:  # 只看当前大运
            stem = cycle.heavenly_stem
            branch = cycle.earthly_branch
            stem_elem = STEMS_TO_ELEMENT.get(stem, "")
            branch_elem = BRANCHES_TO_ELEMENT.get(branch, "")
            stem_yang = STEMS_TO_YIN_YANG.get(stem, "yang")

            if stem_elem == "wood" and branch_elem == "wood":
                themes.append("成长扩展期")
            elif stem_elem == "fire" and branch_elem == "fire":
                themes.append("表达展现期")
            elif stem_elem == "metal" and branch_elem == "metal":
                themes.append("规则整合期")
            elif stem_elem == "water" and branch_elem == "water":
                themes.append("流动调整期")
            elif stem_elem == "earth" and branch_elem == "earth":
                themes.append("稳定积累期")
            elif stem_elem in ("wood", "fire") and branch_elem in ("wood", "fire"):
                themes.append("积极发展期")
            elif stem_elem in ("metal", "water") and branch_elem in ("metal", "water"):
                themes.append("内收调整期")
            elif "earth" in (stem_elem, branch_elem):
                themes.append("结构巩固期")
            else:
                themes.append("综合发展期")

        return themes

    def _calc_capability(self, bazi: BaZiOutput) -> List[str]:
        """六种能力分类"""
        capabilities = []
        ne = bazi.normalized_elements
        ten_gods = bazi.ten_gods

        # 基于十神
        god_set = set(ten_gods.values())
        if "正官" in god_set or "七杀" in god_set:
            capabilities.append("执行能力")
        if "食神" in god_set or "伤官" in god_set:
            capabilities.append("创造能力")
        if "正财" in god_set or "偏财" in god_set:
            capabilities.append("资源管理")
        if "正印" in god_set or "偏印" in god_set:
            capabilities.append("思考能力")
        if "比肩" in god_set or "劫财" in god_set:
            capabilities.append("社交能力")
        if ne.get("earth", 0) >= 5 or ne.get("metal", 0) >= 5:
            capabilities.append("结构能力")
        if ne.get("water", 0) >= 5:
            capabilities.append("风险控制能力")

        if not capabilities:
            capabilities = ["基础执行能力", "学习适应能力"]

        return capabilities[:6]

    def _calc_behavior(self, bazi: BaZiOutput) -> List[str]:
        """行为模式"""
        patterns = []
        ne = bazi.normalized_elements
        ten_gods = bazi.ten_gods
        god_set = set(ten_gods.values())

        if "食神" in god_set:
            patterns.append("稳定输出型")
        if "伤官" in god_set:
            patterns.append("创新表达型")
        if "正官" in god_set and "七杀" not in god_set:
            patterns.append("规则遵从型")
        if "七杀" in god_set:
            patterns.append("挑战驱动型")
        if "正财" in god_set:
            patterns.append("长期积累型")
        if "偏财" in god_set:
            patterns.append("机会捕捉型")
        if ne.get("wood", 0) >= 6:
            patterns.append("持续成长型")
        if ne.get("water", 0) >= 6:
            patterns.append("灵活适应型")
        if ne.get("fire", 0) >= 6:
            patterns.append("外向表达型")
        if ne.get("metal", 0) >= 6:
            patterns.append("理性分析型")
        if ne.get("earth", 0) >= 6:
            patterns.append("系统执行型")

        if not patterns:
            patterns = ["均衡适应型"]

        return patterns[:4]

    def _calc_risk(self, bazi: BaZiOutput) -> Tuple[str, List[str]]:
        """风险检测"""
        constraints = []
        ne = bazi.normalized_elements

        # 五行极度失衡
        max_elem = max(ne, key=ne.get) if ne else "earth"
        min_elem = min(ne, key=ne.get) if ne else "water"
        if ne.get(max_elem, 0) >= 9 and ne.get(min_elem, 0) <= 2:
            constraints.append("五行结构极度失衡，建议关注短板发展")
            return "high", constraints

        if ne.get(max_elem, 0) >= 8 and ne.get(min_elem, 0) <= 3:
            constraints.append("五行结构偏颇，需注意平衡发展")
            return "elevated", constraints

        # 十神冲突检测
        ten_gods = bazi.ten_gods
        god_set = set(ten_gods.values())
        if "正官" in god_set and "伤官" in god_set:
            constraints.append("规则性与创新性并存，需注意协调两者的平衡")
        if "正财" in god_set and "偏财" in god_set:
            constraints.append("资源获取方式多样，需聚焦核心路径")
        if "七杀" in god_set and "正印" not in god_set:
            constraints.append("压力转化机制缺少支撑，建议建立系统化缓冲")

        if not constraints:
            return "normal", []

        if len(constraints) >= 3:
            return "elevated", constraints
        return "normal", constraints

    def _calc_environment(self, bazi: BaZiOutput) -> List[str]:
        """环境倾向"""
        tendencies = []
        ne = bazi.normalized_elements
        ten_gods = bazi.ten_gods
        god_set = set(ten_gods.values())

        if ne.get("fire", 0) >= 5:
            tendencies.append("高变化环境")
        if ne.get("earth", 0) >= 5:
            tendencies.append("稳定环境")
        if "七杀" in god_set:
            tendencies.append("竞争环境")
        if "偏财" in god_set:
            tendencies.append("资源密集环境")
        if "正官" in god_set:
            tendencies.append("规则密集环境")
        if "伤官" in god_set:
            tendencies.append("自由创造环境")

        if not tendencies:
            tendencies = ["均衡环境"]

        return tendencies[:3]

    def _calc_direction(self, bazi: BaZiOutput) -> dict:
        """发展方向"""
        ne = bazi.normalized_elements
        ten_gods = bazi.ten_gods
        god_set = set(ten_gods.values())

        recommended = []
        avoid = []
        optimal = []

        if ne.get("wood", 0) >= 5:
            recommended.append("学习成长型路径")
            optimal.append("教育培训行业")
        if ne.get("fire", 0) >= 5:
            recommended.append("表达创造型路径")
            optimal.append("内容创意行业")
        if ne.get("earth", 0) >= 5:
            recommended.append("稳健积累型路径")
            optimal.append("管理运营岗位")
        if ne.get("metal", 0) >= 5:
            recommended.append("规则分析型路径")
            optimal.append("金融法律行业")
        if ne.get("water", 0) >= 5:
            recommended.append("流动适应型路径")
            optimal.append("咨询互联网行业")
        if "伤官" in god_set:
            recommended.append("创新突破型路径")
        if "正官" in god_set:
            recommended.append("体制发展路径")
        if "偏财" in god_set:
            recommended.append("创业投资路径")

        # 避免方向
        if ne.get("water", 0) <= 2:
            avoid.append("流动性过高的环境")
        if ne.get("wood", 0) <= 2:
            avoid.append("需要持续学习输出的岗位")
        if "七杀" not in god_set and ne.get("fire", 0) <= 3:
            avoid.append("高压竞争环境")

        if not recommended:
            recommended.append("综合发展路径")

        return {
            "recommended_direction": recommended[:3],
            "avoid_direction": avoid[:2],
            "optimal_environment": optimal[:3],
        }
