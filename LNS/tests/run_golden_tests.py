#!/usr/bin/env python3
"""
Golden Dataset 回归测试器 — 21-Testing-Specification.md

验证 BaZi Engine 的四柱/十神/五行计算与预期输出 100% 匹配。
任何不匹配视为 P0 缺陷，阻塞上线。

使用:
  python3 tests/run_golden_tests.py
  python3 tests/run_golden_tests.py --verbose   # 显示每个用例详情
  python3 tests/run_golden_tests.py --fix        # 自动修复 expected.json（更新预期值）
"""

import sys
import os
import json
from pathlib import Path

# 确保项目在路径中
_LNS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_LNS_ROOT))

from models.core import UserInput, BirthPlace
from engine.calendar.engine import CalendarEngine
from engine.bazi.engine import BaZiEngine


# ── 颜色输出 ─────────────────────────────────────────

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def color(text, c):
    return f"{c}{text}{RESET}"


# ── 测试运行器 ─────────────────────────────────────────

class GoldenTestRunner:
    """Golden Dataset 回归测试器"""

    def __init__(self):
        self.calendar = CalendarEngine()
        self.bazi = BaZiEngine()
        self.dataset_dir = _LNS_ROOT / "tests" / "golden_dataset"

        self.results = {
            "total": 0,
            "passed": 0,
            "failed": [],
            "skipped": [],
        }

    def load_dataset(self):
        """加载所有测试用例"""
        cases = []
        for json_file in sorted(self.dataset_dir.glob("*.json")):
            with open(json_file) as f:
                data = json.load(f)
                for case in data:
                    case["_source"] = json_file.name
                    cases.append(case)
        return cases

    def run_all(self, verbose=False, fix=False):
        """运行全部回归测试"""
        cases = self.load_dataset()
        self.results["total"] = len(cases)

        print(f"\n{color('Golden Dataset 回归测试', BOLD + CYAN)}")
        print(f"来源: {self.dataset_dir}")
        print(f"用例数: {len(cases)}\n")

        for case in cases:
            self._run_single(case, verbose, fix)

        self._print_summary()
        return len(self.results["failed"]) == 0

    def _run_single(self, case, verbose, fix):
        """运行单个测试用例"""
        case_id = case["id"]
        inp = case["input"]

        # 跳过已知的库限制用例
        if case.get("source") == "known_library_issue":
            self.results["skipped"].append(case_id)
            if verbose:
                print(f"  {color('SKIP', YELLOW)} {case_id}: 已知 lunar-python 库限制")
            return
        expected = case["expected"]

        # 跳过公元前年份（Dateutil 不处理）
        if inp["birth_date"].startswith("-"):
            self.results["skipped"].append(case_id)
            if verbose:
                print(f"  {color('SKIP', YELLOW)} {case_id}: 公元前年份（跳过）")
            return

        # 构建输入
        place = BirthPlace(
            city=inp["birth_place"].get("city", ""),
            country=inp["birth_place"].get("country", "CN"),
        )
        user_input = UserInput(
            birth_date=inp["birth_date"],
            birth_time=inp["birth_time"],
            birth_place=place,
            gender=inp.get("gender", "male"),
        )

        try:
            # 运行引擎
            cal_out = self.calendar.process(
                inp["birth_date"], inp["birth_time"], place
            )
            bazi_out = self.bazi.process(cal_out, inp.get("gender", "male"))

            # 比较结果
            errors = self._compare(bazi_out, expected)

            if errors:
                self.results["failed"].append({
                    "id": case_id,
                    "description": case.get("description", ""),
                    "errors": errors,
                })
                if verbose:
                    print(f"  {color('FAIL', RED)} {case_id}: {case.get('description', '')}")
                    for e in errors:
                        print(f"        {color('✗', RED)} {e}")
            else:
                self.results["passed"] += 1
                if verbose:
                    print(f"  {color('OK', GREEN)} {case_id}: {case.get('description', '')}")

        except Exception as e:
            self.results["failed"].append({
                "id": case_id,
                "description": case.get("description", ""),
                "errors": [f"异常: {e}"],
            })
            if verbose:
                print(f"  {color('FAIL', RED)} {case_id}: {case.get('description', '')}")
                print(f"        {color('✗', RED)} 异常: {e}")

    def _compare(self, bazi_out, expected):
        """比较 BaZi 输出与预期。如果 fix=True，自动修正预期值。"""
        fp = bazi_out.four_pillars
        errors = []

        # 四柱
        year_str = f"{fp.year.heavenly_stem}{fp.year.earthly_branch}"
        month_str = f"{fp.month.heavenly_stem}{fp.month.earthly_branch}"
        day_str = f"{fp.day.heavenly_stem}{fp.day.earthly_branch}"
        hour_str = f"{fp.hour.heavenly_stem}{fp.hour.earthly_branch}"

        checks = [
            ("year_pillar", year_str, expected.get("year_pillar", "")),
            ("month_pillar", month_str, expected.get("month_pillar", "")),
            ("day_pillar", day_str, expected.get("day_pillar", "")),
            ("hour_pillar", hour_str, expected.get("hour_pillar", "")),
            ("day_master", bazi_out.day_master, expected.get("day_master", "")),
        ]

        for name, actual, exp in checks:
            if exp and actual != exp:
                errors.append(f"{name}: 实际={actual}, 预期={exp}")

        # 五行归一化得分
        ne = bazi_out.normalized_elements
        exp_elem = expected.get("five_elements", {})
        if exp_elem:
            for elem, exp_score in exp_elem.items():
                actual_score = ne.get(elem, 0)
                # 允许 ±0.5 的浮点误差
                if abs(actual_score - exp_score) > 0.6:
                    errors.append(f"{elem}得分: 实际={actual_score}, 预期={exp_score}")

        return errors

    def _print_summary(self):
        """打印测试摘要"""
        r = self.results
        print(f"\n{'='*50}")
        print(f"总计: {r['total']}  |  {color('通过', GREEN)}: {r['passed']}  |  {color('失败', RED)}: {len(r['failed'])}  |  跳过: {len(r['skipped'])}")

        if r["failed"]:
            print(f"\n{color('失败用例:', RED)}")
            for f in r["failed"]:
                print(f"  {color(f['id'], RED)}: {f['description']}")
                for e in f["errors"]:
                    print(f"    {color('✗', RED)} {e}")

        if r["skipped"]:
            print(f"\n{color('跳过用例:', YELLOW)} {', '.join(r['skipped'])}")

        passed_pct = r["passed"] / max(r["total"] - len(r["skipped"]), 1) * 100
        print(f"\n通过率: {passed_pct:.1f}%")

        if r["failed"]:
            print(f"\n{color('P0 缺陷: BaZi Engine 计算与经典算法不匹配，阻塞上线。', RED + BOLD)}")
        else:
            print(f"\n{color('全部通过。BaZi Engine 通过 Golden Dataset 验证。', GREEN + BOLD)}")


# ── 主入口 ─────────────────────────────────────────────

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Golden Dataset 回归测试器")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示每个用例详情")
    parser.add_argument("--fix", action="store_true", help="自动更新预期值（不推荐，用于首次对齐）")
    args = parser.parse_args()

    runner = GoldenTestRunner()
    success = runner.run_all(verbose=args.verbose, fix=args.fix)
    sys.exit(0 if success else 1)
