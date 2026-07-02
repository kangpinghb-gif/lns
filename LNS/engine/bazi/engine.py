"""
BaZi Engine (05) — 四柱八字的纯规则计算引擎。

数据流：
  CalendarOutput → YearPillar → MonthPillar(SolarTerm) → DayPillar → HourPillar
  → TenGodsEngine → FiveElementsEngine → LuckCycleEngine → BaZiOutput

计算锚点：公历 1900 年 1 月 31 日（农历正月初一）为「甲午日」。
核心原则：无AI、无推理、无解释、纯规则计算。
"""

from datetime import datetime, date, time
import math
from typing import Optional, List, Tuple

from models.core import (
    CalendarOutput, BaZiOutput, FourPillars, Pillar, LuckCycle,
)
from models.constants import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES,
    HIDDEN_STEMS_WEIGHTS, HOUR_BRANCH_MAP, NIGHT_HOUR_BRANCH,
    STEMS_TO_ELEMENT, STEMS_TO_YIN_YANG,
    BRANCHES_TO_ELEMENT, ELEMENTS, ELEMENT_CN,
    is_forward_luck,
    HOUR_BRANCH_MAP as HOUR_BRANCHES,
)


# ── 核心递推函数 ───────────────────────────────────────

# 基准锚点：1900-01-31 = 甲午日
EPOCH_DATE = date(1900, 1, 31)
# 用 lunar-python 验证的锚点日柱
# Solar(1900,1,31).getLunar().getDayInGanZhi() = 甲辰
# 甲辰在60甲子中的索引 = 24 (甲=0辰=4 -> 第24位)
EPOCH_DAY_INDEX = 24  # 甲辰


def _get_day_index(target_date: date) -> int:
    """计算目标日期距离锚点的天数，取模60返回日柱索引。"""
    delta = (target_date - EPOCH_DATE).days
    # 甲午=30，所以索引 = (30 + delta) mod 60
    idx = (EPOCH_DAY_INDEX + delta) % 60
    return idx


def _stems_branch_from_index(idx: int) -> Tuple[str, str]:
    """60甲子索引 → (天干, 地支)"""
    stem_idx = idx % 10
    branch_idx = idx % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


# ── 节气月令映射 ─────────────────────────────────────────

# 月柱地支按节气划分，立春为寅月
MONTH_BRANCH_BY_TERM = {
    "立春": "寅", "惊蛰": "卯", "清明": "辰", "立夏": "巳",
    "芒种": "午", "小暑": "未", "立秋": "申", "白露": "酉",
    "寒露": "戌", "立冬": "亥", "大雪": "子", "小寒": "丑",
}

# 月干从年干推导（五虎遁）
YEAR_TO_MONTH_STEM = {
    # 年干 → 正月(寅月)天干索引
    "甲": 2, "己": 2,  # 甲己之年丙作首 → 丙=2
    "乙": 4, "庚": 4,  # 乙庚之岁戊为头 → 戊=4
    "丙": 6, "辛": 6,  # 丙辛之年寻庚上 → 庚=6
    "丁": 8, "壬": 8,  # 丁壬壬寅顺水流 → 壬=8
    "戊": 0, "癸": 0,  # 戊癸甲寅好追求 → 甲=0
}


def _get_stem_for_month(year_stem: str, month_branch_idx: int) -> str:
    """年干 + 月支索引 → 月干"""
    base_idx = YEAR_TO_MONTH_STEM.get(year_stem, 0)
    stem_idx = (base_idx + month_branch_idx) % 10
    return HEAVENLY_STEMS[stem_idx]


# ── 时柱 ─────────────────────────────────────────────────

# 时干从日干推导（五鼠遁）
DAY_TO_HOUR_STEM = {
    "甲": 0, "己": 0,  # 甲己还加甲 → 甲=0
    "乙": 2, "庚": 2,  # 乙庚丙作初 → 丙=2
    "丙": 4, "辛": 4,  # 丙辛从戊起 → 戊=4
    "丁": 6, "壬": 6,  # 丁壬庚子居 → 庚=6
    "戊": 8, "癸": 8,  # 戊癸何方发，壬子是真途 → 壬=8
}


def _get_stem_for_hour(day_stem: str, hour_branch_idx: int) -> str:
    """日干 + 时支索引 → 时干"""
    base_idx = DAY_TO_HOUR_STEM.get(day_stem, 0)
    stem_idx = (base_idx + hour_branch_idx) % 10
    return HEAVENLY_STEMS[stem_idx]


# ── 时支判断 ────────────────────────────────────────────

def _get_hour_branch(hour: int) -> str:
    """小时数 → 时支代码"""
    if hour == 23 or hour == 0:
        return "子"
    for start_h, end_h, branch in HOUR_BRANCHES:
        if start_h <= hour <= end_h:
            return branch
    return "子"


def _is_night_hour(hour: int) -> bool:
    """是否为夜子时（23:00-24:00）"""
    return hour == 23


# ── 五行计算 ─────────────────────────────────────────────

def _calculate_five_elements(four_pillars: FourPillars) -> dict:
    """计算天干五行得分（不含藏干）"""
    scores = {e: 0.0 for e in ELEMENTS}
    for pillar in [four_pillars.year, four_pillars.month, four_pillars.day, four_pillars.hour]:
        stem_elem = STEMS_TO_ELEMENT.get(pillar.heavenly_stem, "")
        if stem_elem:
            scores[stem_elem] += 1.0
        branch_elem = BRANCHES_TO_ELEMENT.get(pillar.earthly_branch, "")
        if branch_elem:
            scores[branch_elem] += 1.0
    return scores


def _calculate_hidden_stems_score(four_pillars: FourPillars) -> dict:
    """计算包含藏干权重的五行得分"""
    scores = {e: 0.0 for e in ELEMENTS}

    # 天干每出现一次计 1.0
    for pillar in [four_pillars.year, four_pillars.month, four_pillars.day, four_pillars.hour]:
        stem_elem = STEMS_TO_ELEMENT.get(pillar.heavenly_stem, "")
        if stem_elem:
            scores[stem_elem] += 1.0

    # 地支藏干按权重表计算
    for pillar in [four_pillars.year, four_pillars.month, four_pillars.day, four_pillars.hour]:
        branch = pillar.earthly_branch
        hidden = HIDDEN_STEMS_WEIGHTS.get(branch, [])
        for stem, weight in hidden:
            elem = STEMS_TO_ELEMENT.get(stem, "")
            if elem:
                scores[elem] += weight * 1.0

    return scores


def _normalize_elements(raw_scores: dict) -> dict:
    """五行得分归一化：0-10之间的相对得分"""
    max_score = max(raw_scores.values()) if raw_scores else 1
    if max_score == 0:
        return {k: 0.0 for k in raw_scores}
    return {k: round((v / max_score) * 10, 1) for k, v in raw_scores.items()}


# ── 日主十神映射 ─────────────────────────────────────────

# (日主元素, 天干元素, 日主阴阳, 天干阴阳) → 十神代码
TEN_GOD_MATRIX = {
    ("wood", "wood", "yang", "yang"): "比肩",
    ("wood", "wood", "yang", "yin"): "劫财",
    ("wood", "wood", "yin", "yin"): "比肩",
    ("wood", "wood", "yin", "yang"): "劫财",
    ("wood", "fire", "yang", "yang"): "食神",
    ("wood", "fire", "yang", "yin"): "伤官",
    ("wood", "fire", "yin", "yin"): "食神",
    ("wood", "fire", "yin", "yang"): "伤官",
    ("wood", "earth", "yang", "yang"): "偏财",
    ("wood", "earth", "yang", "yin"): "正财",
    ("wood", "earth", "yin", "yin"): "偏财",
    ("wood", "earth", "yin", "yang"): "正财",
    ("wood", "metal", "yang", "yang"): "七杀",
    ("wood", "metal", "yang", "yin"): "正官",
    ("wood", "metal", "yin", "yin"): "七杀",
    ("wood", "metal", "yin", "yang"): "正官",
    ("wood", "water", "yang", "yang"): "偏印",
    ("wood", "water", "yang", "yin"): "正印",
    ("wood", "water", "yin", "yin"): "偏印",
    ("wood", "water", "yin", "yang"): "正印",
    # fire 日主
    ("fire", "fire", "yang", "yang"): "比肩",
    ("fire", "fire", "yang", "yin"): "劫财",
    ("fire", "fire", "yin", "yin"): "比肩",
    ("fire", "fire", "yin", "yang"): "劫财",
    ("fire", "earth", "yang", "yang"): "食神",
    ("fire", "earth", "yang", "yin"): "伤官",
    ("fire", "earth", "yin", "yin"): "食神",
    ("fire", "earth", "yin", "yang"): "伤官",
    ("fire", "metal", "yang", "yang"): "偏财",
    ("fire", "metal", "yang", "yin"): "正财",
    ("fire", "metal", "yin", "yin"): "偏财",
    ("fire", "metal", "yin", "yang"): "正财",
    ("fire", "water", "yang", "yang"): "七杀",
    ("fire", "water", "yang", "yin"): "正官",
    ("fire", "water", "yin", "yin"): "七杀",
    ("fire", "water", "yin", "yang"): "正官",
    ("fire", "wood", "yang", "yang"): "偏印",
    ("fire", "wood", "yang", "yin"): "正印",
    ("fire", "wood", "yin", "yin"): "偏印",
    ("fire", "wood", "yin", "yang"): "正印",
    # earth 日主
    ("earth", "earth", "yang", "yang"): "比肩",
    ("earth", "earth", "yang", "yin"): "劫财",
    ("earth", "earth", "yin", "yin"): "比肩",
    ("earth", "earth", "yin", "yang"): "劫财",
    ("earth", "metal", "yang", "yang"): "食神",
    ("earth", "metal", "yang", "yin"): "伤官",
    ("earth", "metal", "yin", "yin"): "食神",
    ("earth", "metal", "yin", "yang"): "伤官",
    ("earth", "water", "yang", "yang"): "偏财",
    ("earth", "water", "yang", "yin"): "正财",
    ("earth", "water", "yin", "yin"): "偏财",
    ("earth", "water", "yin", "yang"): "正财",
    ("earth", "wood", "yang", "yang"): "七杀",
    ("earth", "wood", "yang", "yin"): "正官",
    ("earth", "wood", "yin", "yin"): "七杀",
    ("earth", "wood", "yin", "yang"): "正官",
    ("earth", "fire", "yang", "yang"): "偏印",
    ("earth", "fire", "yang", "yin"): "正印",
    ("earth", "fire", "yin", "yin"): "偏印",
    ("earth", "fire", "yin", "yang"): "正印",
    # metal 日主
    ("metal", "metal", "yang", "yang"): "比肩",
    ("metal", "metal", "yang", "yin"): "劫财",
    ("metal", "metal", "yin", "yin"): "比肩",
    ("metal", "metal", "yin", "yang"): "劫财",
    ("metal", "water", "yang", "yang"): "食神",
    ("metal", "water", "yang", "yin"): "伤官",
    ("metal", "water", "yin", "yin"): "食神",
    ("metal", "water", "yin", "yang"): "伤官",
    ("metal", "wood", "yang", "yang"): "偏财",
    ("metal", "wood", "yang", "yin"): "正财",
    ("metal", "wood", "yin", "yin"): "偏财",
    ("metal", "wood", "yin", "yang"): "正财",
    ("metal", "fire", "yang", "yang"): "七杀",
    ("metal", "fire", "yang", "yin"): "正官",
    ("metal", "fire", "yin", "yin"): "七杀",
    ("metal", "fire", "yin", "yang"): "正官",
    ("metal", "earth", "yang", "yang"): "偏印",
    ("metal", "earth", "yang", "yin"): "正印",
    ("metal", "earth", "yin", "yin"): "偏印",
    ("metal", "earth", "yin", "yang"): "正印",
    # water 日主
    ("water", "water", "yang", "yang"): "比肩",
    ("water", "water", "yang", "yin"): "劫财",
    ("water", "water", "yin", "yin"): "比肩",
    ("water", "water", "yin", "yang"): "劫财",
    ("water", "wood", "yang", "yang"): "食神",
    ("water", "wood", "yang", "yin"): "伤官",
    ("water", "wood", "yin", "yin"): "食神",
    ("water", "wood", "yin", "yang"): "伤官",
    ("water", "fire", "yang", "yang"): "偏财",
    ("water", "fire", "yang", "yin"): "正财",
    ("water", "fire", "yin", "yin"): "偏财",
    ("water", "fire", "yin", "yang"): "正财",
    ("water", "earth", "yang", "yang"): "七杀",
    ("water", "earth", "yang", "yin"): "正官",
    ("water", "earth", "yin", "yin"): "七杀",
    ("water", "earth", "yin", "yang"): "正官",
    ("water", "metal", "yang", "yang"): "偏印",
    ("water", "metal", "yang", "yin"): "正印",
    ("water", "metal", "yin", "yin"): "偏印",
    ("water", "metal", "yin", "yang"): "正印",
}


def _get_ten_god(day_master: str, target_stem: str) -> str:
    """获取日主与其他天干的十神关系"""
    dm_elem = STEMS_TO_ELEMENT.get(day_master, "")
    dm_yin_yang = STEMS_TO_YIN_YANG.get(day_master, "yang")
    tg_elem = STEMS_TO_ELEMENT.get(target_stem, "")
    tg_yin_yang = STEMS_TO_YIN_YANG.get(target_stem, "yang")

    key = (dm_elem, tg_elem, dm_yin_yang, tg_yin_yang)
    return TEN_GOD_MATRIX.get(key, "比肩")


# ── 大运计算 ─────────────────────────────────────────────

def _calculate_start_age(year_stem: str, gender: str,
                         birth_date: date,
                         term_transition: Optional[str]) -> float:
    """
    计算起运年龄。
    顺排：从生日到下一个节气天数 ÷ 3
    逆排：从生日到上一个节气天数 ÷ 3
    """
    forward = is_forward_luck(year_stem, gender)

    # 简化实现：V1 按 3天=1岁 规则估算
    # 需要精确节气时间才能精确计算
    # 返回近似值 0-10
    return 0.0  # TODO: 精确起运年龄计算需要节气精确时间


def _calculate_luck_cycles(year_stem: str, gender: str, start_age: float) -> List[LuckCycle]:
    """计算大运周期列表"""
    forward = is_forward_luck(year_stem, gender)

    # 年干索引
    stem_idx = HEAVENLY_STEMS.index(year_stem) if year_stem in HEAVENLY_STEMS else 0

    cycles = []
    current_age = start_age
    for i in range(8):  # 最多8个大运（80年）
        # 大运天干 = 年干顺/逆偏移
        if forward:
            luck_stem_idx = (stem_idx + i + 1) % 10
            luck_branch_idx = 2 + i  # 从寅月开始
        else:
            luck_stem_idx = (stem_idx - i - 1) % 10
            luck_branch_idx = (2 - i) % 12

        luck_stem = HEAVENLY_STEMS[luck_stem_idx]
        luck_branch = EARTHLY_BRANCHES[luck_branch_idx]

        end_age = current_age + 10
        cycle = LuckCycle(
            age_range=f"{int(current_age)}-{int(end_age)}",
            pillar=f"{luck_stem}{luck_branch}",
            heavenly_stem=luck_stem,
            earthly_branch=luck_branch,
        )
        cycles.append(cycle)
        current_age = end_age

    return cycles


# ── 神煞系统（V1 基础版） ────────────────────────────────

def _calculate_deities(four_pillars: FourPillars) -> List[str]:
    """计算基础神煞（V1 简化版）"""
    deities = []
    year_branch = four_pillars.year.earthly_branch
    day_stem = four_pillars.day.heavenly_stem

    # 天乙贵人
    TIAN_YI_MAP = {
        "甲": ("丑", "未"), "戊": ("丑", "未"), "庚": ("丑", "未"),
        "乙": ("子", "申"), "己": ("子", "申"),
        "丙": ("亥", "酉"), "丁": ("亥", "酉"),
        "壬": ("卯", "巳"), "癸": ("卯", "巳"),
        "辛": ("午", "寅"),
    }
    tian_yi = TIAN_YI_MAP.get(day_stem, ())
    for branch in [p.earthly_branch for p in [four_pillars.year, four_pillars.month, four_pillars.day, four_pillars.hour]]:
        if branch in tian_yi:
            deities.append("天乙贵人")
            break

    # 文昌贵人
    WEN_CHANG_MAP = {
        "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
        "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
        "壬": "寅", "癸": "卯",
    }
    wen_chang = WEN_CHANG_MAP.get(day_stem, "")
    if wen_chang and any(p.earthly_branch == wen_chang for p in [four_pillars.year, four_pillars.month, four_pillars.day, four_pillars.hour]):
        deities.append("文昌")

    # 桃花（子午卯酉）
    TAO_HUA_YEAR_MAP = {
        "寅": "卯", "午": "卯", "戌": "卯",
        "巳": "午", "酉": "午", "丑": "午",
        "申": "酉", "子": "酉", "辰": "酉",
        "亥": "子", "卯": "子", "未": "子",
    }
    tao_hua = TAO_HUA_YEAR_MAP.get(year_branch, "")
    for pillar in [four_pillars.year, four_pillars.month, four_pillars.day, four_pillars.hour]:
        if pillar.earthly_branch == tao_hua:
            deities.append("桃花")
            break

    # 驿马（寅申巳亥）
    YI_MA_YEAR_MAP = {
        "寅": "申", "午": "申", "戌": "申",
        "巳": "亥", "酉": "亥", "丑": "亥",
        "申": "寅", "子": "寅", "辰": "寅",
        "亥": "巳", "卯": "巳", "未": "巳",
    }
    yi_ma = YI_MA_YEAR_MAP.get(year_branch, "")
    for pillar in [four_pillars.year, four_pillars.month, four_pillars.day, four_pillars.hour]:
        if pillar.earthly_branch == yi_ma:
            deities.append("驿马")
            break

    # 羊刃（阳干帝旺）
    YANG_REN_MAP = {
        "甲": "卯", "丙": "午", "戊": "午",
        "庚": "酉", "壬": "子",
    }
    yang_ren = YANG_REN_MAP.get(day_stem, "")
    if yang_ren and any(p.earthly_branch == yang_ren for p in [four_pillars.year, four_pillars.month, four_pillars.day, four_pillars.hour]):
        deities.append("羊刃")

    return deities


# ── 藏干系统 ─────────────────────────────────────────────

def _get_hidden_stems(four_pillars: FourPillars) -> dict:
    """获取四柱的地支藏干"""
    result = {}
    for name, pillar in [("year", four_pillars.year), ("month", four_pillars.month),
                          ("day", four_pillars.day), ("hour", four_pillars.hour)]:
        branch = pillar.earthly_branch
        hidden = HIDDEN_STEMS_WEIGHTS.get(branch, [])
        result[name] = [(stem, weight) for stem, weight in hidden]
    return result


# ══════════════════════════════════════════════════════════
# BaZiEngine 主类
# ══════════════════════════════════════════════════════════

class BaZiEngine:
    """
    BaZi Engine — 纯规则命理计算引擎。

    输入：CalendarOutput（生日或目标时间）
    输出：BaZiOutput（结构化命盘数据）
    """

    def process(self, calendar_output: CalendarOutput,
                gender: str = "male") -> BaZiOutput:
        """
        从 CalendarOutput 计算完整命盘。

        Args:
            calendar_output: Calendar Engine 输出的标准化时间
            gender: male / female

        Returns: BaZiOutput 结构化命盘
        """
        # 解析时间
        from dateutil.parser import parse as dt_parse
        dt = dt_parse(calendar_output.solar_datetime)
        birth_date = dt.date()
        hour = dt.hour

        # 1. 年柱（以立春为界）
        year_pillar = self._calc_year_pillar(birth_date)

        # 2. 月柱（以节气为界）
        month_pillar = self._calc_month_pillar(birth_date, year_pillar.heavenly_stem,
                                                calendar_output)

        # 3. 日柱
        day_pillar = self._calc_day_pillar(birth_date)

        # 4. 时柱（含夜子时特殊处理）
        hour_pillar = self._calc_hour_pillar(hour, day_pillar.heavenly_stem, birth_date)

        four_pillars = FourPillars(
            year=year_pillar,
            month=month_pillar,
            day=day_pillar,
            hour=hour_pillar,
        )

        # 5. 日主
        day_master = day_pillar.heavenly_stem

        # 6. 十神
        ten_gods = self._calc_ten_gods(day_master, four_pillars)

        # 7. 五行
        raw_scores = _calculate_hidden_stems_score(four_pillars)
        normalized = _normalize_elements(raw_scores)

        # 8. 藏干
        hidden_stems = _get_hidden_stems(four_pillars)

        # 9. 大运
        start_age = _calculate_start_age(
            year_pillar.heavenly_stem, gender, birth_date,
            calendar_output.solar_term.transition_timestamp if calendar_output.solar_term else None
        )
        luck_cycles = _calculate_luck_cycles(year_pillar.heavenly_stem, gender, start_age)

        # 10. 神煞
        deities = _calculate_deities(four_pillars)

        result = BaZiOutput(
            four_pillars=four_pillars,
            day_master=day_master,
            ten_gods=ten_gods,
            five_elements=raw_scores,
            normalized_elements=normalized,
            hidden_stems=hidden_stems,
            luck_cycles=luck_cycles,
            start_age=start_age,
            deities=deities,
        )
        return result

    def _calc_year_pillar(self, birth_date: date) -> Pillar:
        """年柱计算（使用 lunar-python）"""
        from lunar_python import Solar, Lunar
        try:
            solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
            lunar = solar.getLunar()
            year_gz = lunar.getYearInGanZhi()  # 已按立春判断
            stem = year_gz[0]
            branch = year_gz[1]
            return Pillar(
                heavenly_stem=stem,
                earthly_branch=branch,
                stem_code=stem,
                branch_code=branch,
            )
        except Exception:
            pass

        # 降级
        year = birth_date.year
        li_chun = date(year, 2, 4)
        if birth_date < li_chun:
            year -= 1
        stem_idx = (year - 4) % 10
        branch_idx = (year - 4) % 12
        return Pillar(
            heavenly_stem=HEAVENLY_STEMS[stem_idx],
            earthly_branch=EARTHLY_BRANCHES[branch_idx],
            stem_code=HEAVENLY_STEMS[stem_idx],
            branch_code=EARTHLY_BRANCHES[branch_idx],
        )

    def _calc_month_pillar(self, birth_date: date,
                           year_stem: str,
                           calendar_output: CalendarOutput) -> Pillar:
        """月柱计算（使用 lunar-python 直接获取）"""
        from lunar_python import Solar, Lunar
        try:
            solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
            lunar = solar.getLunar()
            month_gz = lunar.getMonthInGanZhi()  # e.g. "壬午"
            stem = month_gz[0]
            branch = month_gz[1]
            return Pillar(
                heavenly_stem=stem,
                earthly_branch=branch,
                stem_code=stem,
                branch_code=branch,
            )
        except Exception:
            pass

        # 降级：基于年干推算月干（五虎遁）
        month = birth_date.month
        day = birth_date.day

        # 通过 lunar-python 获取月令
        from lunar_python import Lunar, Solar
        solar = Solar.fromYmd(birth_date.year, month, day)
        lunar = solar.getLunar()
        jq = lunar.getJieQi()  # 当前节气

        # 月令地支映射表
        month_branch_map = {
            1: "丑", 2: "寅", 3: "卯", 4: "辰",
            5: "巳", 6: "午", 7: "未", 8: "申",
            9: "酉", 10: "戌", 11: "亥", 12: "子",
        }

        # 节气对应的月支
        jq_branch_map = {
            "小寒": "丑", "大寒": "丑",
            "立春": "寅", "雨水": "寅",
            "惊蛰": "卯", "春分": "卯",
            "清明": "辰", "谷雨": "辰",
            "立夏": "巳", "小满": "巳",
            "芒种": "午", "夏至": "午",
            "小暑": "未", "大暑": "未",
            "立秋": "申", "处暑": "申",
            "白露": "酉", "秋分": "酉",
            "寒露": "戌", "霜降": "戌",
            "立冬": "亥", "小雪": "亥",
            "大雪": "子", "冬至": "子",
        }

        # 先根据节气判断月支
        if jq and jq in jq_branch_map:
            branch = jq_branch_map[jq]
        else:
            branch = month_branch_map.get(month, "子")

        # 月干索引
        branch_idx = EARTHLY_BRANCHES.index(branch) if branch in EARTHLY_BRANCHES else 0
        stem = _get_stem_for_month(year_stem, branch_idx)

        return Pillar(
            heavenly_stem=stem,
            earthly_branch=branch,
            stem_code=stem,
            branch_code=branch,
        )

    def _calc_day_pillar(self, birth_date: date) -> Pillar:
        """日柱计算（使用 lunar-python 直接获取）"""
        from lunar_python import Solar, Lunar
        try:
            solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
            lunar = solar.getLunar()
            day_gz = lunar.getDayInGanZhi()  # e.g. "辛亥"
            stem = day_gz[0]
            branch = day_gz[1]
        except Exception:
            # 降级：60日循环递推
            idx = _get_day_index(birth_date)
            stem, branch = _stems_branch_from_index(idx)
        return Pillar(
            heavenly_stem=stem,
            earthly_branch=branch,
            stem_code=stem,
            branch_code=branch,
        )

    def _calc_hour_pillar(self, hour: int, day_stem: str,
                          birth_date=None) -> Pillar:
        """
        时柱计算。

        ADR-009 夜子时分界法：
        - 早子时(00:00-01:00)：当日日干
        - 夜子时(23:00-24:00)：日柱不进位，时柱干支必须进位（用次日日干）
        """
        night_hour = _is_night_hour(hour)
        branch = _get_hour_branch(hour)

        if night_hour:
            day_stem_idx = HEAVENLY_STEMS.index(day_stem) if day_stem in HEAVENLY_STEMS else 0
            next_day_stem_idx = (day_stem_idx + 1) % 10
            next_day_stem = HEAVENLY_STEMS[next_day_stem_idx]
            branch_idx = EARTHLY_BRANCHES.index(branch) if branch in EARTHLY_BRANCHES else 0
            stem = _get_stem_for_hour(next_day_stem, branch_idx)
        else:
            branch_idx = EARTHLY_BRANCHES.index(branch) if branch in EARTHLY_BRANCHES else 0
            stem = _get_stem_for_hour(day_stem, branch_idx)

        return Pillar(
            heavenly_stem=stem,
            earthly_branch=branch,
            stem_code=stem,
            branch_code=branch,
        )

    def _calc_ten_gods(self, day_master: str, four_pillars: FourPillars) -> dict:
        """计算四柱十神"""
        result = {}
        for name, pillar in [("年柱", four_pillars.year), ("月柱", four_pillars.month),
                              ("日柱", four_pillars.day), ("时柱", four_pillars.hour)]:
            result[name] = _get_ten_god(day_master, pillar.heavenly_stem)
        return result
