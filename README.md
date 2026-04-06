# Perplexity Sonar API Connector

A custom [Perplexity Computer](https://www.perplexity.ai/computer/skills) skill that provides a CLI helper and full API reference for the Perplexity Sonar API — synchronous and async chat completions, streaming, structured output, and all search filters.

## Features

| Capability | Details |
|------------|---------|
| **Models** | `sonar`, `sonar-pro`, `sonar-reasoning-pro`, `sonar-deep-research` |
| **Sync Completions** | Full chat completion with citations, images, related questions |
| **Async Completions** | Submit long-running jobs (deep research), poll for results |
| **Streaming** | Server-Sent Events (SSE) for token-by-token output |
| **Structured Output** | JSON Schema-based response formatting |
| **Search Filters** | Domain, recency, date range, language, academic, SEC filings |
| **Output Formats** | Pretty text (with citations) or raw JSON |

## Project Structure

```
perplexity-connector/
├── SKILL.md                    # Skill definition (agentskills.io format)
├── scripts/
│   └── perplexity_api.py       # CLI helper (484 lines)
└── references/
    └── api-endpoints.md        # Full API endpoint reference
```

## Quick Start

### Prerequisites

Generate an API key at [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api):

```bash
export PERPLEXITY_API_KEY="pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### CLI Usage

```bash
# Quick factual search
python3 scripts/perplexity_api.py chat "What is the current price of gold?"

# Advanced research with sonar-pro
python3 scripts/perplexity_api.py chat-pro "Compare RISC-V and ARM architectures"

# Deep research (1-3 minutes)
python3 scripts/perplexity_api.py deep-research "Impact of mRNA vaccines on cancer treatment"

# Chain-of-Thought reasoning
python3 scripts/perplexity_api.py reasoning "If 3x + 7 = 22, what is x?"

# Academic search
python3 scripts/perplexity_api.py chat-pro --search-mode academic "LLM alignment techniques"

# Domain-filtered search
python3 scripts/perplexity_api.py chat --domain-filter "gov,cdc.gov" "COVID vaccine recommendations"

# Structured JSON output
python3 scripts/perplexity_api.py chat --json-schema schema.json "Top 5 cloud providers"

# Streaming
python3 scripts/perplexity_api.py chat --stream "Explain quantum entanglement"

# Async deep research
python3 scripts/perplexity_api.py async-create "Comprehensive fusion energy report"
python3 scripts/perplexity_api.py async-list
python3 scripts/perplexity_api.py async-get --id <request-id>
```

### CLI Actions

| Action | Default Model | Description |
|--------|---------------|-------------|
| `chat` | `sonar` | Lightweight search query |
| `chat-pro` | `sonar-pro` | Advanced search query |
| `deep-research` | `sonar-deep-research` | Exhaustive research |
| `reasoning` | `sonar-reasoning-pro` | Chain-of-Thought reasoning |
| `async-create` | `sonar-pro` | Submit async job |
| `async-list` | — | List all async jobs |
| `async-get` | — | Get async job by `--id` |

### CLI Flags

| Flag | Description |
|------|-------------|
| `--model MODEL` | Override the default model |
| `--message TEXT` | User query (also accepted as positional argument) |
| `--system TEXT` | System prompt |
| `--temperature N` | Sampling temperature (0–2) |
| `--top-p N` | Nucleus sampling (0–1) |
| `--max-tokens N` | Max output tokens (0–128,000) |
| `--search-mode MODE` | `web`, `academic`, or `sec` |
| `--domain-filter DOMAINS` | Comma-separated domain allowlist |
| `--recency-filter RANGE` | `hour`, `day`, `week`, `month`, `year` |
| `--return-images` | Include image results |
| `--return-related` | Include related questions |
| `--disable-search` | Disable web search (pure LLM) |
| `--json-schema FILE` | JSON schema file for structured output |
| `--stream` | Enable streaming |
| `--output FORMAT` | `text` (default) or `json` |
| `--quiet` | Suppress progress messages |
| `--id ID` | Async request ID (for `async-get`) |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3 (stdlib only — no dependencies) |
| HTTP | `urllib.request` |
| Auth | Bearer token (`Authorization` header) |
| Streaming | Server-Sent Events (SSE) parsing |
| Skill Format | [agentskills.io](https://agentskills.io) specification |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/sonar` | Synchronous chat completion |
| POST | `/v1/async/sonar` | Submit async chat completion |
| GET | `/v1/async/sonar` | List async completions |
| GET | `/v1/async/sonar/{id}` | Get async completion by ID |

See [`references/api-endpoints.md`](references/api-endpoints.md) for the complete endpoint reference.

## Related Projects

- [perplexity-windows-xpc](https://github.com/brianatalliance/perplexity-windows-xpc) — Perplexity AI for Windows — PowerShell, system tray, Office integration
- [perplexity-xpc](https://github.com/brianatalliance/perplexity-xpc) — PerplexityXPC broker service, tray app, MCP server management
- [atera-dashboard](https://github.com/brianatalliance/atera-dashboard) — Atera RMM NOC dashboard — React + Vite + Tailwind + Recharts
- [atera-connector](https://github.com/brianatalliance/atera-connector) — Atera RMM API v3 connector — Python CLI with full CRUD support
- [synology-connector](https://github.com/brianatalliance/synology-connector) — Synology DSM Web API connector — 40 CLI actions across 10 modules
- [udm-nspawn-pki](https://github.com/brianatalliance/udm-nspawn-pki) — Two-tier PKI in systemd-nspawn on UniFi Dream Machine Pro
- [wireguard-vpn-spk](https://github.com/brianatalliance/wireguard-vpn-spk) — WireGuard VPN Tunnel SPK for Synology DS220+ (userspace wireguard-go)
- [nas-git-sync](https://github.com/brianatalliance/nas-git-sync) — Automated GitHub to Synology NAS repo sync script

## Acknowledgments

- [Perplexity AI](https://www.perplexity.ai/) — Provider of the Sonar API
- [Perplexity Sonar API](https://docs.perplexity.ai/) — Official API documentation
- [Python](https://www.python.org/) — Standard library only; no external dependencies required

## Author

**Brian Vicente** — Network Coordinator & Cybersecurity Admin

Built with [Perplexity Computer](https://computer.perplexity.ai)

## License

MIT License — see [LICENSE](LICENSE) for details.
