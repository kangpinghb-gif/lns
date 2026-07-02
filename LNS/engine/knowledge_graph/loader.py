"""
Knowledge Graph Data Loader — 知识图谱 JSON 数据加载器。

从 knowledge/ 目录加载所有 JSON 文件到内存缓存。
支持热加载和版本追踪。

数据结构：
  knowledge/
    ten_gods/ten_gods.json       — 十神知识库
    five_elements/              — 五行知识库
    hidden_stems/               — 藏干行为映射
    shensha/                    — 神煞系统
    relations/                  — 地支关系（六合/三合/六冲/六害/三刑）
    career/                     — 职业映射
    wealth/                     — 财富模式
    relationship/               — 关系模式
    health/                     — 健康映射
    learning/                   — 学习风格
    risk/                       — 风险库
    actions/action_library.json — 行动模板库
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class KGDataLoader:
    """知识图谱数据加载器 — 从 JSON 文件加载到内存"""

    def __init__(self, knowledge_dir: Path):
        self.knowledge_dir = Path(knowledge_dir)
        self._data: Dict[str, Any] = {}
        self._file_hashes: Dict[str, str] = {}
        self._loaded_at: Optional[datetime] = None

    def load_all(self) -> Dict[str, Any]:
        """加载所有 JSON 文件到内存，验证 version/status"""
        self._data = {}
        self._file_hashes = {}
        validated_count = 0
        skipped_count = 0

        for subdir in self.knowledge_dir.iterdir():
            if not subdir.is_dir():
                continue
            for json_file in subdir.glob("*.json"):
                key = f"{subdir.name}/{json_file.stem}"
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        data = json.loads(content)
                    # V2.1: 列表数据逐项校验 version/status
                    if isinstance(data, list):
                        for item in data:
                            self._validate_node(item, json_file)
                    elif isinstance(data, dict):
                        self._validate_node(data, json_file)
                    self._data[key] = data
                    self._file_hashes[key] = hashlib.md5(content.encode()).hexdigest()
                    validated_count += 1
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[KG Loader] Failed to load {json_file}: {e}")
                    skipped_count += 1

        self._loaded_at = datetime.now()
        print(f"[KG Loader] Loaded {validated_count} files, skipped {skipped_count}")
        return self._data

    @staticmethod
    def _validate_node(item: dict, source_file: Path):
        """校验节点是否包含 version/status（V2.1 新需求）"""
        if not item.get("version"):
            item["version"] = "0.0.0"
        if not item.get("status"):
            item["status"] = "draft"

    def get(self, key: str, default=None):
        """通过键名获取数据（格式：'category/file' 如 'ten_gods/ten_gods'）"""
        return self._data.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """获取所有已加载数据"""
        return self._data

    def hot_reload(self) -> bool:
        """检测文件变化并重新加载（热更新）"""
        changed = False
        for subdir in self.knowledge_dir.iterdir():
            if not subdir.is_dir():
                continue
            for json_file in subdir.glob("*.json"):
                key = f"{subdir.name}/{json_file.stem}"
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    new_hash = hashlib.md5(content.encode()).hexdigest()
                    if self._file_hashes.get(key) != new_hash:
                        data = json.loads(content)
                        self._data[key] = data
                        self._file_hashes[key] = new_hash
                        changed = True
                        print(f"[KG Loader] Hot reloaded: {key}")
                except Exception:
                    pass
        if changed:
            self._loaded_at = datetime.now()
        return changed

    def summary(self) -> Dict:
        """数据加载摘要（V2.1 增加版本和状态统计）"""
        counts = {}
        version_set = set()
        status_count = {"draft": 0, "verified": 0, "deprecated": 0}
        for key, data in self._data.items():
            counts[key] = len(data) if isinstance(data, list) else 1
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        v = item.get("version", "?")
                        s = item.get("status", "?")
                        version_set.add(v)
                        if s in status_count:
                            status_count[s] += 1
        return {
            "loaded_at": self._loaded_at.isoformat() if self._loaded_at else None,
            "files": len(self._data),
            "categories": counts,
            "versions": sorted(version_set),
            "status_distribution": status_count,
        }


# ── 静态路由表 ────────────────────────────────────────────

# [Dominant_Structure_ID] + [Energy_Level] + [Time_Dimension_Scale] → [Action_IDs]
# 结构ID: 01(比肩)/02(劫财)/03(伤官)/04(食神)/05(正财)/06(偏财)/07(正官)/08(七杀)/09(正印)/10(偏印)
# 能量: H(高)/M(中)/L(低)
# 时间: T0(日)/T1(月)/T2(年)/T3(大运)

STRUCTURE_ID_MAP = {
    "比肩": "01", "劫财": "02", "伤官": "03", "食神": "04",
    "正财": "05", "偏财": "06", "正官": "07", "七杀": "08",
    "正印": "09", "偏印": "10",
}

ENERGY_MAP = {"high": "H", "medium": "M", "low": "L"}
TIME_MAP = {"T0": "T0", "T1": "T1", "T2": "T2", "T3": "T3"}

# MVP 前 50 条硬编码路由（25-Algorithm-Cookbook.md §2）
ROUTER_TABLE = {
    # 伤官主导
    "03_H_T0": ["action_003", "action_011"],  # 启动创新任务 + 注意言语安全
    "03_M_T0": ["action_009", "action_003"],  # 输出创作内容 + 启动创新
    "03_L_T1": ["action_007", "action_011"],  # 延迟决策 + 注意言语
    # 正财主导
    "05_H_T1": ["action_005", "action_012"],  # 审查财务 + 整合资源
    "05_L_T2": ["action_005", "action_008"],  # 审查财务 + 制定计划
    "05_M_T0": ["action_008", "action_001"],  # 制定计划 + 系统学习
    # 食神主导
    "04_H_T0": ["action_009", "action_003"],  # 输出创作 + 启动创新
    "04_M_T1": ["action_006", "action_009"],  # 规律作息 + 输出创作
    # 偏财主导
    "06_H_T0": ["action_012", "action_004"],  # 整合资源 + 建立关系
    "06_M_T1": ["action_005", "action_012"],  # 审查财务 + 整合资源
    "06_L_T2": ["action_008", "action_005"],  # 制定计划 + 审查财务
    # 七杀主导
    "08_H_T0": ["action_007", "action_003"],  # 延迟决策 + 启动创新
    "08_M_T1": ["action_010", "action_006"],  # 降低风险 + 规律作息
    # 正官主导
    "07_H_T0": ["action_008", "action_001"],  # 制定计划 + 系统学习
    "07_M_T1": ["action_002", "action_008"],  # 完善简历 + 制定计划
    # 正印主导
    "09_H_T0": ["action_001", "action_009"],  # 系统学习 + 输出创作
    "09_M_T1": ["action_001", "action_006"],  # 系统学习 + 规律作息
    "09_L_T2": ["action_006", "action_008"],  # 规律作息 + 制定计划
    # 偏印主导
    "10_H_T0": ["action_001", "action_003"],  # 系统学习 + 启动创新
    "10_M_T1": ["action_009", "action_001"],  # 输出创作 + 系统学习
    # 比肩主导
    "01_H_T0": ["action_004", "action_003"],  # 建立关系 + 启动创新
    "01_M_T1": ["action_008", "action_006"],  # 制定计划 + 规律作息
    # 劫财主导
    "02_H_T0": ["action_004", "action_012"],  # 建立关系 + 整合资源
    "02_M_T1": ["action_007", "action_005"],  # 延迟决策 + 审查财务
}

# 默认兜底路由
DEFAULT_ROUTES = {
    "T0": ["action_006", "action_008"],  # 规律作息 + 制定计划
    "T1": ["action_008", "action_001"],  # 制定计划 + 系统学习
    "T2": ["action_005", "action_008"],  # 审查财务 + 制定计划
    "T3": ["action_008", "action_010"],  # 制定计划 + 降低风险
}


def build_router_key(dominant_structure: str, energy_level: str, time_scale: str) -> str:
    """
    构建路由键：Router_Key = [Dominant_Structure_ID] + [Energy_Level] + [Time_Dimension_Scale]

    Args:
        dominant_structure: 主导结构描述（含十神名称）
        energy_level: high / medium / low
        time_scale: T0 / T1 / T2 / T3

    Returns: 路由键，如 "03_H_T0"
    """
    # 从主导结构中提取十神名称
    struct_id = "00"  # 默认
    for god_name, sid in STRUCTURE_ID_MAP.items():
        if god_name in dominant_structure:
            struct_id = sid
            break

    energy_code = ENERGY_MAP.get(energy_level, "M")
    time_code = TIME_MAP.get(time_scale, "T0")

    return f"{struct_id}_{energy_code}_{time_code}"


def resolve_routes(dominant_structure: str, energy_level: str,
                   time_scale: str) -> list:
    """
    从路由表获取该状态下的行动 ID 列表。

    Args:
        dominant_structure: 状态引擎输出的主导结构描述
        energy_level: high/medium/low
        time_scale: T0/T1/T2/T3

    Returns: Action ID 列表（如 ["action_003", "action_011"]）
    """
    key = build_router_key(dominant_structure, energy_level, time_scale)
    routes = ROUTER_TABLE.get(key)
    if routes:
        return routes

    # 降级：按时间尺度取默认
    return DEFAULT_ROUTES.get(time_scale, DEFAULT_ROUTES["T0"])
