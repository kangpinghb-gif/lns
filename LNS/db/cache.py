"""
LNS 缓存层 — 5 层数据分类 + Pipeline Short-Circuit。

参考 12A-Caching-Strategy.md。

数据分类：
| 类别 | 计算频率 | 缓存策略 | TTL |
|------|---------|---------|-----|
| 静态命盘 | 一次 | 首次计算后永久 | 永久 |
| 准静态年运 | 每年 | 年首计算 | 365d |
| 半动态月运 | 每月 | 月首计算 | 31d |
| 动态日运 | 每次 | 不缓存 | — |
| AI 问答 | 每次 | 不缓存 | — |

V1 使用内存字典模拟 Redis，V2 替换为 Redis。
"""

import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class MemoryCache:
    """内存缓存（V1 模拟 Redis，V2 替换为真正的 Redis）"""

    def __init__(self):
        self._store: Dict[str, dict] = {}

    def get(self, key: str):
        """获取缓存，自动检查 TTL"""
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry['ttl'] is not None and time.time() > entry['expires_at']:
            del self._store[key]
            return None
        return entry['value']

    def set(self, key: str, value: Any, ttl_seconds=None):
        """设置缓存"""
        entry = {
            'value': value,
            'ttl': ttl_seconds,
            'expires_at': (time.time() + ttl_seconds) if ttl_seconds else None,
            'created_at': time.time(),
        }
        self._store[key] = entry

    def delete(self, key):
        """删除缓存"""
        self._store.pop(key, None)

    def delete_pattern(self, pattern):
        """按前缀模式删除缓存"""
        keys_to_delete = [k for k in self._store if k.startswith(pattern)]
        for k in keys_to_delete:
            del self._store[k]

    def clear(self):
        """清空所有缓存"""
        self._store.clear()

    def stats(self) -> Dict:
        """缓存统计"""
        now = time.time()
        valid = sum(1 for v in self._store.values()
                    if v['ttl'] is None or now <= v['expires_at'])
        expired = sum(1 for v in self._store.values()
                      if v['ttl'] is not None and now > v['expires_at'])
        return {
            "total": len(self._store),
            "valid": valid,
            "expired": expired,
        }


class LNSCache:
    """
    LNS 缓存系统 — 5层数据分类 + Short-Circuit 逻辑。

    缓存键格式：
      lns:static:{user_id}          — 静态命盘，永久
      lns:yearly:{user_id}:{year}   — 年运，365d
      lns:monthly:{user_id}:{year}:{month} — 月运，31d
    """

    # TTL 常量（秒）
    TTL_STATIC = None          # 永久
    TTL_YEARLY = 365 * 86400    # 365天
    TTL_MONTHLY = 31 * 86400    # 31天

    def __init__(self):
        self.cache = MemoryCache()

    def get_static(self, user_id: str):
        """获取静态命盘缓存"""
        return self.cache.get(f"lns:static:{user_id}")

    def set_static(self, user_id: str, data: dict):
        """缓存静态命盘"""
        self.cache.set(f"lns:static:{user_id}", data, self.TTL_STATIC)

    def get_yearly(self, user_id: str, year: int):
        """获取年运缓存"""
        return self.cache.get(f"lns:yearly:{user_id}:{year}")

    def set_yearly(self, user_id: str, year: int, data: dict):
        """缓存年运"""
        self.cache.set(f"lns:yearly:{user_id}:{year}", data, self.TTL_YEARLY)

    def get_monthly(self, user_id: str, year: int, month: int):
        """获取月运缓存"""
        return self.cache.get(f"lns:monthly:{user_id}:{year}:{month}")

    def set_monthly(self, user_id: str, year: int, month: int, data: dict):
        """缓存月运"""
        self.cache.set(f"lns:monthly:{user_id}:{year}:{month}", data, self.TTL_MONTHLY)

    def invalidate_user(self, user_id: str):
        """用户重新校准出生时间→清除该用户全部缓存"""
        self.cache.delete_pattern(f"lns:static:{user_id}")
        self.cache.delete_pattern(f"lns:yearly:{user_id}")
        self.cache.delete_pattern(f"lns:monthly:{user_id}")

    def short_circuit_summary(self, user_id: str, year: int, month: int) -> Dict:
        """
        Pipeline Short-Circuit 检测。
        返回各层缓存命中状态。
        """
        result = {
            "user_id": user_id,
            "static_hit": self.get_static(user_id) is not None,
            "yearly_hit": self.get_yearly(user_id, year) is not None,
            "monthly_hit": self.get_monthly(user_id, year, month) is not None,
        }
        result["all_hit"] = result["static_hit"] and result["yearly_hit"] and result["monthly_hit"]
        return result

    def stats(self) -> Dict:
        return self.cache.stats()
