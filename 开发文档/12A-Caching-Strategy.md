# Life Navigation System — Caching Strategy

> Version: 1.0 | Status:追加冻结

## 1. Purpose
解决 10 节点超长流水线的性能瓶颈。核心策略：将计算分为静态（一次计算，缓存复用）和动态（每次请求重新计算）两层。

## 2. Data Classification

| 数据类别 | 计算频率 | 缓存策略 | 存储位置 |
|---------|---------|---------|---------|
| **静态命盘**：四柱/十神/五行/大运 | 用户一生只算一次 | 用户创建后永久缓存 | Redis（长期）+ PostgreSQL |
| **准静态年运**：T2(年)/T3(10年) | 每年重算一次 | 年首计算后缓存至年终 | Redis（TTL=365天） |
| **半动态月运**：T1(月) | 每月重算一次 | 月首计算后缓存至月末 | Redis（TTL=31天） |
| **动态日运**：T0(日) | 每次请求重算 | 不缓存 | 实时计算 |
| **AI 问答** | 每次请求 | 不缓存 | 实时计算 |

## 3. Pipeline Short-Circuit Logic

```
用户请求到达
    ↓
检查 Redis：静态命盘 cache hit？
    ├── No  → 走完整 Calendar + BaZi 计算 → 写入 Redis
    └── Yes → 跳过静态计算
    ↓
检查 Redis：T2/T3 cache hit（年/10年）？
    ├── No  → Time Engine 计算 T2/T3 → 写入 Redis（TTL=365d）
    └── Yes → 跳过
    ↓
检查 Redis：T1 cache hit（月）？
    ├── No  → Time Engine 计算 T1 → 写入 Redis（TTL=31d）
    └── Yes → 跳过
    ↓
Time Engine 实时计算 T0（日）
    ↓
Decision Engine + Prompt Engine → 输出
```

## 4. Cache Invalidation
- 用户重新校准出生时间 → 清除该用户全部缓存，重新计算
- 年运缓存过期 → 下一年的 T2/T3 增量计算，不需重新计算静态命盘
- 月运缓存过期 → 下个月的 T1 增量计算

## 5. Performance Target Compliance

| 场景 | 无缓存（ms） | 有缓存（ms） | 达标？ |
|------|------------|------------|-------|
| 首次访问 | ~1800 | ~1800 | <3s ✔ |
| 次日回访（T0 刷新） | ~1800 | **~300**（跳过静态） | <200ms ✔ |
| 同月多次回访 | ~1800 | **~150**（跳过静态+T1） | <200ms ✔ |
| AI 问答（含静态） | ~3500 | **~800**（静态缓存命中） | <3s ✔ |

## 6. Implementation Rules
- 每次请求先检查缓存再决定计算路径
- 缓存键格式：`lns:static:{user_id}`、`lns:yearly:{user_id}:{year}`、`lns:monthly:{user_id}:{year}:{month}`
- 缓存过期采用 TTL，不主动清理（Redis 内存自动回收）
---
