"""LNS 核心数据模型 — 使用 dataclass 保持轻量。"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


# ── 基础类型 ──────────────────────────────────────────────

@dataclass
class BirthPlace:
    city: str = ""
    district: str = ""
    country: str = "CN"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class UserInput:
    birth_date: str           # YYYY-MM-DD
    birth_time: str           # HH:MM
    birth_place: BirthPlace = field(default_factory=BirthPlace)
    gender: str = "male"      # male / female
    timezone: str = ""        # optional, auto-detect if empty


@dataclass
class TargetTime:
    date: str = ""            # YYYY-MM-DD, default to today
    time: str = ""            # HH:MM, default to now


# ── Calendar Engine Output (04) ────────────────────────────

@dataclass
class SolarTerm:
    name: str = ""                         # e.g. "立春"
    transition_timestamp: str = ""         # ISO 8601 UTC
    is_before_transition: bool = True


@dataclass
class CalendarOutput:
    solar_datetime: str = ""
    lunar_datetime: str = ""
    timezone: str = ""
    utc_offset: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    solar_term: SolarTerm = field(default_factory=SolarTerm)
    is_dst: bool = False
    true_solar_time: str = ""


# ── BaZi Engine Output (05) ────────────────────────────────

@dataclass
class Pillar:
    heavenly_stem: str = ""   # 天干
    earthly_branch: str = ""  # 地支
    stem_code: str = ""       # 天干代码 e.g. "jia"
    branch_code: str = ""     # 地支代码 e.g. "zi"


@dataclass
class FourPillars:
    year: Pillar = field(default_factory=Pillar)
    month: Pillar = field(default_factory=Pillar)
    day: Pillar = field(default_factory=Pillar)
    hour: Pillar = field(default_factory=Pillar)


@dataclass
class LuckCycle:
    """大运周期"""
    age_range: str = ""       # e.g. "0-10"
    pillar: str = ""          # e.g. "甲子"
    heavenly_stem: str = ""
    earthly_branch: str = ""


@dataclass
class BaZiOutput:
    four_pillars: FourPillars = field(default_factory=FourPillars)
    day_master: str = ""                  # 日主天干, e.g. "丁"
    ten_gods: dict = field(default_factory=dict)       # e.g. {"year": "正印", ...}
    five_elements: dict = field(default_factory=dict)  # e.g. {"wood": 3.0, ...}
    normalized_elements: dict = field(default_factory=dict)
    hidden_stems: dict = field(default_factory=dict)   # e.g. {"zi": ["gui"], ...}
    luck_cycles: List[LuckCycle] = field(default_factory=list)
    start_age: float = 0.0                # 起运年龄
    deities: List[str] = field(default_factory=list)   # 神煞


# ── State Engine Output (06) ────────────────────────────────

@dataclass
class StateOutput:
    current_stage: str = ""
    stage_derivation: str = "age_based"   # age_based | luck_based
    energy_level: str = "medium"          # high | medium | low
    risk_level: str = "normal"            # normal | elevated | high
    dominant_structure: str = ""
    luck_cycle_theme: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    capability_profile: List[str] = field(default_factory=list)
    behavior_patterns: List[str] = field(default_factory=list)
    environment_tendency: List[str] = field(default_factory=list)
    development_direction: dict = field(default_factory=dict)


# ── Knowledge Graph Intermediate ────────────────────────────

@dataclass
class KnowledgeGraphInput:
    """KG 的输入包含 State Engine 的上下文"""
    four_pillars: FourPillars = field(default_factory=FourPillars)
    ten_gods: dict = field(default_factory=dict)
    five_elements: dict = field(default_factory=dict)
    normalized_elements: dict = field(default_factory=dict)
    hidden_stems: dict = field(default_factory=dict)
    luck_cycles: List[LuckCycle] = field(default_factory=list)
    state_context: dict = field(default_factory=dict)  # stage, energy, risk, dominant


@dataclass
class KnowledgeGraphOutput:
    behavior_model: List[str] = field(default_factory=list)
    capability_model: List[str] = field(default_factory=list)
    career_mapping: List[str] = field(default_factory=list)
    risk_model: dict = field(default_factory=dict)
    advice_templates: List[str] = field(default_factory=list)
    ten_god_weights: dict = field(default_factory=dict)


# ── State Synthesizer Output (07A) ──────────────────────────

@dataclass
class SynthesizedOutput:
    synthesized_behavior: List[str] = field(default_factory=list)
    synthesized_career: List[str] = field(default_factory=list)
    synthesized_risk: List[str] = field(default_factory=list)
    dominant_profile: str = ""
    confidence_score: float = 0.0
    conflict_log: List[dict] = field(default_factory=list)


# ── Time Engine Output (08) ────────────────────────────────

@dataclass
class T0Layer:
    daily_state: str = ""
    energy_state: str = "medium"           # high / medium / low
    focus_area: List[str] = field(default_factory=list)
    avoid_actions: List[str] = field(default_factory=list)
    recommended_focus: List[str] = field(default_factory=list)
    risk: List[str] = field(default_factory=list)


@dataclass
class T1Layer:
    monthly_trend: str = "stable"            # up / stable / down
    opportunities: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    recommended_focus: List[str] = field(default_factory=list)


@dataclass
class T2Layer:
    yearly_direction: str = ""
    structural_shift: str = ""
    major_shift: List[str] = field(default_factory=list)
    strategic_focus: List[str] = field(default_factory=list)
    avoidance_strategy: List[str] = field(default_factory=list)
    risk_level: str = "normal"


@dataclass
class T3Layer:
    life_stage: str = ""
    long_term_direction: List[str] = field(default_factory=list)
    structural_advantage: List[str] = field(default_factory=list)
    structural_risk: List[str] = field(default_factory=list)
    strategic_path: List[str] = field(default_factory=list)


@dataclass
class TMinus1Item:
    period: str = ""
    luck_pillar: str = ""
    life_stage: str = ""
    energy_pattern: str = ""
    key_theme: str = ""
    structural_shift: bool = False


@dataclass
class TMinus1Layer:
    timeline: List[TMinus1Item] = field(default_factory=list)
    key_transitions: List[dict] = field(default_factory=list)
    repeating_patterns: List[str] = field(default_factory=list)
    path_summary: str = ""


@dataclass
class TimeOutput:
    T0: T0Layer = field(default_factory=T0Layer)
    T1: T1Layer = field(default_factory=T1Layer)
    T2: T2Layer = field(default_factory=T2Layer)
    T3: T3Layer = field(default_factory=T3Layer)
    T_minus_1: TMinus1Layer = field(default_factory=TMinus1Layer)


# ── Decision Engine Output (09) ─────────────────────────────

@dataclass
class PriorityAction:
    description: str = ""
    reason: str = ""
    risk_note: str = ""
    time_scale: str = "T0"  # T0 / T1 / T2 / T3


@dataclass
class DecisionOutput:
    P0: List[PriorityAction] = field(default_factory=list)  # 立即执行
    P1: List[PriorityAction] = field(default_factory=list)  # 重要任务
    P2: List[PriorityAction] = field(default_factory=list)  # 优化项
    P3: List[PriorityAction] = field(default_factory=list)  # 可选探索
    decision_logic: dict = field(default_factory=dict)
    priority_reasoning: List[str] = field(default_factory=list)


# ── Prompt Engine Input ─────────────────────────────────────

@dataclass
class PromptInput:
    state: StateOutput = field(default_factory=StateOutput)
    time: TimeOutput = field(default_factory=TimeOutput)
    decision: DecisionOutput = field(default_factory=DecisionOutput)
    knowledge_graph: SynthesizedOutput = field(default_factory=SynthesizedOutput)
    user_query: str = ""
