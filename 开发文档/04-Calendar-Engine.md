# Life Navigation System — Calendar Engine

> Version: 1.0 | Status: Core Infrastructure (Frozen)

## 1. Purpose
Calendar Engine 是 LNS 时间标准化核心层。唯一职责：将用户出生时间转化为可用于命理计算的标准时间结构。

## 2. Core Principle
Calendar Engine 不做任何命理判断。只做时间标准化（Time Normalization）。所有命理计算必须基于该标准时间。

## 3. Responsibilities
- 公历↔农历转换
- 节气计算（Critical：八字月柱以节气为准，立春=新一年开始）
- 时区标准化
- 夏令时（DST）识别与修正
- 真太阳时（可选专业模式）
- 出生地解析：输入{city, country} → 输出{latitude, longitude, timezone, dst_supported}

## 4. Input Specification
```json
{
  "birth_date": "YYYY-MM-DD",
  "birth_time": "HH:MM",
  "birth_place": {
    "city": "",
    "district": "",
    "country": "",
    "latitude": null,
    "longitude": null
  },
  "timezone": "optional",
  "target_time": {
    "date": "",
    "time": ""
  }
}
```
> **Note**: `latitude`/`longitude` 可选。若不传，系统从 `cities.json` 静态表中读取城市算中心经纬度。直辖市/跨经度城市（如重庆、伊犁）建议传入精确区县或经纬度，否则真太阳时误差可达 10 分钟。`target_time` 为当前查询时间，用于流日/流年计算。|

## 5. Output Specification (Core)
```json
{
  "solar_datetime": "",
  "lunar_datetime": "",
  "timezone": "",
  "utc_offset": "",
  "latitude": "",
  "longitude": "",
  "solar_term": {
    "name": "立春",
    "transition_timestamp": "2026-02-04T04:28:00Z",
    "is_before_transition": true
  },
  "is_dst": false,
  "true_solar_time": ""
}
```
> **Note**: `solar_term.transition_timestamp` 是节气交节的精确时刻（ISO 8601 UTC）。BaZi Engine 通过比对该时间戳与出生时间的先后顺序判断月柱归属。`is_before_transition` 为 true 表示出生时刻在交节之前。|

## 6. System Workflow
User Input → Timezone Resolver → DST Adjuster → Solar Calendar Parser → Lunar Calendar Converter → Solar Term Engine → True Solar Time Adjuster → Output Normalized Time Object

## 7. Sub-Modules
- Timezone Resolver: 城市→时区，国家→默认时区，自动识别UTC offset
- DST Adjuster: 判断夏令时，自动修正时间
- Lunar Converter: 公历↔农历转换，处理闰月
- Solar Term Engine: 计算24节气，判断当前节气区间，提供节气标签
- True Solar Time Engine: 经纬度修正时间，用于专业八字计算

## 8. Business Rules
1. Calendar Engine 不允许计算命理
2. 不输出命运信息
3. 所有输出必须是时间数据结构
4. 节气优先级高于农历
5. 所有后续引擎必须依赖 Calendar Engine

## 9. Error Handling
{error: INVALID_INPUT, message: ""}，必须处理：无效日期、无效时间、未知城市、时区缺失、DST无法判断。

## 10. Performance Requirements
时间解析 <100ms，时区匹配 <50ms，节气计算 <100ms。

## 11. Dependencies
Calendar Engine 独立，不依赖 BaZi Engine / State Engine / AI。是最底层基础设施。

## 12. Output Contract (Strict)
任何调用 Calendar Engine 的模块必须：不修改输出结构、不做二次推导、不插入命理解释。

## 13. Design Philosophy
Calendar Engine 的本质：将混乱时间变成可计算时间。

## 14. Extension (V2)
历史时间回溯、历法差异支持（儒略历）、全球天文历系统。
