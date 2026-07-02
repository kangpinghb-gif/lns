"""
LNS 数据库层 — SQLite 持久化实现。

参考 12-Database-Design.md 的 Core Tables 设计。

包含：
- users / bazi_chart / life_state / time_analysis / decisions / chat_sessions / reports
- bazi_chart 版本断代（is_active / deactivated_at / version）
- 事件日志（event_log）

V1 使用 SQLite（零配置），V2 迁移到 PostgreSQL + Redis。
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "lns.db"


def get_db_path():
    """获取数据库路径"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return str(DB_PATH)


def dict_factory(cursor, row):
    """SQLite row → dict"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class LNSDatabase:
    """LNS 数据库操作层"""

    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = dict_factory
        # WAL 模式在某些文件系统上不可用，静默降级
        try:
            self.conn.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        self._init_tables()

    def _init_tables(self):
        """初始化所有表结构"""
        cursor = self.conn.cursor()

        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            birth_date TEXT NOT NULL,
            birth_time TEXT NOT NULL,
            birth_place TEXT NOT NULL DEFAULT '{}',
            timezone TEXT DEFAULT '',
            gender TEXT DEFAULT 'male',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS bazi_chart (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            version TEXT DEFAULT '1.0.0',
            is_active INTEGER DEFAULT 1,
            deactivated_at TIMESTAMP,
            year_pillar TEXT,
            month_pillar TEXT,
            day_pillar TEXT,
            hour_pillar TEXT,
            day_master TEXT,
            ten_gods TEXT DEFAULT '{}',
            five_elements TEXT DEFAULT '{}',
            hidden_stems TEXT DEFAULT '{}',
            luck_cycles TEXT DEFAULT '[]',
            start_age REAL DEFAULT 0.0,
            deities TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS bazi_chart_history (
            id TEXT PRIMARY KEY,
            bazi_chart_id TEXT,
            user_id TEXT,
            year_pillar TEXT, month_pillar TEXT, day_pillar TEXT, hour_pillar TEXT,
            ten_gods TEXT, five_elements TEXT, hidden_stems TEXT, luck_cycles TEXT,
            version TEXT,
            deactivated_at TIMESTAMP,
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS life_state (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            current_stage TEXT,
            energy_level TEXT DEFAULT 'medium',
            risk_level TEXT DEFAULT 'normal',
            dominant_structure TEXT,
            capability_profile TEXT DEFAULT '[]',
            behavior_patterns TEXT DEFAULT '[]',
            luck_cycle_theme TEXT DEFAULT '[]',
            stage_derivation TEXT DEFAULT 'age_based',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS time_analysis (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            t0 TEXT DEFAULT '{}',
            t1 TEXT DEFAULT '{}',
            t2 TEXT DEFAULT '{}',
            t3 TEXT DEFAULT '{}',
            target_date TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            p0 TEXT DEFAULT '[]',
            p1 TEXT DEFAULT '[]',
            p2 TEXT DEFAULT '[]',
            p3 TEXT DEFAULT '[]',
            decision_logic TEXT DEFAULT '{}',
            priority_reasoning TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            messages TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS event_log (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            trace_id TEXT,
            stage TEXT,
            status TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            report_type TEXT NOT NULL,
            title TEXT,
            content TEXT DEFAULT '{}',
            period_start TEXT,
            period_end TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            trace_id TEXT,
            category TEXT DEFAULT 'decision',
            score INTEGER DEFAULT 3,
            comment TEXT DEFAULT '',
            decision_p0 TEXT DEFAULT '[]',
            decision_p1 TEXT DEFAULT '[]',
            state_snapshot TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id);
        CREATE INDEX IF NOT EXISTS idx_feedback_score ON feedback(score);

        CREATE INDEX IF NOT EXISTS idx_bazi_user ON bazi_chart(user_id, is_active);
        CREATE INDEX IF NOT EXISTS idx_bazi_history ON bazi_chart_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_life_state_user ON life_state(user_id);
        CREATE INDEX IF NOT EXISTS idx_decisions_user ON decisions(user_id);
        CREATE INDEX IF NOT EXISTS idx_event_log ON event_log(user_id, trace_id);
        """)

        self.conn.commit()

    # ── User ─────────────────────────────────────────────

    def create_user(self, user_id, birth_date, birth_time,
                    birth_place=None, timezone="", gender="male"):
        """创建用户"""
        self.conn.execute(
            "INSERT OR IGNORE INTO users (id, birth_date, birth_time, birth_place, timezone, gender) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, birth_date, birth_time,
             json.dumps(birth_place, ensure_ascii=False) if birth_place else '{}',
             timezone, gender)
        )
        self.conn.commit()

    def get_user(self, user_id):
        """获取用户"""
        c = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return c.fetchone()

    # ── BaZi Chart ────────────────────────────────────────

    def save_bazi_chart(self, user_id, bazi_data):
        """保存命盘（版本断代：自动将旧版 is_active 置为 false）"""
        chart_id = str(uuid.uuid4())

        # 先停用当前活跃的旧版
        self.conn.execute(
            "UPDATE bazi_chart SET is_active = 0, deactivated_at = CURRENT_TIMESTAMP "
            "WHERE user_id = ? AND is_active = 1",
            (user_id,)
        )
        # 归档旧版
        old = self.conn.execute(
            "SELECT * FROM bazi_chart WHERE user_id = ? AND is_active = 0 "
            "AND deactivated_at IS NOT NULL ORDER BY deactivated_at DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        if old:
            self.conn.execute(
                "INSERT INTO bazi_chart_history "
                "(id, bazi_chart_id, user_id, year_pillar, month_pillar, day_pillar, hour_pillar, "
                "ten_gods, five_elements, hidden_stems, luck_cycles, version, deactivated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), old['id'], user_id,
                 old['year_pillar'], old['month_pillar'], old['day_pillar'], old['hour_pillar'],
                 old['ten_gods'], old['five_elements'], old['hidden_stems'], old['luck_cycles'],
                 old['version'], old['deactivated_at'])
            )

        fp = bazi_data.get('four_pillars', {})
        self.conn.execute(
            "INSERT INTO bazi_chart "
            "(id, user_id, is_active, year_pillar, month_pillar, day_pillar, hour_pillar, "
            "day_master, ten_gods, five_elements, hidden_stems, luck_cycles, start_age, deities) "
            "VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (chart_id, user_id,
             fp.get('year', {}).get('stem', '') + fp.get('year', {}).get('branch', ''),
             fp.get('month', {}).get('stem', '') + fp.get('month', {}).get('branch', ''),
             fp.get('day', {}).get('stem', '') + fp.get('day', {}).get('branch', ''),
             fp.get('hour', {}).get('stem', '') + fp.get('hour', {}).get('branch', ''),
             bazi_data.get('day_master', ''),
             json.dumps(bazi_data.get('ten_gods', {}), ensure_ascii=False),
             json.dumps(bazi_data.get('normalized_elements', {}), ensure_ascii=False),
             json.dumps(bazi_data.get('hidden_stems', {}), ensure_ascii=False),
             json.dumps(bazi_data.get('luck_cycles', []), ensure_ascii=False),
             bazi_data.get('start_age', 0.0),
             json.dumps(bazi_data.get('deities', []), ensure_ascii=False))
        )
        self.conn.commit()
        return chart_id

    def get_active_chart(self, user_id):
        """获取当前活跃命盘"""
        c = self.conn.execute(
            "SELECT * FROM bazi_chart WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        return c.fetchone()

    # ── Life State ────────────────────────────────────────

    def save_life_state(self, user_id, state_data):
        """保存人生状态"""
        state_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO life_state "
            "(id, user_id, current_stage, energy_level, risk_level, dominant_structure, "
            "capability_profile, behavior_patterns, luck_cycle_theme) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (state_id, user_id,
             state_data.get('current_stage', ''),
             state_data.get('energy_level', 'medium'),
             state_data.get('risk_level', 'normal'),
             state_data.get('dominant_structure', ''),
             json.dumps(state_data.get('capability_profile', []), ensure_ascii=False),
             json.dumps(state_data.get('behavior_patterns', []), ensure_ascii=False),
             json.dumps(state_data.get('luck_cycle_theme', []), ensure_ascii=False))
        )
        self.conn.commit()
        return state_id

    # ── Time Analysis ─────────────────────────────────────

    def save_time_analysis(self, user_id, time_data, target_date=""):
        """保存时间分析"""
        ta_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO time_analysis (id, user_id, t0, t1, t2, t3, target_date) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ta_id, user_id,
             json.dumps(time_data.get('T0', {}), ensure_ascii=False),
             json.dumps(time_data.get('T1', {}), ensure_ascii=False),
             json.dumps(time_data.get('T2', {}), ensure_ascii=False),
             json.dumps(time_data.get('T3', {}), ensure_ascii=False),
             target_date)
        )
        self.conn.commit()
        return ta_id

    # ── Decisions ─────────────────────────────────────────

    def save_decision(self, user_id, decision_data):
        """保存决策"""
        dec_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO decisions (id, user_id, p0, p1, p2, p3, decision_logic, priority_reasoning) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (dec_id, user_id,
             json.dumps(decision_data.get('P0', []), ensure_ascii=False),
             json.dumps(decision_data.get('P1', []), ensure_ascii=False),
             json.dumps(decision_data.get('P2', []), ensure_ascii=False),
             json.dumps(decision_data.get('P3', []), ensure_ascii=False),
             json.dumps(decision_data.get('decision_logic', {}), ensure_ascii=False),
             json.dumps(decision_data.get('priority_reasoning', []), ensure_ascii=False))
        )
        self.conn.commit()
        return dec_id

    # ── Event Log ─────────────────────────────────────────

    def log_event(self, user_id, trace_id, stage, status, message=""):
        """记录事件日志"""
        self.conn.execute(
            "INSERT INTO event_log (id, user_id, trace_id, stage, status, message) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, trace_id, stage, status, message)
        )
        self.conn.commit()

    def get_recent_logs(self, user_id="", limit=20):
        """获取最近日志"""
        if user_id:
            c = self.conn.execute(
                "SELECT * FROM event_log WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            c = self.conn.execute(
                "SELECT * FROM event_log ORDER BY created_at DESC LIMIT ?", (limit,)
            )
        return c.fetchall()

    # ── 会话管理 ─────────────────────────────────────────

    def save_chat_message(self, session_id, user_id, role, content):
        """保存聊天消息"""
        session = self.conn.execute(
            "SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if session:
            messages = json.loads(session['messages'])
            messages.append({"role": role, "content": content, "time": datetime.now().isoformat()})
            self.conn.execute(
                "UPDATE chat_sessions SET messages = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE session_id = ?",
                (json.dumps(messages, ensure_ascii=False), session_id)
            )
        else:
            messages = [{"role": role, "content": content, "time": datetime.now().isoformat()}]
            self.conn.execute(
                "INSERT INTO chat_sessions (session_id, user_id, messages) VALUES (?, ?, ?)",
                (session_id, user_id, json.dumps(messages, ensure_ascii=False))
            )
        self.conn.commit()

    def list_users(self, limit=20):
        """列出所有用户"""
        c = self.conn.execute(
            "SELECT id, birth_date, birth_time, gender, created_at FROM users ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return c.fetchall()

    def search_users(self, keyword=""):
        """搜索用户（按 ID 或生日）"""
        pattern = f"%{keyword}%"
        c = self.conn.execute(
            "SELECT id, birth_date, birth_time, gender, created_at FROM users "
            "WHERE id LIKE ? OR birth_date LIKE ? ORDER BY created_at DESC LIMIT 20",
            (pattern, pattern)
        )
        return c.fetchall()

    def update_user(self, user_id, birth_date=None, birth_time=None,
                    birth_place=None, timezone=None, gender=None):
        """更新用户信息"""
        updates = []
        params = []
        if birth_date:
            updates.append("birth_date = ?")
            params.append(birth_date)
        if birth_time:
            updates.append("birth_time = ?")
            params.append(birth_time)
        if birth_place:
            updates.append("birth_place = ?")
            params.append(json.dumps(birth_place, ensure_ascii=False))
        if timezone:
            updates.append("timezone = ?")
            params.append(timezone)
        if gender:
            updates.append("gender = ?")
            params.append(gender)
        if not updates:
            return False
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        self.conn.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params
        )
        self.conn.commit()
        return True

    # ── 历史查询 ─────────────────────────────────────

    def get_life_state_history(self, user_id, limit=20):
        """获取用户状态变更历史"""
        c = self.conn.execute(
            "SELECT current_stage, energy_level, risk_level, capability_profile, "
            "behavior_patterns, created_at FROM life_state "
            "WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        return c.fetchall()

    def get_decision_history(self, user_id, limit=20):
        """获取用户决策历史"""
        c = self.conn.execute(
            "SELECT p0, p1, p2, p3, priority_reasoning, created_at FROM decisions "
            "WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        rows = c.fetchall()
        return [{
            "P0": json.loads(r["p0"]),
            "P1": json.loads(r["p1"]),
            "P2": json.loads(r["p2"]),
            "P3": json.loads(r["p3"]),
            "reasoning": json.loads(r["priority_reasoning"]),
            "time": r["created_at"],
        } for r in rows]

    def get_chart_history(self, user_id):
        """获取命盘版本历史"""
        c = self.conn.execute(
            "SELECT * FROM bazi_chart_history WHERE user_id = ? "
            "ORDER BY archived_at DESC",
            (user_id,)
        )
        return c.fetchall()

    # ── 报告管理 ─────────────────────────────────────

    def save_report(self, user_id, report_type, title, content,
                    period_start="", period_end=""):
        """保存报告"""
        report_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO reports (id, user_id, report_type, title, content, "
            "period_start, period_end) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (report_id, user_id, report_type, title,
             json.dumps(content, ensure_ascii=False) if isinstance(content, dict) else content,
             period_start, period_end)
        )
        self.conn.commit()
        return report_id

    def get_reports(self, user_id, report_type="", limit=10):
        """获取用户报告列表"""
        if report_type:
            c = self.conn.execute(
                "SELECT id, report_type, title, period_start, period_end, generated_at "
                "FROM reports WHERE user_id = ? AND report_type = ? "
                "ORDER BY generated_at DESC LIMIT ?",
                (user_id, report_type, limit)
            )
        else:
            c = self.conn.execute(
                "SELECT id, report_type, title, period_start, period_end, generated_at "
                "FROM reports WHERE user_id = ? "
                "ORDER BY generated_at DESC LIMIT ?",
                (user_id, limit)
            )
        return c.fetchall()

    def get_report(self, report_id):
        """获取单条报告"""
        c = self.conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        r = c.fetchone()
        if r and isinstance(r.get("content"), str):
            try:
                r["content"] = json.loads(r["content"])
            except Exception:
                pass
        return r

    def close(self):
        """关闭数据库连接"""
        self.conn.close()

    # ── 反馈系统 ─────────────────────────────────────

    def save_feedback(self, user_id, trace_id, score, category="decision",
                      comment="", decision_p0=None, decision_p1=None, state_snapshot=None):
        """保存用户反馈"""
        fb_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO feedback (id, user_id, trace_id, category, score, comment, "
            "decision_p0, decision_p1, state_snapshot) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (fb_id, user_id, trace_id, category, score, comment,
             json.dumps(decision_p0 or [], ensure_ascii=False),
             json.dumps(decision_p1 or [], ensure_ascii=False),
             json.dumps(state_snapshot or {}, ensure_ascii=False))
        )
        self.conn.commit()
        return fb_id

    def get_feedback_stats(self, user_id=""):
        """获取反馈统计"""
        if user_id:
            c = self.conn.execute(
                "SELECT AVG(score) as avg_score, COUNT(*) as total, "
                "SUM(CASE WHEN score >= 4 THEN 1 ELSE 0 END) as positive, "
                "SUM(CASE WHEN score <= 2 THEN 1 ELSE 0 END) as negative "
                "FROM feedback WHERE user_id = ?", (user_id,))
        else:
            c = self.conn.execute(
                "SELECT AVG(score) as avg_score, COUNT(*) as total, "
                "SUM(CASE WHEN score >= 4 THEN 1 ELSE 0 END) as positive, "
                "SUM(CASE WHEN score <= 2 THEN 1 ELSE 0 END) as negative "
                "FROM feedback")
        return c.fetchone()

    def get_recent_feedback(self, user_id="", limit=20):
        """获取最近的反馈"""
        if user_id:
            c = self.conn.execute(
                "SELECT * FROM feedback WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit))
        else:
            c = self.conn.execute(
                "SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?", (limit,))
        return c.fetchall()
