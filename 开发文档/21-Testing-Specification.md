# Life Navigation System — Testing Specification

> Version: 1.0 | Status: Frozen

## 1. Purpose
定义 LNS 系统的测试体系，确保每个模块可验证、可回归、可覆盖。

## 2. Test Layers

### 2.1 单元测试
覆盖所有 Engine 的核心计算函数。包括：Calendar Engine 时间转换、BaZi Engine 四柱计算、Ten Gods Engine、Five Elements Engine、Luck Cycle Engine。

### 2.2 Engine 测试
每个 Engine 必须通过独立输入/输出合同测试。

### 2.3 Prompt 回归测试
每次 Prompt 修改必须运行回归测试，确保输出结构不变。

### 2.4 AI 输出一致性测试
对固定输入验证 AI 输出是否符合统一四段式结构（状态→时间→建议→解释）。

### 2.5 命盘基准测试（Golden Dataset）
建立已知八字的 Golden Dataset，每个已知八字验证：四柱、十神、五行、大运、神煞全部计算正确。已知八字对照测试、时间回归测试、节气边界测试、闰年测试，请参见第6章 Golden Dataset (BaZi Benchmark) 的详细规范。

## 3. Test Requirements
- 单元测试覆盖率 > 90%
- 边界测试：节气边界、闰年、时区边界、DST 切换日
- 回归测试每次部署前必须通过
- AI 输出一致性每轮 Prompt 修改后验证 20+ 样本

## 6. Golden Dataset (BaZi Benchmark)

### 6.1 Purpose
这是 BaZi Engine 上线前的第一道硬性前提。必须有至少 50 个经人工验证的命盘用例，作为回归基准。

### 6.2 Two-Layer Structure

**第一层——公开历史人物命盘（约20个）**，用来验证计算正确性。

来源：命理界有共识的历史人物案例，出生时间有史料记载，且网上有多个命理网站独立计算结果可供交叉验证。

步骤：
1. 找 5-8 个主流命理网站（如命理网、八字算命网等）
2. 对同一出生时间分别计算
3. 取其中结果一致的作为 Ground Truth
4. 结果有分歧的，标注分歧来源（通常是节气边界或夜子时处理方式不同），暂不纳入数据

**第二层——边界测试用例（约30个）**，专门覆盖计算容易出错的点：
- 节气当天出生（立春前后1小时内）
- 夜子时（23:00-00:00）出生
- 闰月出生
- 跨年节气（立春在1月下旬或2月上旬的年份）
- DST 切换当天出生（如1980年代中国实行夏令时期间）
- 海外出生（需时区转换）

这30个用例不需要外部验证，只需要把预期输出手工计算一遍，写成 {input, expected_output} 格式。

### 6.3 Dataset Format

```json
{
  "id": "golden_001",
  "description": "历史人物-公开命盘",
  "input": {
    "birth_date": "1893-12-26",
    "birth_time": "07:30",
    "birth_place": {"city": "湘潭", "country": "CN"},
    "gender": "male"
  },
  "expected": {
    "year_pillar": "癸巳",
    "month_pillar": "甲子",
    "day_pillar": "丁酉",
    "hour_pillar": "甲辰",
    "day_master": "丁",
    "five_elements": {"fire": 2, "water": 2, "wood": 2, "metal": 2, "earth": 2}
  },
  "source": "cross_validated",
  "notes": "节气验证点：1893年立春为2月4日"
}
```

### 6.4 绝对通过标准

#### 标准来源
彻底放弃对齐外部商业网站，将 **《三命通会》与《子平真诠》古典数理逻辑化后的算法** 作为唯一绝对标准答案。

#### 边界判定
凡交接点在 1 秒以内的边界盘，一律以 Calendar Engine 基于紫金山天文台历法数据推导出的真太阳时为准。Expected Output 由首席命理架构师人工锁定，不匹配则直接阻塞系统上线。

#### 执行红线
1. 每次 BaZi Engine 代码变更后，必须完整运行 Golden Dataset 回归
2. 四柱/十神/五行计算结果必须与古典算法 100% 匹配
3. 任何不匹配视为优先级 P0 缺陷，阻塞上线
4. 扩展：每次新增计算逻辑，需同步扩展数据集

### 6.5 Effort Estimate
一个人 3-5 天可完成 50 个用例的整理。
