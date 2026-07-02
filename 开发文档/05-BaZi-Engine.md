# Life Navigation System — BaZi Engine

> Version: 1.0 | Status: Core Calculation Layer (Frozen)

## 1. Purpose
将 Calendar Engine 输出的标准时间，转换为四柱命盘结构。不做解释、不做分析、不做建议。只做计算。

### 1.1 历法基准锚点
系统时间转换与干支递推统一以公历 1900 年 1 月 31 日（农历正月初一）为「甲午日」作为底层数学递推的绝对基准。开发团队校验算法库时必须与此锚点对齐。

## 2. Core Principle
BaZi Engine = Deterministic Calculation Layer。无AI、无推理、无解释、纯规则计算。

## 3. Input Contract
从 Calendar Engine 接收 {solar_datetime, lunar_datetime, timezone, solar_term, latitude, longitude}

## 4. Output Contract (Core)
{four_pillars: {year, month, day, hour}, ten_gods: {}, five_elements: {}, hidden_stems: {}, luck_cycles: {ten_year[], yearly[]}, deities: []}

## 5. System Workflow
Calendar Engine Output → Year Pillar Calculator → Month Pillar Calculator (Solar Term Based) → Day Pillar Calculator → Hour Pillar Calculator → Ten Gods Engine → Five Elements Engine → Luck Cycle Engine → Output Structuring

## 6. Core Calculation Rules

### 6.1 年柱（Year Pillar）
以立春为分界点，非农历新年。立春前=上一年干支，立春后=新一年干支。

### 6.2 月柱（Month Pillar）
以节气划分月令：寅月=立春~惊蛰，卯月=惊蛰~清明，辰月=清明~立夏...

### 6.3 日柱（Day Pillar）
以基准日干支推算，使用60日循环。

### 6.4 时柱（Hour Pillar）
子时23:00-00:59，丑时01:00-02:59...

#### 6.4.1 夜子时分界规则
LNS 统一采用「早夜子时分界法」：
- 早子时（00:00–01:00）：属于当日，干支使用当日日干
- 夜子时（23:00–24:00）：属于当日，日柱干支不进位（仍算当天），但时柱干支必须进位（使用次日的时干支来推算时柱）

This rule is codified as ADR-009 in 00A-ADR.md.

#### 6.4.2 夜子时边界溢出防护

系统递推基准锚点为公历 1900 年 1 月 31 日（甲午日）。当日历输入落在基准锚点前后 24 小时内或系统支持日期范围的边界时，执行以下防护逻辑：

1. **下界防护**：若输入的出生日期为 1900 年 1 月 30 日（基准锚点前 1 天），且时段为夜子时（23:00-24:00），算法必须支持**逆向推算**，从锚点向前递减日期差而非向后。时柱进位所需的「次日日干」必须通过从锚点推算出 1900 年 1 月 31 日的干支再逆向推导 1 天获得。

2. **上界防护**：若输入的出生日期为系统支持的最大日期（如 2100-12-31）且时段为夜子时，时柱进位所需的「次日日干」须通过模 60 循环向前投影，不能因日期越界抛出异常。

3. **测试要求**：Golden Dataset 第二层必须包含至少 4 个边界夜子时用例：锚点前 1 天夜子时、锚点当天早子时、最大日期夜子时、最大日期早子时。

## 7. Ten Gods Engine（十神系统）
十神来源于日主（Day Master）与其他天干的关系。基于五行生克：生我=印，我生=食伤，克我=官杀，我克=财，同我=比劫。

## 8. Five Elements Engine（五行系统）

### 8.1 藏干权重常数表（本气/中气/余气）

| 地支 | 本气（权重0.7） | 中气（权重0.2） | 余气（权重0.1） |
|------|----------------|----------------|----------------|
| 子 | 癸(水) | — | — |
| 丑 | 己(土) | 癸(水) | 辛(金) |
| 寅 | 甲(木) | 丙(火) | 戊(土) |
| 卯 | 乙(木) | — | — |
| 辰 | 戊(土) | 乙(木) | 癸(水) |
| 巳 | 丙(火) | 戊(土) | 庚(金) |
| 午 | 丁(火) | 己(土) | — |
| 未 | 己(土) | 丁(火) | 乙(木) |
| 申 | 庚(金) | 壬(水) | 戊(土) |
| 酉 | 辛(金) | — | — |
| 戌 | 戊(土) | 辛(金) | 丁(火) |
| 亥 | 壬(水) | 甲(木) | — |

### 8.2 五行得分归一化公式

```python
def normalize_five_elements(raw_scores):
    """
    raw_scores: {wood: float, fire: float, earth: float, metal: float, water: float}
    天干每出现一次计 1.0
    地支藏干按权重表计算：本气 * 0.7 + 中气 * 0.2 + 余气 * 0.1
    归一化：score_i = (raw_i / max(raw)) * 10，保留一位小数
    输出：0-10 之间的相对得分
    """
    max_score = max(raw_scores.values())
    if max_score == 0:
        return {k: 0.0 for k in raw_scores}
    normalized = {k: round((v / max_score) * 10, 1) for k, v in raw_scores.items()}
    return normalized
```

### 8.3 Golden Dataset 对齐
五行得分必须与 Golden Dataset 中标注的 expected.five_elements 100% 匹配。任何流派差异（如藏干权重比例不同）在 V1 中以本表为准，不允许自定义。

## 9. Hidden Stems Engine（藏干系统）
{earthly_branches: {zi: [gui], chou: [ji, gui, xin]...}}

|## 10. Luck Cycle Engine（大运/流年）
|阴阳+性别+出生节气方向决定顺排/逆排。输出{ten_year_cycles:[{age_range, pillar}]}
|
|注：`theme`（主题）为语义层概念，已移交 `06-State-Engine.md` 基于大运干支与状态模型生成，BaZi Engine 仅输出纯数理结构。
|
## 11. Design Constraints
- 不允许情绪化语言、解释命运、AI推理
- 必须输出结构化数据、可计算结果
- 所有计算必须可复现、可验证、可测试

## 12. Dependency Rule
BaZi Engine 依赖 Calendar Engine 为唯一输入来源。禁止AI直接输入、State Engine反向修改。

## 13. Error Handling
{error: CALCULATION_ERROR, stage, message}

## 14. Performance Requirement
单次计算 < 200ms，无AI依赖，可批量计算。

## 15. Testing Strategy

### 15.1 Regression Tests
已知八字对照测试、时间回归测试、节气边界测试、闰年测试。

### 15.2 Golden Dataset
BaZi Engine 上线前必须建立 Golden Dataset（最少 50 个经人工验证的命盘用例）作为回归基准。详见 `21-Testing-Specification.md` 第 6 章。

### 15.3 Test Requirements
- 四柱/十神/五行计算结果必须与 Golden Dataset 100% 匹配
- 任何不匹配视为 P0 缺陷，阻塞上线
- 每次新增计算逻辑需同步扩展 Golden Dataset

## 16. Architecture Philosophy
BaZi Engine 的本质：把时间变成结构化命理数据。

## 17. Extension (V2)
AI辅助修正、命盘对比系统、多流派支持（子平/紫微）、历史人物验证系统。
