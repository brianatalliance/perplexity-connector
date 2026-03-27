---
name: perplexity-connector
description: >-
  Custom connector for the Perplexity AI Sonar API. Use when the user wants to
  query Perplexity's web-grounded AI, run deep research, perform reasoning with
  Chain of Thought, submit async chat completions, or retrieve citations and
  search results. Handles authentication via Bearer token, synchronous and
  async completions, streaming SSE, structured JSON output, and all search
  filters. Includes a CLI helper script and full endpoint reference. Trigger
  phrases: Perplexity, Sonar, sonar-pro, sonar-deep-research, sonar-reasoning,
  web-grounded AI, citations, deep research, search API, async completion,
  academic search, SEC search, Perplexity API.
metadata:
  author: your-name
  version: '1.0'
  api_version: v1
  base_url: https://api.perplexity.ai
---

# Perplexity Sonar API Connector

## When to Use This Skill

Use this skill whenever the user asks you to:

- Query Perplexity AI with web-grounded responses and citations
- Run deep research or comprehensive report generation
- Perform multi-step reasoning or Chain-of-Thought analysis
- Search academic papers or SEC filings via Perplexity
- Submit long-running research jobs asynchronously
- Filter search results by domain, recency, date range, or language
- Return structured JSON output from a Perplexity query
- Stream Perplexity responses token-by-token
- Build automations, scripts, or integrations against the Perplexity API

## Prerequisites

**API key required.** Generate one at https://www.perplexity.ai/settings/api

The CLI helper expects the key as an environment variable:

```bash
export PERPLEXITY_API_KEY="pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

The script has an empty default — you **must** set this variable or calls will fail with a clear error message.

## Quick Start

### Using the CLI Helper Script

```bash
# Simple search query
python3 skills/perplexity-connector/scripts/perplexity_api.py chat "What is the current Fed funds rate?"

# Advanced research
python3 skills/perplexity-connector/scripts/perplexity_api.py chat-pro "Explain the differences between transformer and Mamba architectures"

# Deep research (can take 1-3 minutes)
python3 skills/perplexity-connector/scripts/perplexity_api.py deep-research "History and current state of nuclear fusion energy"

# Reasoning with Chain of Thought
python3 skills/perplexity-connector/scripts/perplexity_api.py reasoning "A train travels 120 miles in 2 hours. How long to travel 450 miles at the same speed?"
```

### Direct API Call (curl)

```bash
curl -s https://api.perplexity.ai/v1/sonar \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-pro",
    "messages": [{"role": "user", "content": "What is the latest news on AI regulation?"}]
  }' | python3 -m json.tool
```

### Direct API Call (Python)

```python
import json
import urllib.request

API_KEY = "pplx-your-key-here"
BASE_URL = "https://api.perplexity.ai"

body = {
    "model": "sonar-pro",
    "messages": [{"role": "user", "content": "Summarize recent advances in CRISPR therapy"}],
    "return_related_questions": True,
}

req = urllib.request.Request(
    BASE_URL + "/v1/sonar",
    data=json.dumps(body).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())

# Print answer
print(data["choices"][0]["message"]["content"])

# Print citations
for i, url in enumerate(data.get("citations", []), 1):
    print(f"[{i}] {url}")
```

## Authentication

- **Method**: Bearer token in HTTP header
- **Header**: `Authorization: Bearer <your-api-key>`
- **Base URL**: `https://api.perplexity.ai`
- **API version**: v1

Get your API key at https://www.perplexity.ai/settings/api  
API key format: `pplx-` followed by a hex string

Set the environment variable before running any CLI command:
```bash
export PERPLEXITY_API_KEY="pplx-xxxxxxxxxxxx"
```

## Model Selection Guide

| Model | Best For | Speed |
|-------|----------|-------|
| `sonar` | Quick lookups, current events, simple Q&A | Fastest |
| `sonar-pro` | Complex queries, follow-ups, nuanced analysis | Fast |
| `sonar-reasoning-pro` | Math, logic, code, multi-step problems | Medium |
| `sonar-deep-research` | Exhaustive research, comprehensive reports | Slow (1-3 min) |

**Decision rules:**
- Default to `sonar` for quick factual questions
- Use `sonar-pro` for detailed explanations or multi-turn conversations
- Use `sonar-reasoning-pro` when the problem requires step-by-step reasoning
- Use `sonar-deep-research` when the user asks for a comprehensive report — submit via `async-create` for reliability

## CLI Reference

### Actions

| Action | Default Model | Description |
|--------|---------------|-------------|
| `chat` | `sonar` | Lightweight search query |
| `chat-pro` | `sonar-pro` | Advanced search query |
| `deep-research` | `sonar-deep-research` | Exhaustive research |
| `reasoning` | `sonar-reasoning-pro` | Chain-of-Thought reasoning |
| `async-create` | `sonar-pro` | Submit async job |
| `async-list` | — | List all async jobs |
| `async-get` | — | Get async job by `--id` |

### Common Flags

| Flag | Description |
|------|-------------|
| `--model MODEL` | Override the default model |
| `--message TEXT` | User query (also accepted as positional argument) |
| `--system TEXT` | System prompt to prepend |
| `--temperature N` | Sampling temperature (0–2) |
| `--top-p N` | Nucleus sampling probability (0–1) |
| `--max-tokens N` | Max output tokens (0–128000) |
| `--search-mode MODE` | `web`, `academic`, or `sec` |
| `--domain-filter DOMAINS` | Comma-separated domain allowlist |
| `--recency-filter RANGE` | `hour`, `day`, `week`, `month`, `year` |
| `--return-images` | Include image results |
| `--return-related` | Include related questions |
| `--disable-search` | Disable web search (pure LLM) |
| `--json-schema FILE` | Path to JSON schema for structured output |
| `--stream` | Stream response tokens via SSE |
| `--output FORMAT` | `text` (default) or `json` |
| `--quiet` | Suppress progress messages |
| `--id ID` | Async request ID (for `async-get`) |

### Usage Examples

```bash
# Quick question
python3 scripts/perplexity_api.py chat "Who won the 2024 Nobel Prize in Physics?"

# Academic search
python3 scripts/perplexity_api.py chat-pro --search-mode academic "mRNA vaccine efficacy meta-analysis"

# Domain-restricted search
python3 scripts/perplexity_api.py chat --domain-filter "cdc.gov,who.int" "COVID-19 vaccine recommendations 2025"

# Recent news only
python3 scripts/perplexity_api.py chat --recency-filter week "latest AI model releases"

# Date-range filtered (set manually via --output json and review search_results)
python3 scripts/perplexity_api.py chat-pro --output json "electric vehicle sales 2023"

# Structured JSON output
python3 scripts/perplexity_api.py chat --json-schema schema.json "List the top 5 cloud providers by market share"

# Streaming
python3 scripts/perplexity_api.py chat --stream "Write a haiku about machine learning"

# Full JSON response (includes citations, usage, search_results)
python3 scripts/perplexity_api.py chat --output json "What is the Higgs boson?"

# Reasoning with system prompt
python3 scripts/perplexity_api.py reasoning \
  --system "You are a financial analyst. Show your work." \
  "Calculate the compound annual growth rate from $10,000 to $18,500 over 6 years"

# Submit deep research as async job
python3 scripts/perplexity_api.py async-create \
  --model sonar-deep-research \
  "Comprehensive analysis of carbon capture technologies and their commercial viability"

# Check job status
python3 scripts/perplexity_api.py async-list

# Retrieve completed result
python3 scripts/perplexity_api.py async-get --id async-xyz789
```

## Common Patterns

### Research Workflow with Async

For `sonar-deep-research` jobs, always use async to avoid timeouts:

```bash
# Step 1: Submit
ID=$(python3 scripts/perplexity_api.py async-create \
  --model sonar-deep-research \
  --output json \
  "State of autonomous vehicle regulation in 2025" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Job ID: $ID"

# Step 2: Poll until complete (every 30 seconds)
python3 scripts/perplexity_api.py async-get --id "$ID"
```

### Citation-Grounded Summaries

```python
import json, subprocess

result = subprocess.run(
    ["python3", "scripts/perplexity_api.py", "chat-pro",
     "--output", "json",
     "Summarize the current state of quantum error correction"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
content = data["choices"][0]["message"]["content"]
citations = data.get("citations", [])

print(content)
print("\nSources:")
for i, url in enumerate(citations, 1):
    print(f"  [{i}] {url}")
```

### Structured Output for Data Extraction

Create a schema file (`schema.json`):

```json
{
  "type": "object",
  "properties": {
    "companies": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "market_share_pct": { "type": "number" },
          "headquarters": { "type": "string" }
        },
        "required": ["name", "market_share_pct"]
      }
    }
  },
  "required": ["companies"]
}
```

Then run:

```bash
python3 scripts/perplexity_api.py chat \
  --json-schema schema.json \
  --output json \
  "Top 5 cloud providers by market share"
```

### Academic Research Pipeline

```bash
# Find papers on a topic
python3 scripts/perplexity_api.py chat-pro \
  --search-mode academic \
  --return-related \
  --output json \
  "Transformer attention mechanism improvements 2024" > results.json

# Extract citations
python3 -c "import json; [print(u) for u in json.load(open('results.json')).get('citations', [])]"
```

### SEC Filing Analysis

```bash
python3 scripts/perplexity_api.py chat-pro \
  --search-mode sec \
  "Apple Inc 2024 annual report revenue breakdown and risk factors"
```

## Error Handling

| HTTP Code | Meaning | Resolution |
|-----------|---------|------------|
| 400 | Bad request — invalid body or field values | Check required fields; validate JSON |
| 401 | Invalid or missing API key | Verify `PERPLEXITY_API_KEY` is set and correct |
| 403 | Insufficient permissions | Check model access on your plan |
| 404 | Endpoint or async ID not found | Verify path and async request ID |
| 422 | Validation error — invalid parameter values | Check value ranges and enum options |
| 429 | Rate limit exceeded | Back off with exponential delay |
| 500 | Server error | Retry after a brief delay |
| 503 | Service unavailable | Retry with exponential back-off |

The CLI helper prints HTTP error code, reason, and response body to stderr then exits with code 1.

For programmatic retry logic:

```python
import time

def call_with_retry(fn, max_retries=3):
    for attempt in range(max_retries):
        try:
            return fn()
        except SystemExit:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            time.sleep(wait)
```

## Rate Limits

- Rate limits vary by subscription tier
- Implement exponential back-off on 429 responses (1s → 2s → 4s → …, cap at 60s)
- `sonar-deep-research` is computationally intensive — use async endpoint and poll rather than holding an HTTP connection
- For bulk workloads, add a small delay between requests (e.g., 200ms) to stay within limits

## API Reference

Load `references/api-endpoints.md` for the complete endpoint reference covering:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/sonar` | POST | Synchronous chat completion |
| `/v1/async/sonar` | POST | Submit async chat completion |
| `/v1/async/sonar` | GET | List async completions |
| `/v1/async/sonar/{id}` | GET | Get async completion by ID |

The reference includes all request/response fields, structured output schema format, streaming SSE format, model descriptions, date filter syntax, and error code details.
