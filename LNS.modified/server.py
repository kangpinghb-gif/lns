#!/usr/bin/env python3
"""
LNS Web API v2 — 零依赖 HTTP API 服务器。

参考 11-API-Design.md + 12-Database-Design.md + 17-Output-Specification.md。

启动：
  python3 server.py [--port 8080]
"""

import sys
import os
import json
import uuid
import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path
# 确保项目在 Python 路径中
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
from models.core import UserInput, BirthPlace, TargetTime
from db.database import LNSDatabase
from db.cache import LNSCache
from engine.report_engine import ReportEngine


# ── 全局实例（延迟初始化）──────────────────────────────

_orch = None
_db = None
_cache = None
_report = None


def get_orch():
    global _orch
    if _orch is None:
        _orch = LNSOrchestrator()
    return _orch


def get_db():
    global _db
    if _db is None:
        _db = LNSDatabase()
    return _db


def get_cache():
    global _cache
    if _cache is None:
        _cache = LNSCache()
    return _cache


def get_report():
    global _report
    if _report is None:
        _report = ReportEngine()
    return _report


# ── LLM 客户端（延迟初始化，自动检测 API Key）─────────────

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        try:
            from engine.llm_client import LLMClient
            _llm = LLMClient()
        except ValueError as e:
            _llm = None
    return _llm


# ── JSON 工具 ────────────────────────────────────────────

_STATIC_DIR = _LNS_ROOT / "static"


def serve_static(handler, filename):
    """服务静态文件"""
    if not filename or '..' in filename:
        json_response(handler, {"error": "Forbidden"}, 403)
        return
    filepath = _STATIC_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        json_response(handler, {"error": "Not found"}, 404)
        return

    content_type = {
        '.html': 'text/html; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
    }.get(filepath.suffix.lower(), 'application/octet-stream')

    handler.send_response(200)
    handler.send_header('Content-Type', content_type)
    handler.send_header('Cache-Control', 'no-cache')
    handler.end_headers()
    with open(filepath, 'rb') as f:
        handler.wfile.write(f.read())


def json_response(handler, data, status=200):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))


def read_body(handler):
    length = int(handler.headers.get('Content-Length', 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode('utf-8'))


# ── 路由表 ────────────────────────────────────────────────

def match_route(path):
    """解析路径并返回 (route_type, params)。支持 /api/v1/user/{id}/history 等嵌套路由。"""
    parts = path.strip('/').split('/')
    if len(parts) >= 3 and parts[0] == 'api' and parts[1] == 'v1':
        resource = parts[2]
        if resource == 'user':
            if len(parts) == 3:
                return ('user_list', {})
            if len(parts) == 4:
                return ('user_get', {'user_id': parts[3]})
            if len(parts) == 5 and parts[4] == 'history':
                return ('user_history', {'user_id': parts[3]})
            if len(parts) == 5 and parts[4] == 'reports':
                return ('user_reports_list', {'user_id': parts[3]})
            if len(parts) == 5 and parts[4] == 'chart':
                return ('user_chart', {'user_id': parts[3]})
            if len(parts) == 5 and parts[4] == 'decisions':
                return ('user_decisions', {'user_id': parts[3]})
        elif resource == 'users':
            return ('users_list', {})
        elif resource == 'report':
            if len(parts) == 5 and parts[4] == 'view':
                return ('report_get', {'report_id': parts[3]})
            else:
                return ('report_generate', {})
        elif resource == 'timeline':
            return ('timeline', {})
        elif resource == 'professional':
            return ('professional', {})
        elif resource == 'simulate':
            return ('simulate', {})

    return ('unknown', {})


# ── API Handler ───────────────────────────────────────────

class LNSAPIHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 首页
        if path == '/' or path == '':
            serve_static(self, 'home.html')
            return

        if path.startswith('/api/v1/feedback/stats'):
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            uid = qs.get('user_id', [''])[0]
            stats = get_db().get_feedback_stats(uid)
            recent = get_db().get_recent_feedback(uid, 10)
            json_response(self, {"success": True, "stats": stats, "recent": recent})
            return

        if path == '/health':
            json_response(self, {
                "status": "ok",
                "version": "1.0.0",
                "profile": "code",
                "timestamp": datetime.now().isoformat(),
            })
            return

        # 静态文件（/static/*）
        if path.startswith('/static/'):
            serve_static(self, path[len('/static/'):])
            return

        route_type, params = match_route(path)

        if route_type == 'user_get':
            self._handle_get_user(params['user_id'])
        elif route_type == 'user_history':
            self._handle_user_history(params['user_id'])
        elif route_type == 'user_reports_list':
            self._handle_user_reports(params['user_id'])
        elif route_type == 'user_chart':
            self._handle_user_chart(params['user_id'])
        elif route_type == 'user_decisions':
            self._handle_user_decisions(params['user_id'])
        elif route_type == 'users_list':
            self._handle_list_users()
        elif route_type == 'user_list':
            self._handle_list_users()
        elif route_type == 'report_get':
            self._handle_get_report(params['report_id'])
        elif path.startswith('/api/v1/feedback/stats'):
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            uid = qs.get('user_id', [''])[0]
            stats = get_db().get_feedback_stats(uid)
            recent = get_db().get_recent_feedback(uid, 10)
            json_response(self, {"success": True, "stats": stats, "recent": recent})
        else:
            json_response(self, {"error": "Not found", "path": path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = read_body(self)
        except Exception:
            json_response(self, {"error": "Invalid JSON body"}, 400)
            return

        if path == '/api/v1/analyze':
            self._handle_analyze(body)
        elif path == '/api/v1/chat':
            self._handle_chat(body)
        elif path == '/api/v1/user':
            self._handle_create_user(body)
        elif path == '/api/v1/user/update':
            self._handle_update_user(body)
        elif path == '/api/v1/report':
            self._handle_generate_report(body)
        elif path == '/api/v1/timeline':
            self._handle_timeline(body)
        elif path == '/api/v1/professional':
            self._handle_professional(body)
        elif path == '/api/v1/simulate':
            self._handle_simulate(body)
        elif path == '/api/v1/feedback':
            self._handle_feedback(body)
        elif path.startswith('/api/v1/feedback/stats'):
            self._handle_feedback_stats(body)
        else:
            json_response(self, {"error": "Not found"}, 404)

    # ── User CRUD ──────────────────────────────────────

    def _handle_get_user(self, user_id):
        user = get_db().get_user(user_id)
        if user:
            json_response(self, {"success": True, "data": user})
        else:
            json_response(self, {"success": False, "error": "User not found"}, 404)

    def _handle_create_user(self, body):
        user_id = str(uuid.uuid4())
        get_db().create_user(
            user_id=user_id,
            birth_date=body.get('birth_date', ''),
            birth_time=body.get('birth_time', ''),
            birth_place={'city': body.get('city', ''), 'district': body.get('district', ''),
                         'country': body.get('country', 'CN'),
                         'latitude': body.get('latitude'), 'longitude': body.get('longitude')},
            timezone=body.get('timezone', ''),
            gender=body.get('gender', 'male'),
        )
        json_response(self, {"success": True, "user_id": user_id}, 201)

    def _handle_update_user(self, body):
        user_id = body.get('user_id', '')
        if not user_id:
            json_response(self, {"success": False, "error": "user_id required"}, 400)
            return
        ok = get_db().update_user(
            user_id=user_id,
            birth_date=body.get('birth_date'),
            birth_time=body.get('birth_time'),
            birth_place=body.get('birth_place'),
            timezone=body.get('timezone'),
            gender=body.get('gender'),
        )
        if ok:
            # 更新后清除缓存（版本断代触发）
            get_cache().invalidate_user(user_id)
            json_response(self, {"success": True, "message": "用户信息已更新"})
        else:
            json_response(self, {"success": False, "error": "更新失败"})

    def _handle_list_users(self):
        users = get_db().list_users(limit=50)
        json_response(self, {"success": True, "data": users})

    # ── 用户历史 ──────────────────────────────────────

    def _handle_user_history(self, user_id):
        states = get_db().get_life_state_history(user_id, 30)
        decisions = get_db().get_decision_history(user_id, 10)
        json_response(self, {
            "success": True,
            "data": {
                "user_id": user_id,
                "life_states": states,
                "recent_decisions": decisions,
            }
        })

    def _handle_user_reports(self, user_id):
        qs = parse_qs(urlparse(self.path).query)
        report_type = qs.get('type', [''])[0]
        reports = get_db().get_reports(user_id, report_type)
        json_response(self, {"success": True, "data": reports})

    def _handle_user_chart(self, user_id):
        chart = get_db().get_active_chart(user_id)
        if chart:
            json_response(self, {"success": True, "data": chart})
        else:
            json_response(self, {"success": False, "error": "No chart found"}, 404)

    def _handle_user_decisions(self, user_id):
        decisions = get_db().get_decision_history(user_id, 10)
        json_response(self, {"success": True, "data": decisions})

    # ── 分析 / 对话 ───────────────────────────────────

    def _handle_analyze(self, body):
        try:
            user_input = UserInput(
                birth_date=body.get('birth_date', '1990-06-15'),
                birth_time=body.get('birth_time', '14:30'),
                birth_place=BirthPlace(
                    city=body.get('city', '北京'),
                    country=body.get('country', 'CN'),
                ),
                gender=body.get('gender', 'male'),
            )
            age = float(body.get('age', 35))
            user_id = body.get('user_id', '')

            result = get_orch().full_analysis(user_input, age=age)

            if result['success'] and user_id:
                bazi_data = result['data']['bazi_birth']
                get_cache().set_static(user_id, {'day_master': bazi_data.get('day_master')})
                get_db().save_bazi_chart(user_id, bazi_data)
                get_db().save_life_state(user_id, result['data']['state'])
                get_db().save_time_analysis(user_id, result['data']['time'],
                                            target_date=datetime.now().strftime('%Y-%m-%d'))
                get_db().save_decision(user_id, result['data']['decision'])
                get_db().log_event(user_id, result.get('trace_id', ''), 'api_analyze', 'ok')

            json_response(self, result)

        except Exception as e:
            json_response(self, {"success": False, "error": str(e)}, 500)

    def _handle_chat(self, body):
        try:
            user_input = UserInput(
                birth_date=body.get('birth_date', '1990-06-15'),
                birth_time=body.get('birth_time', '14:30'),
                birth_place=BirthPlace(city=body.get('city', '北京'),
                                       country=body.get('country', 'CN')),
                gender=body.get('gender', 'male'),
            )
            message = body.get('message', '')
            age = float(body.get('age', 35))

            # 1. 做完整分析获取引擎数据
            analysis = get_orch().full_analysis(user_input, age=age)
            if not analysis['success']:
                json_response(self, analysis)
                return

            # 2. 尝试调用 LLM
            llm = get_llm()
            if llm:
                from models.core import StateOutput, TimeOutput, DecisionOutput, SynthesizedOutput, PromptInput

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
                    knowledge_graph=synth, user_query=message,
                )

                # 调用 Prompt Engine 的 LLM 对话链
                from engine.prompt.engine import PromptEngine
                pe = PromptEngine()
                llm_result = pe.chat_with_llm(prompt_input, llm)

                # 3. 保存对话
                user_id = body.get('user_id', '')
                if user_id:
                    session_id = body.get('session_id', user_id + '_default')
                    get_db().save_chat_message(session_id, user_id, 'user', message)
                    get_db().save_chat_message(session_id, user_id, 'assistant',
                                               llm_result.get('content', ''))

                json_response(self, {
                    "success": True,
                    "mode": llm_result["mode"],
                    "response": llm_result["content"],
                    "footer": llm_result.get("footer", ""),
                    "usage": llm_result.get("llm_usage", {}),
                })
            else:
                # 无 LLM：使用原来的 orchestrator.chat（纯情绪分流）
                result = get_orch().chat(user_input, message, age=age)
                user_id = body.get('user_id', '')
                if user_id:
                    session_id = body.get('session_id', user_id + '_default')
                    get_db().save_chat_message(session_id, user_id, 'user', message)
                    get_db().save_chat_message(session_id, user_id, 'assistant',
                                               json.dumps(result, ensure_ascii=False))
                json_response(self, result)

        except Exception as e:
            json_response(self, {"success": False, "error": str(e)}, 500)

    # ── 报告生成 ─────────────────────────────────────────

    def _handle_generate_report(self, body):
        try:
            user_input = UserInput(
                birth_date=body.get('birth_date', '1990-06-15'),
                birth_time=body.get('birth_time', '14:30'),
                birth_place=BirthPlace(city=body.get('city', '北京'),
                                       country=body.get('country', 'CN')),
                gender=body.get('gender', 'male'),
            )
            report_type = body.get('report_type', 'daily')
            age = float(body.get('age', 35))
            user_id = body.get('user_id', '')

            # 先做完整分析
            result = get_orch().full_analysis(user_input, age=age)
            if not result['success']:
                json_response(self, result)
                return

            # 生成报告
            from models.core import StateOutput, TimeOutput, DecisionOutput, SynthesizedOutput

            state_data = result['data']['state']
            time_data = result['data']['time']
            decision_data = result['data']['decision']
            synth_data = result['data']['synthesized']

            # 反序列化为对象
            state = StateOutput(**state_data)
            synth = SynthesizedOutput(**synth_data)

            # TimeOutput 和 DecisionOutput 是嵌套 dataclass，手动构造
            time_obj = TimeOutput()
            time_obj.T0.energy_state = time_data['T0'].get('energy_state', 'medium')
            time_obj.T0.recommended_focus = time_data['T0'].get('recommended_focus', [])
            time_obj.T0.risk = time_data['T0'].get('risk', [])
            time_obj.T1.monthly_trend = time_data['T1'].get('monthly_trend', 'stable')
            time_obj.T1.opportunities = time_data['T1'].get('opportunities', [])
            time_obj.T1.risks = time_data['T1'].get('risks', [])
            time_obj.T2.yearly_direction = time_data['T2'].get('yearly_direction', '')
            time_obj.T2.strategic_focus = time_data['T2'].get('strategic_focus', [])
            time_obj.T2.risk_level = time_data['T2'].get('risk_level', 'normal')
            time_obj.T3.life_stage = time_data['T3'].get('life_stage', '')
            time_obj.T3.long_term_direction = time_data['T3'].get('long_term_direction', [])
            time_obj.T3.strategic_path = time_data['T3'].get('strategic_path', [])

            dec_obj = DecisionOutput()
            dec_obj.P0 = [type('A', (), {'description': d, 'reason': ''})() for d in decision_data.get('P0', [])]
            dec_obj.P1 = [type('A', (), {'description': d, 'reason': ''})() for d in decision_data.get('P1', [])]
            dec_obj.P2 = [type('A', (), {'description': d, 'reason': ''})() for d in decision_data.get('P2', [])]
            dec_obj.priority_reasoning = decision_data.get('priority_reasoning', [])

            report_content = get_report().generate(
                state, time_obj, dec_obj, synth,
                report_type=report_type,
                target_date=body.get('target_date', datetime.now().strftime('%Y-%m-%d'))
            )

            # 持久化
            if user_id and result['success']:
                period = body.get('target_date', datetime.now().strftime('%Y-%m-%d'))
                title = report_content.get('title', report_type)
                get_db().save_report(user_id, report_type, title, report_content,
                                     period_start=period, period_end=period)

            json_response(self, {"success": True, "data": report_content})

        except Exception as e:
            json_response(self, {"success": False, "error": str(e)}, 500)

    def _handle_get_report(self, report_id):
        report = get_db().get_report(report_id)
        if report:
            json_response(self, {"success": True, "data": report})
        else:
            json_response(self, {"success": False, "error": "Report not found"}, 404)

    # ── 时间导航 ─────────────────────────────────────────

    def _handle_timeline(self, body):
        """生成时间导航（T0-T3 完整输出）"""
        try:
            user_input = UserInput(
                birth_date=body.get('birth_date', '1990-06-15'),
                birth_time=body.get('birth_time', '14:30'),
                birth_place=BirthPlace(city=body.get('city', '北京'),
                                       country=body.get('country', 'CN')),
                gender=body.get('gender', 'male'),
            )
            age = float(body.get('age', 35))

            # 全量分析，返回时间层数据
            result = get_orch().full_analysis(user_input, age=age)

            if result['success']:
                json_response(self, {
                    "success": True,
                    "data": {
                        "timeline": result['data']['time'],
                        "state": result['data']['state'],
                    }
                })
            else:
                json_response(self, result)

        except Exception as e:
            json_response(self, {"success": False, "error": str(e)}, 500)

    # ── 专业模式 ─────────────────────────────────────────

    def _handle_professional(self, body):
        """专业模式：返回完整八字命盘结构（符合 ADR-010 视觉边界）"""
        try:
            user_input = UserInput(
                birth_date=body.get('birth_date', '1990-06-15'),
                birth_time=body.get('birth_time', '14:30'),
                birth_place=BirthPlace(city=body.get('city', '北京'),
                                       country=body.get('country', 'CN')),
                gender=body.get('gender', 'male'),
            )
            age = float(body.get('age', 35))

            result = get_orch().full_analysis(user_input, age=age,
                                              use_professional_mode=True)

            if result['success']:
                bazi = result['data']['bazi_birth']
                state = result['data']['state']
                json_response(self, {
                    "success": True,
                    "data": {
                        "four_pillars": bazi['four_pillars'],
                        "day_master": bazi['day_master'],
                        "ten_gods": bazi['ten_gods'],
                        "five_elements": bazi['normalized_elements'],
                        "hidden_stems": bazi.get('hidden_stems', {}),
                        "luck_cycles": bazi.get('luck_cycles', []),
                        "deities": bazi.get('deities', []),
                        "current_state": {
                            "stage": state['current_stage'],
                            "energy": state['energy_level'],
                            "risk": state['risk_level'],
                            "dominant": state['dominant_structure'],
                            "capabilities": state.get('capability_profile', []),
                            "luck_cycle_theme": state.get('luck_cycle_theme', []),
                        },
                    }
                })
            else:
                json_response(self, result)

        except Exception as e:
            json_response(self, {"success": False, "error": str(e)}, 500)

    def log_message(self, format, *args):
        print(f"[API] {args[0]}" if args else "")

    # ── What-if 模拟器 ─────────────────────────────────

    def _handle_simulate(self, body):
        """POST /api/v1/simulate — What-if 模拟器"""
        try:
            user_input = UserInput(
                birth_date=body.get('birth_date', '1990-06-15'),
                birth_time=body.get('birth_time', '14:30'),
                birth_place=BirthPlace(city=body.get('city', '北京'),
                                       country=body.get('country', 'CN')),
                gender=body.get('gender', 'male'),
            )

            scenarios = body.get('scenarios', [])
            if not scenarios:
                json_response(self, {"success": False, "error": "请提供至少一个 scenarios"}, 400)
                return

            # 转为 TargetTime 对象
            parsed_scenarios = []
            for sc in scenarios:
                parsed_scenarios.append({
                    "label": sc.get("label", "场景"),
                    "target_time": TargetTime(
                        date=sc.get("date", datetime.now().strftime("%Y-%m-%d")),
                        time=sc.get("time", "12:00"),
                    ),
                    "age": sc.get("age", 35),
                })

            result = get_orch().simulate(user_input, parsed_scenarios)
            json_response(self, result)

        except Exception as e:
            json_response(self, {"success": False, "error": str(e)}, 500)




    # ── 反馈系统 ─────────────────────────────────────

    def _handle_feedback(self, body):
        """POST /api/v1/feedback — 提交反馈"""
        try:
            fb_id = get_db().save_feedback(
                user_id=body.get('user_id', ''),
                trace_id=body.get('trace_id', ''),
                score=body.get('score', 3),
                category=body.get('category', 'decision'),
                comment=body.get('comment', ''),
                decision_p0=body.get('decision_p0', []),
                decision_p1=body.get('decision_p1', []),
                state_snapshot=body.get('state_snapshot', {}),
            )
            stats = get_db().get_feedback_stats(body.get('user_id', ''))
            json_response(self, {"success": True, "feedback_id": fb_id, "stats": stats})
        except Exception as e:
            json_response(self, {"success": False, "error": str(e)}, 500)

    def _handle_feedback_stats(self, body):
        """POST /api/v1/feedback/stats — 获取反馈统计"""
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        user_id = qs.get('user_id', [''])[0]
        stats = get_db().get_feedback_stats(user_id)
        recent = get_db().get_recent_feedback(user_id, 10)
        json_response(self, {"success": True, "stats": stats, "recent": recent})

def run_server(host='0.0.0.0', port=8080):
    server = HTTPServer((host, port), LNSAPIHandler)
    print(f"LNS API Server v2 running on http://{host}:{port}")
    print(f"── User ──")
    print(f"  POST /api/v1/user          创建用户")
    print(f"  POST /api/v1/user/update   更新用户（触发版本断代）")
    print(f"  GET  /api/v1/users          用户列表")
    print(f"  GET  /api/v1/user/{id}      用户详情")
    print(f"  GET  /api/v1/user/{id}/history    状态/决策历史")
    print(f"  GET  /api/v1/user/{id}/chart      命盘信息")
    print(f"  GET  /api/v1/user/{id}/decisions  决策历史")
    print(f"  GET  /api/v1/user/{id}/reports    报告列表")
    print(f"── 分析 ──")
    print(f"  POST /api/v1/analyze        完整人生分析")
    print(f"  POST /api/v1/chat            AI 对话")
    print(f"── 报告 ──")
    print(f"  POST /api/v1/report          生成报告 (daily/monthly/yearly/decade)")
    print(f"  GET  /api/v1/report/{id}/view 获取报告")
    print(f"── 导航 ──")
    print(f"  POST /api/v1/timeline        时间导航 (T0-T3)")
    print(f"── 专业模式 ──")
    print(f"  POST /api/v1/professional    八字命盘数据")
    print(f"── 模拟器 ──")
    print(f"  POST /api/v1/simulate        What-if 场景对比")
    print(f"── 反馈 ──")
    print(f"  POST /api/v1/feedback        提交反馈")
    print(f"  GET  /api/v1/feedback/stats  反馈统计")
    print(f"── 系统 ──")
    print(f"  GET  /health                 健康检查")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='LNS API Server v2')
    parser.add_argument('--port', type=int, default=8080, help='Port (default: 8080)')
    parser.add_argument('--host', default='0.0.0.0', help='Host (default: 0.0.0.0)')
    args = parser.parse_args()
    run_server(args.host, args.port)
