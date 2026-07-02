"""
Calendar Engine — 时间标准化底座

职责：公历↔农历转换、节气计算、时区转换、DST处理、真太阳时。
强制锁定库：Skyfield ≥1.46, lunar-python ≥2.0.5

数据流：
  UserInput → TimezoneResolver → DSTAdjuster → SolarParser → LunarConverter
  → SolarTermEngine → TrueSolarTimeAdjuster → CalendarOutput

依赖：无 LNS 内部依赖（独立底座）。
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import warnings

import pytz
from dateutil import parser as dateutil_parser
from lunar_python import Lunar, Solar

from models.core import CalendarOutput, SolarTerm, BirthPlace, UserInput, TargetTime

# 时区数据库 — 常用城市到时区映射
CITIES_TIMEZONE: Dict[str, str] = {
    # 中国主要城市
    "北京": "Asia/Shanghai", "上海": "Asia/Shanghai", "广州": "Asia/Shanghai",
    "深圳": "Asia/Shanghai", "杭州": "Asia/Shanghai", "成都": "Asia/Shanghai",
    "武汉": "Asia/Shanghai", "西安": "Asia/Shanghai", "南京": "Asia/Shanghai",
    "重庆": "Asia/Shanghai", "天津": "Asia/Shanghai", "长沙": "Asia/Shanghai",
    "苏州": "Asia/Shanghai", "郑州": "Asia/Shanghai", "东莞": "Asia/Shanghai",
    "青岛": "Asia/Shanghai", "沈阳": "Asia/Shanghai", "宁波": "Asia/Shanghai",
    "昆明": "Asia/Shanghai", "大连": "Asia/Shanghai", "厦门": "Asia/Shanghai",
    "合肥": "Asia/Shanghai", "佛山": "Asia/Shanghai", "福州": "Asia/Shanghai",
    "哈尔滨": "Asia/Shanghai", "济南": "Asia/Shanghai", "温州": "Asia/Shanghai",
    "长春": "Asia/Shanghai", "石家庄": "Asia/Shanghai", "常州": "Asia/Shanghai",
    "泉州": "Asia/Shanghai", "南宁": "Asia/Shanghai", "贵阳": "Asia/Shanghai",
    "南昌": "Asia/Shanghai", "太原": "Asia/Shanghai", "烟台": "Asia/Shanghai",
    "嘉兴": "Asia/Shanghai", "南通": "Asia/Shanghai", "金华": "Asia/Shanghai",
    "珠海": "Asia/Shanghai", "惠州": "Asia/Shanghai", "徐州": "Asia/Shanghai",
    "海口": "Asia/Shanghai", "乌鲁木齐": "Asia/Urumqi", "拉萨": "Asia/Shanghai",
    "呼和浩特": "Asia/Shanghai", "兰州": "Asia/Shanghai",
    # 港澳台
    "香港": "Asia/Hong_Kong", "澳门": "Asia/Macau", "台北": "Asia/Taipei",
    # 国际主要城市
    "Tokyo": "Asia/Tokyo", "Seoul": "Asia/Seoul",
    "Singapore": "Asia/Singapore", "Bangkok": "Asia/Bangkok",
    "London": "Europe/London", "Paris": "Europe/Paris",
    "Berlin": "Europe/Berlin", "New York": "America/New_York",
    "Los Angeles": "America/Los_Angeles", "San Francisco": "America/Los_Angeles",
    "Chicago": "America/Chicago", "Sydney": "Australia/Sydney",
    "Melbourne": "Australia/Melbourne", "Dubai": "Asia/Dubai",
}


class TimezoneResolver:
    """时区解析器：城市→时区，国家→默认时区，自动识别UTC offset"""

    @staticmethod
    def resolve(place: BirthPlace, timezone_str: str = "") -> str:
        if timezone_str:
            return timezone_str
        if place.city in CITIES_TIMEZONE:
            return CITIES_TIMEZONE[place.city]
        # 国家默认
        country_tz = {
            "CN": "Asia/Shanghai", "US": "America/New_York",
            "JP": "Asia/Tokyo", "GB": "Europe/London",
            "DE": "Europe/Berlin", "FR": "Europe/Paris",
            "AU": "Australia/Sydney", "SG": "Asia/Singapore",
            "KR": "Asia/Seoul", "TH": "Asia/Bangkok",
        }
        return country_tz.get(place.country, "UTC")


class DSTAdjuster:
    """夏令时识别与修正"""

    @staticmethod
    def is_dst(dt: datetime, tz_str: str) -> bool:
        try:
            tz = pytz.timezone(tz_str)
            localized = tz.localize(dt, is_dst=None)
            return bool(localized.dst()) and localized.dst().total_seconds() != 0
        except (pytz.exceptions.AmbiguousTimeError, pytz.NonExistentTimeError):
            return False
        except Exception:
            return False


class LunarConverter:
    """农历转换：公历↔农历"""

    @staticmethod
    def to_lunar(solar_date: str) -> str:
        """公历日期 → 农历日期字符串"""
        parts = solar_date.split("-")
        solar = Solar.fromYmd(int(parts[0]), int(parts[1]), int(parts[2]))
        lunar = solar.getLunar()
        year = lunar.getYear()
        month = lunar.getMonth()
        day = lunar.getDay()
        month_str = lunar.getMonthInChinese()
        day_str = lunar.getDayInChinese()
        return f"{year}年{month_str}月{day_str}"

    @staticmethod
    def to_lunar_tuple(year: int, month: int, day: int) -> tuple:
        """公历 → (农历年, 农历月, 农历日, 是否闰月)"""
        solar = Solar.fromYmd(year, month, day)
        lunar = solar.getLunar()
        return (lunar.getYear(), lunar.getMonth(), lunar.getDay(), False)


class SolarTermEngine:
    """节气计算 — 使用 lunar-python 获取24节气"""

    # 24节气列表（按顺序）
    SOLAR_TERMS = [
        "立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
        "立秋", "白露", "寒露", "立冬", "大雪", "小寒",
        "雨水", "春分", "谷雨", "小满", "夏至", "大暑",
        "处暑", "秋分", "霜降", "小雪", "冬至", "大寒",
    ]

    # 月令节气映射（八字月柱以节气分界）
    MONTH_BRANCH_TERMS = {
        "寅": "立春",  # 正月
        "卯": "惊蛰",  # 二月
        "辰": "清明",  # 三月
        "巳": "立夏",  # 四月
        "午": "芒种",  # 五月
        "未": "小暑",  # 六月
        "申": "立秋",  # 七月
        "酉": "白露",  # 八月
        "戌": "寒露",  # 九月
        "亥": "立冬",  # 十月
        "子": "大雪",  # 十一月
        "丑": "小寒",  # 十二月
    }

    @staticmethod
    def get_current_solar_term(dt: datetime) -> SolarTerm:
        """获取当前节气区间"""
        result = SolarTerm()
        from lunar_python import Lunar
        lunar = Lunar.fromYmd(dt.year, dt.month, dt.day)

        # Get current solar term
        jq = lunar.getJieQi()
        result.name = jq or ""

        # Try to get the transition time from JieQiTable
        try:
            jq_table = lunar.getJieQiTable()
            if jq_table and jq in jq_table:
                result.transition_timestamp = jq_table[jq].isoformat()
                result.is_before_transition = dt < jq_table[jq]
        except Exception:
            pass

        return result


class TrueSolarTimeEngine:
    """真太阳时计算（专业模式）"""

    @staticmethod
    def calculate(local_dt: datetime, longitude: float) -> datetime:
        """
        计算真太阳时。
        真太阳时 = 平太阳时 + 经度修正 + 均时差

        V1 简化实现：仅做经度修正。
        每度经度 = 4分钟时差（东经为正）。
        """
        if longitude == 0.0:
            return local_dt

        # 中国标准时间使用东八区(120°E)
        std_longitude = 120.0
        # 经度差 → 时间差（分钟）
        diff_minutes = (longitude - std_longitude) * 4

        true_solar = local_dt + timedelta(minutes=diff_minutes)
        return true_solar


class CalendarEngine:
    """
    Calendar Engine 主入口

    双模式：处理出生时间（静态）和当前时间（流日/流年）。
    """

    def __init__(self):
        self.tz_resolver = TimezoneResolver()
        self.dst_adjuster = DSTAdjuster()
        self.lunar_converter = LunarConverter()
        self.solar_term_engine = SolarTermEngine()
        self.true_solar_engine = TrueSolarTimeEngine()

    def process(self,
                birth_date: str,
                birth_time: str,
                birth_place: Optional[BirthPlace] = None,
                timezone_str: str = "",
                use_true_solar: bool = False) -> CalendarOutput:
        """
        处理用户出生时间 → CalendarOutput

        Args:
            birth_date: YYYY-MM-DD
            birth_time: HH:MM
            birth_place: 出生地（含经纬度）
            timezone_str: 时区字符串
            use_true_solar: 是否启用真太阳时（专业模式）
        """
        place = birth_place or BirthPlace()

        # 1. 解析时区
        tz_name = self.tz_resolver.resolve(place, timezone_str)
        try:
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.UTC
            tz_name = "UTC"

        # 2. 构建 datetime
        try:
            dt_str = f"{birth_date} {birth_time}"
            dt = dateutil_parser.parse(dt_str)
            dt = tz.localize(dt)
        except Exception as e:
            raise ValueError(f"无效日期时间: {birth_date} {birth_time}") from e

        # 3. DST 检测
        is_dst = self.dst_adjuster.is_dst(dt, tz_name)

        # 4. 农历转换
        lunar_str = self.lunar_converter.to_lunar(birth_date)

        # 5. 节气判断
        solar_term = self.solar_term_engine.get_current_solar_term(dt)

        # 6. 真太阳时
        true_solar_time = ""
        if use_true_solar and (place.longitude or place.latitude):
            # 先转UTC再计算
            utc_dt = dt.astimezone(pytz.UTC)
            ts_dt = self.true_solar_engine.calculate(
                utc_dt.replace(tzinfo=None),
                place.longitude or 0
            )
            true_solar_time = ts_dt.strftime("%H:%M")

        # 7. 构造输出
        utc_offset = dt.strftime("%z")
        result = CalendarOutput(
            solar_datetime=dt.isoformat(),
            lunar_datetime=lunar_str,
            timezone=tz_name,
            utc_offset=utc_offset,
            latitude=place.latitude or 0.0,
            longitude=place.longitude or 0.0,
            solar_term=solar_term,
            is_dst=is_dst,
            true_solar_time=true_solar_time,
        )
        return result

    def process_target(self,
                       target_time: Optional[TargetTime] = None,
                       birth_place: Optional[BirthPlace] = None) -> CalendarOutput:
        """
        处理当前/目标时间 → CalendarOutput
        用于流日/流年计算。
        """
        if target_time is None:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M")
        else:
            date_str = target_time.date or datetime.now().strftime("%Y-%m-%d")
            time_str = target_time.time or "12:00"

        return self.process(
            birth_date=date_str,
            birth_time=time_str,
            birth_place=birth_place,
            timezone_str="",
            use_true_solar=False,
        )
