# Broryat AI — Cambodia AI Scam Shield

A Telegram bot that protects Cambodian users from scams, phishing, and malware. It analyzes forwarded messages, uploaded files, and links in both Khmer and English, combining an AI-based social-engineering classifier with VirusTotal API v3 malware intelligence.

See [`docs/requirements.md`](docs/requirements.md) for the full product vision.

## Features

**Private chat**
- Scans forwarded messages, pasted URLs (in text or on their own), and uploaded files of any type.
- Casual typed messages (not forwarded, no link) get a plain-language nudge to forward the suspicious content instead of being scanned.
- Persistent language preference (Khmer/English) with a bilingual fallback when none is set.
- A persistent reply-keyboard menu mirrors the slash-command list (`/help`, `/use`, `/secure`, `/password`, `/addgroup`, `/donate`, `/language`).

**Group chat (scan-only by default, with lightweight moderation)**
- Only scans messages containing a link or an uploaded document — everything else is ignored to keep the group quiet.
- Defaults to Khmer, switchable per-group via `/language`.
- When VirusTotal confirms a file or link is malicious, the bot deletes the message and posts a short warning; everything else stays silent except confirmed threats.

**Detection pipeline**
- AI intent classification (provider-agnostic — Gemini implemented today; OpenAI/Anthropic/Hugging Face share the same interface) detects Telegram impersonation, banking scams, fake recruitment, fake government notices, investment/crypto scams, credential theft, malware delivery, and urgency tactics.
- VirusTotal API v3 for file hashes and URLs, with a sliding-window rate limiter tuned to the free tier (4/min, 500/day, 15.5K/month) and a scan-history cache to avoid redundant lookups.
- Strict URL validation rejects incomplete domains, email addresses, IP addresses, and incidental dotted text (log lines, module paths) — only genuine, well-formed domains are scanned.
- A hardcoded trusted-domain allowlist (major tech companies, banks, Cambodian government sites, etc.) skips scanning entirely for a lone trusted link, while still catching look-alike and suffix-attack domains.
- A per-user (private) / per-chat (group) limit of 2 scans per rolling 24 hours protects API quota.

**Safety-by-design**
- Photos and videos are never scanned directly — only a link in the caption, if present.
- VirusTotal's verdict always takes priority over the AI's when both are available.
- Every scan result — URL, domain, SHA-256, VirusTotal verdict, AI verdict, timestamp, language, category — is persisted for future threat-intelligence use.

## Architecture

```
Telegram User / Group → Telegram Bot → AI Intent Detection → VirusTotal API v3 → Risk Engine → Postgres
```

| Layer | Location |
|---|---|
| Telegram transport | `bot/handlers/` (`private.py`, `group.py`, `media.py`, `commands.py`, `report.py`) |
| Orchestration | `bot/services/pipeline.py` (`ScanPipeline`) |
| AI provider abstraction | `bot/services/ai/` (`base.py`, `factory.py`, `gemini_provider.py`, `prompt.py`) |
| VirusTotal client | `bot/services/virustotal/` (`client.py`, `rate_limiter.py`, `cache.py`, `polling.py`) |
| Persistence | `bot/database/` + `bot/models/` (SQLModel over Postgres/Supabase) |
| Shared utilities | `bot/utils/` (URL extraction/validation, trusted domains, language detection, hashing) |

## Getting started

### Prerequisites

- Python 3.13 (pinned in `.python-version`)
- [uv](https://docs.astral.sh/uv/) for dependency management
- A Postgres database (a [Supabase](https://supabase.com) project works well)
- A [Telegram bot token](https://core.telegram.org/bots#how-do-i-create-a-bot) and a [VirusTotal API key](https://www.virustotal.com/gui/join-us)
- An API key for your chosen AI provider (Gemini by default)

### Setup

```bash
git clone <this-repo>
cd broryat-ai
cp .env.example .env   # fill in your tokens/keys below
uv sync
uv run main.py
```

### Configuration

All configuration lives in `.env` (see `.env.example`):

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `AI_PROVIDER` | `gemini` \| `openai` \| `anthropic` \| `huggingface` |
| `LLM_MODEL` | Model name for the selected provider |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `HUGGINGFACE_API_KEY` | API key for the selected provider |
| `VT_API_KEY` | VirusTotal API v3 key |
| `VT_RPM_LIMIT` / `VT_DAILY_LIMIT` / `VT_MONTHLY_LIMIT` | VirusTotal rate-limit ceilings (defaults match the free tier) |
| `DATABASE_URL` | Postgres connection string (tables are created automatically on startup) |
| `GROUP_SCAN_ENABLED` | Enable/disable group scanning |
| `ADMIN_CHAT_ID` | Telegram chat ID that receives report notifications |
| `LOG_LEVEL` | Standard Python logging level |

## Testing

```bash
uv run pytest
```

No real network calls are made — VirusTotal and the AI provider are mocked at their client boundary (`respx` for HTTP, `AsyncMock`/`MagicMock` for SDK clients), and the database layer runs against a real in-memory SQLite engine.

## Deployment

### Docker (recommended)

Docker is the recommended way to run Broryat AI, in development or in production — it bundles the exact Python version and dependencies the bot was built and tested with, so there's no environment drift.

```bash
# Build the image
docker build -t broryat-ai .

# Run it, loading configuration from .env
docker run -d \
  --name broryat-ai \
  --env-file .env \
  --restart unless-stopped \
  broryat-ai

# Follow logs
docker logs -f broryat-ai

# After pulling new code, rebuild and replace the running container
docker build -t broryat-ai .
docker stop broryat-ai && docker rm broryat-ai
docker run -d --name broryat-ai --env-file .env --restart unless-stopped broryat-ai
```

`--restart unless-stopped` keeps the bot running across host reboots and automatic restarts if it ever crashes.

### Render

`render.yaml` defines a free-tier Docker web service. The bot uses Telegram long polling, so a lightweight health-check HTTP server is started alongside it purely to satisfy Render's free-tier requirement that a web service bind a port; pair it with an uptime pinger (e.g. UptimeRobot) to prevent the free instance from spinning down.

## Project status

This repo implements the Telegram bot: AI + VirusTotal detection, file/URL/text scanning, Khmer & English support, and light group moderation (delete-on-confirmed-malware). A broader community threat-intelligence platform (campaign detection, dashboard, takedown/reporting workflow) is described in [`docs/requirements.md`](docs/requirements.md) and not yet implemented.
