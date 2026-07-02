# Life Navigation System — Output Specification

> Version: 1.0 | Status: Frozen

## 1. Purpose

Define a unified output schema for all system outputs. Every Engine, API, AI, and H5 page MUST conform to this standard. No one is permitted to construct arbitrary JSON structures.

## 2. Output Hierarchy

- **L1** — Page Output (Home, Life Overview, Time Navigation, Decision Center)
- **L2** — API Output (REST API)
- **L3** — AI Output (Chat)
- **L4** — Report Output (PDF / HTML / Markdown)

## 3. Page Schemas

### 3.1 Home Page Schema

```
{
  "current_stage": "<string>",
  "energy_state": "<object>",
  "risk_signal": ["<string>"],
  "today_action": ["<object>"],
  "timeline": "<object>",
  "decision_summary": "<object>"
}
```

### 3.2 Life Overview Schema

```
{
  "identity": "<string>",
  "life_stage": "<string>",
  "capabilities": ["<string>"],
  "strengths": ["<string>"],
  "attention": ["<string>"],
  "growth_path": ["<object>"]
}
```

### 3.3 Time Navigation Schema

```
{
  "T0": "<object>",
  "T1": "<object>",
  "T2": "<object>",
  "T3": "<object>"
}
```

## 4. AI Response — Unified Structure

All AI responses MUST follow a fixed four-part structure:

1. **Current State** — Where the user is now
2. **Time Impact** — How the situation affects their timeline
3. **Recommendation (P0–P3)** — Prioritized actions, from highest to lowest urgency
4. **Why** — Rationale behind the recommendation

No free-form deviation is permitted.

## 5. API — Unified Return Format

```
{
  "success": <bool>,
  "code": <int>,
  "message": "<string>",
  "data": <any>,
  "trace_id": "<string>",
  "timestamp": "<string>"
}
```

## 6. HTTP Status Codes

| Code | Meaning       |
|------|----------------|
| 400  | Bad Request    |
| 401  | Unauthorized   |
| 403  | Forbidden      |
| 404  | Not Found      |
| 422  | Validation Error |
| 500  | Internal Server Error |

## 7. Output Principles

- Every statement has a source.
- Every statement is traceable.
