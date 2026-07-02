# Life Navigation System — API Design

> Version: 1.0 | Status: Backend Interface Layer (Frozen)

## 1. Purpose
将 LNS 所有内部引擎能力标准化为可调用的外部接口。支持 Web、Mobile、Codex、AI Agent、Third-party integration。

## 2. Core Principle
API 层不做计算。只做请求接收、数据路由、引擎调用、结果返回。

## 3. Base URL
https://api.lns.system/v1

## 4. Authentication
{api_key, user_id, session_token}

## 5. Core API List

### 5.1 Create User Profile
POST /user/create
|Request:
|  {
|    "birth_data": {
|      "birth_date": "YYYY-MM-DD",
|      "birth_time": "HH:MM",
|      "birth_place": {
|        "city": "",
|        "district": "",
|        "country": ""
|      }
|    },
|    "target_time": {
|      "date": "YYYY-MM-DD",
|      "time": "HH:MM"
|    }
|  }
|  > Note: target_time 传入当前查询时间。Calendar Engine 和 BaZi Engine 并行处理出生时间和当前时间，生成静态命盘和流年/流日两路数据。
|Response: {user_id, status: created}|

### 5.2 Generate Life State
POST /state/generate
Flow: Calendar Engine → BaZi Engine → State Engine
Response: {current_state, capability_profile, risk_model, behavior_patterns}

### 5.3 Get Time Navigation
GET /time/navigation
Response: {T0, T1, T2, T3}

### 5.4 Get Decision Output
POST /decision/generate
Input: {user_id, state, time}
Response: {P0[], P1[], P2[], P3[], decision_logic}

### 5.5 AI Chat (Navigator)
POST /chat
|Request:
|  {
|    "user_id": "",
|    "message": "",
|    "target_time": {"date": "", "time": ""},
|    "context_mode": "standard | professional"
|  }
Internal: User Message → State Engine → Time Engine → Decision Engine → Prompt Engine → LLM → Output Engine
Response: {answer, structured_output:{state, time, decision}}

### 5.6 Generate Report
POST /report/generate
Types: daily, monthly, yearly, decade
Response: {report_type, content, actions[]}

## 6. Engine Routing Map
- /user/create → Calendar Engine
- /state/generate → State Engine
- /time/navigation → Time Engine
- /decision/generate → Decision Engine
- /chat → Full Pipeline
- /report/generate → Full Pipeline

## 7. Data Flow Architecture
Client → API Gateway → Authentication Layer → Routing Layer → Engine Layer → Response Formatter → Client

## 8. Error Handling
{error_code, message, stage}
Common Errors: INVALID_INPUT, CALC_ENGINE_FAIL, STATE_NOT_FOUND, TIME_PARSE_ERROR

## 9. Rate Limiting
Free User: 20 req/min, Pro User: 200 req/min, Enterprise: unlimited

## 10. Security Rules
禁止：伪造出生信息、修改历史命盘、直接调用内部 Engine。

## 11. Versioning Strategy
/v1 → stable, /v2 → experimental

## 12. Performance Requirements
API响应 <200ms（非AI），Chat响应 <3s，Report生成 <10s。

## 13. Design Philosophy
把复杂的人生计算系统变成标准开发接口。

## 14. Extension (V2)
Webhook系统、多用户协作接口、企业API、决策流API（Workflow API）。
