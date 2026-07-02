#!/usr/bin/env python3
"""
LNS — Life Navigation System 命令行入口

使用方式：
  python3 main.py                            # 默认分析
  python3 main.py --chat "今天心情不好"       # AI 对话（走 LLM）
  python3 main.py --chat "我适合换工作吗？"
  python3 main.py --no-llm --chat "..."      # 不走 LLM，只出数据
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

_LNS_ROOT = Path(__file__).resolve().parent
if str(_LNS_ROOT) not in sys.path:
    sys.path.insert(0, str(_LNS_ROOT))

# 加载 .env 环境变量（支持多个可能路径）
_possible_envs = [
    _LNS_ROOT / ".env",
    Path.home() / ".hermes" / "profiles" / "code" / ".env",
    Path.home() / ".hermes" / "profiles" / "code" / ".env.local",
    Path.home() / ".hermes" / ".env",
    Path.home() / ".hermes" / ".env.local",
]
for _env_file in _possible_envs:
    if _env_file.exists():
        with open(_env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

from orchestrator import LNSOrchestrator
from models.core import UserInput, BirthPlace, TargetTime, PromptInput
from models.core import StateOutput, TimeOutput, DecisionOutput, SynthesizedOutput
from engine.prompt.engine import PromptEngine


def main():
    parser = argparse.ArgumentParser(description='LNS — Life Navigation System')
    parser.add_argument('--birth', default='1990-06-15', help='出生日期 YYYY-MM-DD')
    parser.add_argument('--time', default='14:30', help='出生时间 HH:MM')
    parser.add_argument('--city', default='北京', help='出生城市')
    parser.add_argument('--country', default='CN', help='国家代码')
    parser.add_argument('--gender', default='male', help='性别 male/female')
    parser.add_argument('--age', type=float, default=35, help='当前年龄')
    parser.add_argument('--chat', help='AI 对话模式，传入用户消息')
    parser.add_argument('--no-llm', action='store_true', help='不走 LLM，只出结构化数据')
    parser.add_argument('--pretty', action='store_true', help='美化的 JSON 输出')
    parser.add_argument('--output', help='输出到文件')

    args = parser.parse_args()

    user_input = UserInput(
        birth_date=args.birth,
        birth_time=args.time,
        birth_place=BirthPlace(city=args.city, country=args.country),
        gender=args.gender,
    )

    orch = LNSOrchestrator()

    if not args.chat:
        # 完整分析模式
        result = orch.full_analysis(user_input, age=args.age)
        _output(result, args)
        return

    # ── AI 对话模式 ──────────────────────────────────

    if args.no_llm:
        # 不走 LLM：只跑引擎 + 情绪分流
        result = orch.chat(user_input, args.chat, age=args.age)
        _output(result, args)
        return

    # 走 LLM
    try:
        from engine.llm_client import LLMClient
        llm = LLMClient()
    except ValueError as e:
        print(f"[LNS] 未配置 LLM API Key: {e}")
        print("[LNS] 降级为无 AI 模式。设置 DASHSCOPE_API_KEY 或使用 --no-llm")
        result = orch.chat(user_input, args.chat, age=args.age)
        _output(result, args)
        return

    # 完整分析 → Prompt → LLM
    analysis = orch.full_analysis(user_input, age=args.age)
    if not analysis['success']:
        _output(analysis, args)
        return

    sd = analysis['data']['state']
    td = analysis['data']['time']
    dd = analysis['data']['decision']
    kgd = analysis['data']['synthesized']

    state = StateOutput(**sd)
    synth = SynthesizedOutput(**kgd)

    time_obj = TimeOutput()
    time_obj.T0.energy_state = td['T0'].get('energy_state', 'medium')
    time_obj.T0.recommended_focus = td['T0'].get('recommended_focus', [])
    time_obj.T0.risk = td['T0'].get('risk', [])
    time_obj.T1.monthly_trend = td['T1'].get('monthly_trend', 'stable')
    time_obj.T2.yearly_direction = td['T2'].get('yearly_direction', '')
    time_obj.T3.life_stage = td['T3'].get('life_stage', '')

    dec_obj = DecisionOutput()
    dec_obj.P0 = [type('A', (), {'description': d, 'reason': '', 'risk_note': ''})() for d in dd.get('P0', [])]
    dec_obj.P1 = [type('A', (), {'description': d, 'reason': '', 'risk_note': ''})() for d in dd.get('P1', [])]
    dec_obj.P2 = [type('A', (), {'description': d, 'reason': '', 'risk_note': ''})() for d in dd.get('P2', [])]
    dec_obj.P3 = [type('A', (), {'description': d, 'reason': '', 'risk_note': ''})() for d in dd.get('P3', [])]
    dec_obj.priority_reasoning = dd.get('priority_reasoning', [])

    prompt_input = PromptInput(
        state=state, time=time_obj, decision=dec_obj,
        knowledge_graph=synth, user_query=args.chat,
    )

    pe = PromptEngine()
    llm_result = pe.chat_with_llm(prompt_input, llm)

    if args.pretty:
        print("=" * 50)
        print(llm_result["content"])
        print()
        if llm_result.get("data_card"):
            print("--- 数据卡片（兜底） ---")
            print(json.dumps(llm_result["data_card"], ensure_ascii=False, indent=2))
        print(llm_result.get("footer", ""))
        if llm_result.get("llm_usage"):
            print(f"\n--- Tokens: {llm_result['llm_usage'].get('total_tokens', 'N/A')} ---")
    else:
        # JSON 格式（兼容脚本调用）
        if llm_result["mode"] == "data_card":
            result = {
                "success": True,
                "mode": "data_card",
                "message": llm_result["content"],
                "data_card": llm_result.get("data_card"),
            }
        else:
            result = {
                "success": True,
                "mode": llm_result["mode"],
                "response": llm_result["content"],
                "footer": llm_result.get("footer", ""),
                "usage": llm_result.get("llm_usage", {}),
            }
        _output(result, args)


def _output(data, args):
    indent = 2 if args.pretty else None
    output = json.dumps(data, ensure_ascii=False, indent=indent)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Output saved to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
