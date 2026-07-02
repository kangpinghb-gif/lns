"""LNS 全局配置"""

from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent

# 知识图谱数据目录
KNOWLEDGE_DIR = ROOT / "knowledge"

# 缓存配置（V1 使用内存缓存，生产环境替换为 Redis）
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 性能目标
PERFORMANCE = {
    "calendar_engine_ms": 100,
    "bazi_engine_ms": 200,
    "single_analysis_ms": 3000,
    "api_response_ms": 200,
    "ai_response_ms": 5000,
}

# 锁定库版本
LOCKED_LIBS = {
    "skyfield": ">=1.46",
    "lunar-python": ">=1.4.8,<2.0",
}
