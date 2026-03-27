#!/usr/bin/env python3
"""
Perplexity Sonar API Helper — for use within Perplexity Computer skill.

Usage:
    python3 perplexity_api.py <action> [options]

Environment:
    PERPLEXITY_API_KEY — Required. Your Perplexity API key.

Actions:
    chat                Quick factual query using sonar (lightweight search)
    chat-pro            Complex query using sonar-pro (advanced search)
    deep-research       Exhaustive research using sonar-deep-research
    reasoning           Multi-step analysis using sonar-reasoning-pro
    async-create        Submit an async chat completion request
    async-list          List all async chat completion requests
    async-get           Get an async chat completion by --id

Options:
    --model MODEL           Override the default model for the action
    --message TEXT          The user query / prompt (positional arg also accepted)
    --system TEXT           System prompt to prepend
    --temperature N         Sampling temperature (0-2, default 0.2)
    --top-p N               Nucleus sampling (0-1)
    --max-tokens N          Max output tokens (0-128000)
    --search-mode MODE      Search corpus: web, academic, sec
    --domain-filter DOMAINS Comma-separated domain allowlist (e.g. arxiv.org,nature.com)
    --recency-filter RANGE  Restrict search recency: hour, day, week, month, year
    --return-images         Include image results in response
    --return-related        Include related questions in response
    --disable-search        Disable web search (pure LLM mode)
    --json-schema FILE      Path to JSON schema file for structured output
    --stream                Enable streaming output (SSE)
    --output FORMAT         Output format: text (default) or json
    --quiet                 Suppress progress output, print only results
    --id ID                 Async request ID (for async-get)

Examples:
    # Quick factual search
    python3 perplexity_api.py chat "What is the current price of gold?"

    # Complex research with sonar-pro
    python3 perplexity_api.py chat-pro "Compare RISC-V and ARM architectures"

    # Deep research with citations
    python3 perplexity_api.py deep-research "Impact of mRNA vaccines on cancer treatment"

    # Reasoning with CoT
    python3 perplexity_api.py reasoning "Solve: if 3x + 7 = 22, what is x?"

    # Academic search only
    python3 perplexity_api.py chat-pro --search-mode academic "LLM alignment techniques 2024"

    # Domain-filtered search
    python3 perplexity_api.py chat --domain-filter "gov,cdc.gov" "COVID vaccine recommendations"

    # Recency-filtered search
    python3 perplexity_api.py chat --recency-filter week "latest AI research news"

    # Structured JSON output
    python3 perplexity_api.py chat --json-schema schema.json "List top 5 programming languages"

    # Stream output
    python3 perplexity_api.py chat --stream "Explain quantum entanglement"

    # Submit async job and retrieve later
    python3 perplexity_api.py async-create "Write a comprehensive report on fusion energy"
    python3 perplexity_api.py async-list
    python3 perplexity_api.py async-get --id <request-id>

    # Raw JSON output (full API response)
    python3 perplexity_api.py chat --output json "What is the speed of light?"
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "https://api.perplexity.ai"
API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")

# Default models per action
ACTION_MODELS = {
    "chat": "sonar",
    "chat-pro": "sonar-pro",
    "deep-research": "sonar-deep-research",
    "reasoning": "sonar-reasoning-pro",
    "async-create": "sonar-pro",
}

VALID_MODELS = {"sonar", "sonar-pro", "sonar-deep-research", "sonar-reasoning-pro"}


# ─── HTTP helpers ────────────────────────────────────────────────────────────

def check_api_key():
    if not API_KEY:
        print(
            "ERROR: PERPLEXITY_API_KEY environment variable is not set.\n"
            "       Get your API key at https://www.perplexity.ai/settings/api",
            file=sys.stderr,
        )
        sys.exit(1)


def api_request(method, path, body=None, params=None, quiet=False):
    """Make an authenticated request to the Perplexity API."""
    check_api_key()

    url = BASE_URL + path
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url += ("&" if "?" in url else "?") + qs

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} — {e.reason}", file=sys.stderr)
        try:
            err_json = json.loads(err_body)
            print(json.dumps(err_json, indent=2), file=sys.stderr)
        except Exception:
            print(err_body, file=sys.stderr)
        sys.exit(1)


def api_stream(path, body, quiet=False):
    """Stream a chat completion via SSE and print chunks as they arrive."""
    check_api_key()

    url = BASE_URL + path
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            full_content = []
            for raw_line in resp:
                line = raw_line.decode("utf-8").rstrip("\n\r")
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        print(content, end="", flush=True)
                        full_content.append(content)
                except json.JSONDecodeError:
                    pass
            print()  # newline after stream ends
            return "".join(full_content)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"\nHTTP {e.code} — {e.reason}", file=sys.stderr)
        print(err_body, file=sys.stderr)
        sys.exit(1)


# ─── Output helpers ──────────────────────────────────────────────────────────

def print_text_response(resp):
    """Pretty-print a chat completion in human-readable text mode."""
    choices = resp.get("choices", [])
    if not choices:
        print("(no response content)")
        return

    message = choices[0].get("message", {})
    content = message.get("content", "")
    print(content)

    # Print citations if present
    citations = resp.get("citations", [])
    if citations:
        print("\nCitations:")
        for i, url in enumerate(citations, 1):
            print(f"  [{i}] {url}")

    # Print related questions if present
    related = resp.get("related_questions", [])
    if related:
        print("\nRelated Questions:")
        for q in related:
            print(f"  - {q}")

    # Print images if present
    images = resp.get("images", [])
    if images:
        print("\nImages:")
        for img in images:
            src = img.get("url", img) if isinstance(img, dict) else img
            print(f"  - {src}")

    # Print usage summary
    usage = resp.get("usage", {})
    if usage and not os.environ.get("PERPLEXITY_HIDE_USAGE"):
        tokens_in = usage.get("prompt_tokens", "?")
        tokens_out = usage.get("completion_tokens", "?")
        print(f"\n[usage: {tokens_in} prompt tokens, {tokens_out} completion tokens]",
              file=sys.stderr)


def emit_response(resp, output_fmt, stream_used=False):
    """Emit the final response in the requested format."""
    if output_fmt == "json":
        print(json.dumps(resp, indent=2, default=str))
    else:
        if not stream_used:
            print_text_response(resp)


# ─── Request builder ─────────────────────────────────────────────────────────

def build_body(args, model):
    """Construct the API request body from parsed args."""
    messages = []

    if args.system:
        messages.append({"role": "system", "content": args.system})

    user_msg = args.message if args.message else ""
    if not user_msg:
        print("ERROR: A message/query is required (use --message or a positional argument).",
              file=sys.stderr)
        sys.exit(1)
    messages.append({"role": "user", "content": user_msg})

    body = {
        "model": model,
        "messages": messages,
    }

    # Optional numeric params
    if args.temperature is not None:
        body["temperature"] = args.temperature
    if args.top_p is not None:
        body["top_p"] = args.top_p
    if args.max_tokens is not None:
        body["max_tokens"] = args.max_tokens

    # Search options
    if args.search_mode:
        body["search_mode"] = args.search_mode
    if args.recency_filter:
        body["search_recency_filter"] = args.recency_filter
    if args.domain_filter:
        domains = [d.strip() for d in args.domain_filter.split(",") if d.strip()]
        body["search_domain_filter"] = domains
    if args.return_images:
        body["return_images"] = True
    if args.return_related:
        body["return_related_questions"] = True
    if args.disable_search:
        body["disable_search"] = True

    # Structured output via JSON schema file
    if args.json_schema:
        with open(args.json_schema) as f:
            schema = json.load(f)
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {"schema": schema},
        }

    # Streaming
    if args.stream:
        body["stream"] = True

    return body


# ─── Actions ─────────────────────────────────────────────────────────────────

def do_chat(action, args):
    """Execute a synchronous chat completion."""
    model = args.model or ACTION_MODELS.get(action, "sonar")
    if model not in VALID_MODELS:
        print(f"ERROR: Unknown model '{model}'. Valid models: {', '.join(sorted(VALID_MODELS))}",
              file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"  Model: {model}", file=sys.stderr)

    body = build_body(args, model)

    if args.stream:
        api_stream("/v1/sonar", body, quiet=args.quiet)
        return

    resp = api_request("POST", "/v1/sonar", body=body, quiet=args.quiet)
    emit_response(resp, args.output)


def do_async_create(args):
    """Submit an async chat completion."""
    model = args.model or ACTION_MODELS.get("async-create", "sonar-pro")
    if not args.quiet:
        print(f"  Submitting async job with model: {model}", file=sys.stderr)

    inner_body = build_body(args, model)
    body = {"request": inner_body}

    resp = api_request("POST", "/v1/async/sonar", body=body, quiet=args.quiet)

    if args.output == "json":
        print(json.dumps(resp, indent=2, default=str))
    else:
        req_id = resp.get("id", "unknown")
        status = resp.get("status", "unknown")
        print(f"Async request submitted.")
        print(f"  ID:     {req_id}")
        print(f"  Status: {status}")
        print(f"\nRetrieve result with:")
        print(f"  python3 perplexity_api.py async-get --id {req_id}")


def do_async_list(args):
    """List all async chat completions."""
    if not args.quiet:
        print("  Fetching async request list...", file=sys.stderr)

    resp = api_request("GET", "/v1/async/sonar", quiet=args.quiet)

    if args.output == "json":
        print(json.dumps(resp, indent=2, default=str))
    else:
        requests = resp.get("requests", [])
        if not requests:
            print("(no async requests found)")
            return
        print(f"{'ID':<40} {'Status':<15} {'Model':<25} {'Created At'}")
        print("-" * 100)
        for r in requests:
            print(
                f"{r.get('id', ''):<40} "
                f"{r.get('status', ''):<15} "
                f"{r.get('model', ''):<25} "
                f"{r.get('created_at', '')}"
            )
        next_token = resp.get("next_token")
        if next_token:
            print(f"\n(more results available — next_token: {next_token})")


def do_async_get(args):
    """Get a specific async chat completion by ID."""
    if not args.entity_id:
        print("ERROR: --id is required for async-get.", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"  Fetching async request {args.entity_id}...", file=sys.stderr)

    resp = api_request("GET", f"/v1/async/sonar/{args.entity_id}", quiet=args.quiet)

    if args.output == "json":
        print(json.dumps(resp, indent=2, default=str))
    else:
        status = resp.get("status", "unknown")
        req_id = resp.get("id", "unknown")
        print(f"ID:     {req_id}")
        print(f"Status: {status}")

        if status == "COMPLETED":
            inner = resp.get("response")
            if inner:
                print("\n--- Response ---")
                print_text_response(inner)
        elif status == "FAILED":
            print(f"Error:  {resp.get('error_message', 'unknown error')}")
        else:
            started = resp.get("started_at", "not started")
            print(f"Started: {started}")
            print("(job still in progress — try again later)")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Perplexity Sonar API CLI helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("action", help="API action to perform")
    parser.add_argument("message", nargs="?", default=None, help="User query (positional)")

    # Message / prompt options
    parser.add_argument("--message", dest="message_flag", default=None,
                        help="User query (flag form — overrides positional)")
    parser.add_argument("--system", default=None, help="System prompt")

    # Model / sampling
    parser.add_argument("--model", default=None, help="Override default model")
    parser.add_argument("--temperature", type=float, default=None, help="Sampling temperature (0-2)")
    parser.add_argument("--top-p", dest="top_p", type=float, default=None,
                        help="Nucleus sampling probability (0-1)")
    parser.add_argument("--max-tokens", dest="max_tokens", type=int, default=None,
                        help="Maximum output tokens (0-128000)")

    # Search controls
    parser.add_argument("--search-mode", dest="search_mode", choices=["web", "academic", "sec"],
                        default=None, help="Search corpus")
    parser.add_argument("--domain-filter", dest="domain_filter", default=None,
                        help="Comma-separated domain allowlist")
    parser.add_argument("--recency-filter", dest="recency_filter",
                        choices=["hour", "day", "week", "month", "year"],
                        default=None, help="Restrict search recency")
    parser.add_argument("--return-images", dest="return_images", action="store_true",
                        help="Include image results")
    parser.add_argument("--return-related", dest="return_related", action="store_true",
                        help="Include related questions")
    parser.add_argument("--disable-search", dest="disable_search", action="store_true",
                        help="Disable web search (pure LLM)")

    # Structured output
    parser.add_argument("--json-schema", dest="json_schema", default=None,
                        help="Path to JSON schema file for structured output")

    # Output / streaming
    parser.add_argument("--stream", action="store_true", help="Enable streaming output")
    parser.add_argument("--output", default="text", choices=["text", "json"],
                        help="Output format: text (default) or json")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")

    # Async
    parser.add_argument("--id", dest="entity_id", default=None,
                        help="Async request ID (for async-get)")

    args = parser.parse_args()

    # Merge --message flag into positional if both provided (flag wins)
    if args.message_flag:
        args.message = args.message_flag

    act = args.action

    if act in ("chat", "chat-pro", "deep-research", "reasoning"):
        do_chat(act, args)
    elif act == "async-create":
        do_async_create(args)
    elif act == "async-list":
        do_async_list(args)
    elif act == "async-get":
        do_async_get(args)
    else:
        print(f"ERROR: Unknown action '{act}'. Run with -h for help.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
