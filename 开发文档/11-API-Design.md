# Life Navigation System — API Design

> Version: 1.1 | Status: Current Implementation Interface

## 1. Purpose
将 LNS 所有内部引擎能力标准化为可调用的外部接口。支持 Web、Mobile、Codex、AI Agent、Third-party integration。

## 2. Core Principle
API 层不做计算。只做请求接收、数据路由、引擎调用、结果返回。

## 3. Base URL

当前本地实现：

```text
http://127.0.0.1:8080/api/v1
```

生产域名上线前再确定，不在本文档中提前绑定。

## 4. Authentication

当前实现未启用强认证。

规划字段：

```json
{
  "api_key": "",
  "user_id": "",
  "session_token": ""
}
```

## 5. Core API List

### 5.1 Create User Profile

```http
POST /api/v1/user
```

Request:

```json
{
  "birth_date": "YYYY-MM-DD",
  "birth_time": "HH:MM",
  "city": "北京",
  "district": "",
  "country": "CN",
  "latitude": null,
  "longitude": null,
  "timezone": "Asia/Shanghai",
  "gender": "male"
}
```

Response:

```json
{
  "success": true,
  "user_id": "uuid"
}
```

### 5.2 Analyze Full Life Navigation

```http
POST /api/v1/analyze
```

Flow: Calendar Engine -> BaZi Engine -> State Engine -> Knowledge Graph -> State Synthesizer -> Time Engine -> Decision Engine -> Prompt Engine

Request:

```json
{
  "birth_date": "YYYY-MM-DD",
  "birth_time": "HH:MM",
  "city": "北京",
  "country": "CN",
  "gender": "male",
  "age": 35,
  "user_id": "uuid"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "calendar_birth": {},
    "bazi_birth": {},
    "state": {},
    "knowledge_graph": {},
    "synthesized": {},
    "time": {},
    "decision": {},
    "prompt": ""
  }
}
```

### 5.3 Generate Report

```http
POST /api/v1/report
```

Types: `daily`, `monthly`, `yearly`, `decade`

Request:

```json
{
  "birth_date": "YYYY-MM-DD",
  "birth_time": "HH:MM",
  "city": "北京",
  "country": "CN",
  "gender": "male",
  "user_id": "uuid",
  "report_type": "decade",
  "target_date": "YYYY-MM-DD",
  "age": 35
}
```

Response:

```json
{
  "success": true,
  "data": {
    "title": "",
    "type": "decade",
    "overview": {}
  }
}
```

### 5.4 User Report List

```http
GET /api/v1/user/{user_id}/reports
GET /api/v1/user/{user_id}/reports?type=yearly
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "report_type": "yearly",
      "title": "",
      "period_start": "YYYY-MM-DD",
      "period_end": "YYYY-MM-DD",
      "generated_at": ""
    }
  ]
}
```

### 5.5 Report Detail

```http
GET /api/v1/report/{report_id}/view
```

Response:

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "report_type": "yearly",
    "title": "",
    "content": {}
  }
}
```

### 5.6 AI Chat Navigator

```http
POST /api/v1/chat
```

Request:

```json
{
  "user_id": "uuid",
  "message": "",
  "birth_date": "YYYY-MM-DD",
  "birth_time": "HH:MM",
  "city": "北京",
  "country": "CN",
  "gender": "male",
  "age": 35,
  "session_id": ""
}
```

Response:

```json
{
  "success": true,
  "mode": "llm",
  "response": "",
  "footer": "",
  "usage": {}
}
```

### 5.7 User Data Query

```http
GET /api/v1/users
GET /api/v1/user/{user_id}
GET /api/v1/user/{user_id}/history
GET /api/v1/user/{user_id}/chart
GET /api/v1/user/{user_id}/decisions
```

### 5.8 Time Navigation

```http
POST /api/v1/timeline
```

Response:

```json
{
  "success": true,
  "data": {
    "timeline": {},
    "state": {}
  }
}
```

### 5.9 Professional Mode

```http
POST /api/v1/professional
```

Response:

```json
{
  "success": true,
  "data": {
    "four_pillars": {},
    "day_master": "",
    "ten_gods": {},
    "five_elements": {},
    "hidden_stems": {},
    "luck_cycles": [],
    "deities": [],
    "current_state": {}
  }
}
```

### 5.10 What-if Simulator

```http
POST /api/v1/simulate
```

Request:

```json
{
  "birth_date": "YYYY-MM-DD",
  "birth_time": "HH:MM",
  "city": "北京",
  "country": "CN",
  "gender": "male",
  "scenarios": [
    {
      "label": "场景 A",
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "age": 35
    }
  ]
}
```

### 5.11 Feedback

```http
POST /api/v1/feedback
GET /api/v1/feedback/stats?user_id={user_id}
```

### 5.12 Health Check

```http
GET /health
```

## 6. Engine Routing Map

- `POST /api/v1/user` -> Database User CRUD
- `POST /api/v1/analyze` -> Full Pipeline
- `POST /api/v1/report` -> Full Pipeline + Report Engine
- `POST /api/v1/chat` -> Full Pipeline + Prompt Engine + optional LLM
- `POST /api/v1/timeline` -> Full Pipeline, returns time layer
- `POST /api/v1/professional` -> Full Pipeline, returns professional BaZi data
- `POST /api/v1/simulate` -> Scenario comparison pipeline
- `POST /api/v1/feedback` -> Feedback persistence

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

当前实现使用 `/api/v1`。

- `/api/v1` -> current implementation
- `/api/v2` -> future experimental

## 12. Performance Requirements
API响应 <200ms（非AI），Chat响应 <3s，Report生成 <10s。

## 13. Design Philosophy
把复杂的人生计算系统变成标准开发接口。

## 14. Extension (V2)
Webhook系统、多用户协作接口、企业API、决策流API（Workflow API）。

## 15. Deprecated Draft Routes

以下路径来自早期草案，当前程序未实现。后续开发不要继续引用。

| Deprecated route | Current route |
|---|---|
| `POST /user/create` | `POST /api/v1/user` |
| `POST /state/generate` | `POST /api/v1/analyze` |
| `GET /time/navigation` | `POST /api/v1/timeline` |
| `POST /decision/generate` | `POST /api/v1/analyze` |
| `POST /chat` | `POST /api/v1/chat` |
| `POST /report/generate` | `POST /api/v1/report` |
