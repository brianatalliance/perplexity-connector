# Perplexity Sonar API — Full Endpoint Reference

**Base URL**: `https://api.perplexity.ai`  
**Auth**: `Authorization: Bearer <PERPLEXITY_API_KEY>`  
**Content-Type** (POST): `application/json`  
**Docs**: https://docs.perplexity.ai/

---

## Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/sonar` | Create synchronous chat completion |
| POST | `/v1/async/sonar` | Submit async chat completion |
| GET | `/v1/async/sonar` | List async chat completions |
| GET | `/v1/async/sonar/{id}` | Get specific async completion |

---

## 1. POST /v1/sonar — Create Chat Completion (Sync)

Creates a chat completion and returns the full response synchronously. Supports optional streaming via SSE.

### Request Headers

| Header | Value | Required |
|--------|-------|----------|
| `Authorization` | `Bearer <token>` | Yes |
| `Content-Type` | `application/json` | Yes |
| `Accept` | `text/event-stream` | Only for streaming |

### Request Body

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | string (enum) | Model to use. One of: `sonar`, `sonar-pro`, `sonar-deep-research`, `sonar-reasoning-pro` |
| `messages` | array | Conversation history. Each item has `role` (string) and `content` (string). Roles: `system`, `user`, `assistant` |

#### Optional Fields — Generation

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_tokens` | integer | — | Maximum output tokens (0–128000) |
| `stream` | boolean | `false` | Enable SSE streaming of response tokens |
| `stop` | string \| array | — | Stop sequence(s) that halt generation |
| `temperature` | number | `0.2` | Sampling temperature (0–2). Higher = more creative |
| `top_p` | number | `0.9` | Nucleus sampling probability (0–1) |
| `response_format` | object | — | Enforce structured JSON output (see Structured Output below) |
| `stream_mode` | string | — | Streaming verbosity: `full` (all tokens) or `concise` |
| `reasoning_effort` | string | — | Chain-of-thought depth: `minimal`, `low`, `medium`, `high` (sonar-reasoning-pro only) |
| `language_preference` | string | — | Response language preference (ISO 639-1, e.g., `en`, `es`, `fr`) |

#### Optional Fields — Search Control

| Field | Type | Description |
|-------|------|-------------|
| `search_mode` | string (enum) | Search corpus: `web` (default), `academic`, `sec` |
| `disable_search` | boolean | Set `true` to disable web search (pure LLM completion) |
| `enable_search_classifier` | boolean | Enable classifier to auto-decide when to search |
| `web_search_options` | object | Advanced web search configuration object |
| `return_images` | boolean | Include image results in the response |
| `return_related_questions` | boolean | Include related follow-up questions |
| `search_domain_filter` | string[] | Allowlist of domains to restrict search (e.g., `["arxiv.org", "nature.com"]`) |
| `search_language_filter` | string[] | ISO 639-1 language codes to restrict search results |
| `search_recency_filter` | string (enum) | Limit results by age: `hour`, `day`, `week`, `month`, `year` |
| `search_after_date_filter` | string | Only return results published after this date (MM/DD/YYYY) |
| `search_before_date_filter` | string | Only return results published before this date (MM/DD/YYYY) |
| `last_updated_before_filter` | string | Only return pages last updated before this date (MM/DD/YYYY) |
| `last_updated_after_filter` | string | Only return pages last updated after this date (MM/DD/YYYY) |
| `image_format_filter` | string[] | Filter image results by format (e.g., `["jpg", "png"]`) |
| `image_domain_filter` | string[] | Filter image results to specific domains |

#### Structured Output (response_format)

To get a JSON response conforming to a schema:

```json
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "schema": {
        "type": "object",
        "properties": {
          "answer": { "type": "string" },
          "confidence": { "type": "number" }
        },
        "required": ["answer"]
      }
    }
  }
}
```

### Request Example

```json
{
  "model": "sonar-pro",
  "messages": [
    { "role": "system", "content": "Be precise and concise." },
    { "role": "user", "content": "What is the capital of France?" }
  ],
  "temperature": 0.2,
  "search_recency_filter": "month",
  "return_related_questions": true
}
```

### Response Body

```json
{
  "id": "cmpl-abc123",
  "model": "sonar-pro",
  "created": 1711234567,
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris [1]."
      },
      "delta": { "role": "assistant", "content": "" }
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 12,
    "total_tokens": 27
  },
  "citations": [
    "https://en.wikipedia.org/wiki/Paris"
  ],
  "search_results": [
    {
      "title": "Paris — Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Paris",
      "date": "2024-01-15",
      "last_updated": "2024-03-20"
    }
  ],
  "images": [],
  "related_questions": [
    "What is the population of Paris?",
    "What is France known for?"
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique completion ID |
| `model` | string | Model used |
| `created` | integer | Unix timestamp |
| `choices` | array | Array of completion choices (usually 1) |
| `choices[].index` | integer | Choice index |
| `choices[].finish_reason` | string | Why generation stopped: `stop`, `length`, `content_filter` |
| `choices[].message.role` | string | Always `assistant` |
| `choices[].message.content` | string | The generated response text (may include `[n]` citation markers) |
| `usage.prompt_tokens` | integer | Tokens consumed by input |
| `usage.completion_tokens` | integer | Tokens in the output |
| `usage.total_tokens` | integer | Total tokens used |
| `citations` | string[] | List of source URLs referenced in the response |
| `search_results` | object[] | Detailed search result metadata (`title`, `url`, `date`, `last_updated`) |
| `images` | object[] | Image results when `return_images: true` |
| `related_questions` | string[] | Follow-up questions when `return_related_questions: true` |

### Streaming Response (SSE)

When `stream: true`, the response is a stream of Server-Sent Events:

```
data: {"id":"cmpl-abc","choices":[{"delta":{"role":"assistant","content":"Paris"},"index":0}]}
data: {"id":"cmpl-abc","choices":[{"delta":{"content":" is"},"index":0}]}
data: [DONE]
```

Each event is a JSON object with a `delta` containing the incremental content. The stream ends with `data: [DONE]`.

---

## 2. POST /v1/async/sonar — Create Async Chat Completion

Submits a chat completion job for asynchronous processing. Useful for long-running tasks like `sonar-deep-research`.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request` | object | Yes | Same body as POST /v1/sonar (all fields apply) |
| `idempotency_key` | string | No | Optional unique key to prevent duplicate submissions |

### Request Example

```json
{
  "request": {
    "model": "sonar-deep-research",
    "messages": [
      { "role": "user", "content": "Write a comprehensive report on quantum computing progress in 2024." }
    ]
  },
  "idempotency_key": "report-quantum-2024-v1"
}
```

### Response Body

```json
{
  "id": "async-xyz789",
  "model": "sonar-deep-research",
  "created_at": "2024-03-27T17:00:00Z",
  "status": "CREATED",
  "started_at": null,
  "completed_at": null,
  "failed_at": null,
  "error_message": null,
  "response": null
}
```

### Status Values

| Status | Description |
|--------|-------------|
| `CREATED` | Job queued, not yet started |
| `IN_PROGRESS` | Job is actively being processed |
| `COMPLETED` | Job finished successfully; `response` field contains results |
| `FAILED` | Job failed; see `error_message` |

---

## 3. GET /v1/async/sonar — List Async Chat Completions

Returns a paginated list of all previously submitted async requests.

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `next_token` | string | Pagination cursor from a previous response |

### Response Body

```json
{
  "requests": [
    {
      "id": "async-xyz789",
      "created_at": "2024-03-27T17:00:00Z",
      "model": "sonar-deep-research",
      "status": "COMPLETED",
      "started_at": "2024-03-27T17:00:05Z",
      "completed_at": "2024-03-27T17:02:30Z",
      "failed_at": null
    }
  ],
  "next_token": null
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `requests` | array | List of async request summaries |
| `requests[].id` | string | Unique async request ID |
| `requests[].created_at` | string | ISO 8601 creation timestamp |
| `requests[].model` | string | Model used |
| `requests[].status` | string | Current status (see Status Values above) |
| `requests[].started_at` | string \| null | When processing began |
| `requests[].completed_at` | string \| null | When processing completed |
| `requests[].failed_at` | string \| null | When processing failed |
| `next_token` | string \| null | Cursor for next page; `null` if no more results |

---

## 4. GET /v1/async/sonar/{id} — Get Async Chat Completion

Retrieves full details and results for a specific async request.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | The async request ID returned by POST /v1/async/sonar |

### Response Body

Same structure as POST /v1/async/sonar response, with the `response` field populated when `status == "COMPLETED"`:

```json
{
  "id": "async-xyz789",
  "model": "sonar-deep-research",
  "created_at": "2024-03-27T17:00:00Z",
  "status": "COMPLETED",
  "started_at": "2024-03-27T17:00:05Z",
  "completed_at": "2024-03-27T17:02:30Z",
  "failed_at": null,
  "error_message": null,
  "response": {
    "id": "cmpl-def456",
    "model": "sonar-deep-research",
    "created": 1711234650,
    "choices": [
      {
        "index": 0,
        "finish_reason": "stop",
        "message": {
          "role": "assistant",
          "content": "Quantum computing in 2024 saw major advances..."
        }
      }
    ],
    "usage": { "prompt_tokens": 20, "completion_tokens": 2500, "total_tokens": 2520 },
    "citations": ["https://...", "https://..."],
    "search_results": [],
    "images": [],
    "related_questions": []
  }
}
```

---

## Models Reference

| Model ID | Category | Best For | Notes |
|----------|----------|----------|-------|
| `sonar` | Search | Quick factual queries, summaries, comparisons | Lightweight; fastest response |
| `sonar-pro` | Search | Complex queries, follow-up conversations | More capable; better accuracy |
| `sonar-reasoning-pro` | Reasoning | Multi-step analysis, math, logic, coding | Chain-of-Thought; supports `reasoning_effort` |
| `sonar-deep-research` | Research | Exhaustive research, comprehensive reports | Runs extended search; best via async |

### Model Selection Guide

- **sonar** — Use for quick lookups, simple Q&A, current events. Cheapest and fastest.
- **sonar-pro** — Use when the user needs nuanced, multi-turn, or detailed answers. Good balance of speed and capability.
- **sonar-reasoning-pro** — Use for problems requiring logical steps: math, code debugging, multi-hop reasoning, strategy analysis. Set `reasoning_effort` to control CoT depth.
- **sonar-deep-research** — Use for reports, literature reviews, comprehensive research topics. Expect longer latency; submit via async for best UX.

---

## Error Codes

| HTTP Code | Error | Description | Resolution |
|-----------|-------|-------------|------------|
| 400 | Bad Request | Malformed request body, invalid field values | Check required fields and value ranges |
| 401 | Unauthorized | Missing or invalid API key | Verify `Authorization: Bearer <key>` header |
| 403 | Forbidden | Account lacks access to the requested feature/model | Upgrade plan or check model availability |
| 404 | Not Found | Endpoint or async request ID does not exist | Check path and async ID |
| 422 | Unprocessable Entity | Validation error (e.g., invalid model name, out-of-range value) | Review parameter constraints |
| 429 | Too Many Requests | Rate limit exceeded | Implement exponential back-off; see Rate Limits |
| 500 | Internal Server Error | Server-side failure | Retry after a brief delay |
| 503 | Service Unavailable | API temporarily unavailable | Retry with back-off |

### Error Response Format

```json
{
  "error": {
    "message": "Invalid model 'sonar-ultra'. Valid models are: sonar, sonar-pro, sonar-deep-research, sonar-reasoning-pro",
    "type": "invalid_request_error",
    "code": "invalid_model"
  }
}
```

---

## Rate Limits

Perplexity enforces rate limits per API key. Specific limits depend on your subscription tier. General guidance:

- Implement **exponential back-off** on 429 responses (start at 1s, double up to 60s)
- `sonar-deep-research` jobs can take minutes — use async endpoint to avoid client timeouts
- Concurrent streaming connections may be limited per account

---

## Search Mode Details

| Mode | Corpus | Use Case |
|------|--------|----------|
| `web` | General web | Default — broadest coverage |
| `academic` | Scholarly papers | Research, citations, peer-reviewed sources |
| `sec` | SEC EDGAR filings | Financial filings, 10-K, 10-Q, 8-K documents |

---

## Date Filter Format

All date filters use **MM/DD/YYYY** format:

```json
{
  "search_after_date_filter": "01/01/2024",
  "search_before_date_filter": "12/31/2024"
}
```

---

## Additional Resources

- **API Key Management**: https://www.perplexity.ai/settings/api
- **Official Documentation**: https://docs.perplexity.ai/
- **Model Pricing**: https://docs.perplexity.ai/guides/pricing
- **API Changelog**: https://docs.perplexity.ai/changelog
