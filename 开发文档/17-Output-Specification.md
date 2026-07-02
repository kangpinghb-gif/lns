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

All AI responses SHOULD follow a five-part structure. Section 0 is optional when BaZi source data is missing, but should be enabled by default when chart data exists:

0. **BaZi Anchor / 命理锚点** — One short sentence that states the BaZi basis using authentic chart terms
1. **Current State / 当前状态** — Where the user is now, written mainly in modern product language
2. **Time Impact / 时间影响** — How the situation affects their timeline
3. **Recommendation (P0–P3) / 行动建议** — Prioritized actions, from highest to lowest urgency
4. **Why / 原因** — Rationale behind the recommendation

No free-form deviation is permitted.

### 4.1 BaZi Anchor Rules

The BaZi Anchor exists to make the source of the interpretation visible to the user before the system switches to modern explanation.

Example:

```
【你的命盘结构】
日主丁火，伤官格，木火偏旺。
```

Rules:

- Use only upstream structured BaZi data or Knowledge Graph mappings.
- Keep it to one sentence by default.
- Do not make deterministic fortune claims.
- Do not include direct action recommendations in Section 0.
- If BaZi data is unavailable, omit Section 0 and continue with Section 1.

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
