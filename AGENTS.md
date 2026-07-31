# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Status

Phase 1 MVP is implemented: a Telegram bot (long polling) that scans private-chat text/forwarded messages/files/URLs and group messages (scan-only, no moderation) using a provider-agnostic AI intent classifier (Gemini implemented; OpenAI/Anthropic/HuggingFace are future providers behind the same interface) combined with VirusTotal API v3. Group moderation actions, campaign detection, and the admin dashboard are Phase 2+ and not implemented. The PRD lives at `docs/requirements.md`; treat it as the scope source of truth.

Storage connects directly to Postgres via SQLModel/SQLAlchemy (not the Supabase REST client) — `DATABASE_URL` in `.env` must point at a real Postgres database (e.g. a Supabase project's connection string). The `scan_records` table is created automatically at startup via `SQLModel.metadata.create_all()` (see `bot/database/engine.py`); there is no separate migration file to run by hand. All other components are fully unit-tested against mocks/an in-memory SQLite engine and don't need real credentials to develop against.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency and environment management (Python 3.13, pinned in `.python-version`).

- Run the bot: `uv run main.py` (requires a populated `.env` — copy `.env.example`)
- Run all tests: `uv run pytest`
- Run a single test file: `uv run pytest tests/services/test_risk_engine.py`
- Run a single test: `uv run pytest tests/services/test_risk_engine.py::test_vt_malicious_file_always_wins_over_safe_ai`
- Add a dependency: `uv add <package>`

No real network calls are made in the test suite — VirusTotal/Gemini are mocked at their client boundary (`respx` for HTTP, `AsyncMock`/`MagicMock` for SDK clients), and the database layer is tested against a real in-memory SQLite engine (via SQLAlchemy's `StaticPool`) rather than mocks. Async tests run automatically without `@pytest.mark.asyncio` (`asyncio_mode = "auto"` in `pyproject.toml`).

## Module Layout

- `bot/config/settings.py` — `pydantic-settings` config loaded from `.env`; `get_settings()` is a cached singleton.
- `bot/schemas/` — pydantic DTOs (`RiskLevel` enum, `IntentResult`, `VTFileVerdict`/`VTUrlVerdict`, `ScanRequest`/`ScanResult`) passed between layers; not persisted directly.
- `bot/models/scan_record.py` — `ScanRecord`, a `SQLModel` table model (`table=True`) that both defines the `scan_records` schema and is used directly as the ORM row object.
- `bot/utils/` — pure helpers shared by handlers and services: URL extraction/normalization, Khmer/English language detection, streaming SHA-256 hashing, file-extension allow-list.
- `bot/services/risk_engine.py` — the core business rule as a pure function: `merge_verdicts(ai, vt_file, vt_url)`. VirusTotal's verdict always wins when it has a confirmed malicious/suspicious result; otherwise falls back to the AI verdict. Read this file before changing how risk is computed.
- `bot/services/virustotal/` — `rate_limiter.py` (sliding-window limiter for the free tier's 4/min, 500/day, 15.5K/month caps — all time/sleep calls are dependency-injected for deterministic testing), `client.py` (thin httpx wrapper over VT v3: file report/upload/analysis, URL scan/report), `polling.py` (waits for async VT analyses to complete), `cache.py` (checks `scan_records` for a recent match before ever calling VT, to conserve the free-tier quota).
- `bot/services/ai/` — `prompt.py` (shared prompt builder encoding the PRD's scam categories), `response_parsing.py` (extracts the trailing `RISK:LEVEL` marker every provider's reply ends with).
  - `bot/services/ai/providers/` — `base.py` (`AIProvider` ABC + `AIProviderError`), `gemini.py`/`openai.py`/`anthropic.py`/`huggingface.py` (concrete text-classification providers), `factory.py` (`get_ai_provider(settings)` — the sole seam other code depends on; add new providers here, not by branching in callers).
  - `bot/services/ai/image_extractors/` — mirrors the providers package but for OCR: `base.py` (`ImageExtractor` ABC + `ImageExtractionError` + shared `INSTRUCTION`), `gemini.py`/`openai.py`/`anthropic.py`/`huggingface.py`, `factory.py` (`get_image_extractor(settings)` — picks the OCR backend from `settings.ai_provider`, same as the text provider).
- `bot/services/pipeline.py` — `ScanPipeline.run(request)`, the orchestrator: resolves file/URL VirusTotal verdicts (cache-first, then upload/scan + poll) concurrently with the AI classification, merges them via `risk_engine`, persists a `ScanRecord`, and returns a `ScanResult`. Free of any Telegram-specific types.
- `bot/database/` — `engine.py` (`get_engine(database_url)` wraps `sqlmodel.create_engine`; `create_db_and_tables(engine)` runs `SQLModel.metadata.create_all`), `repository.py` (`ScanRepository`: `insert_scan`, `find_recent_by_hash`, `find_recent_by_url` — SQLAlchemy's sync `Session` is wrapped in `asyncio.to_thread` since it has no stable async driver in use here).
- `bot/handlers/` — the Telegram transport layer: `commands.py` (`/start`, `/help`), `private.py` (routes private-chat text/forwarded/file/URL messages into a `ScanRequest`), `group.py` (same pipeline call, but replies only when risk is above `SAFE` and never deletes/warns/notifies — moderation is explicitly Phase 2), `formatting.py` (renders the bilingual risk-report template), `__init__.py` (`register_handlers` wires everything into the PTB `Application`).
- `main.py` — thin composition root: builds settings → AI provider → rate-limited VT client → DB engine (creates tables) + repo → `ScanPipeline` → registers handlers → `run_polling()`.

## Product Context (from docs/requirements.md)

**Broryat AI** is an AI-powered cybersecurity platform, starting as a Telegram bot and expanding into a community threat-intelligence platform for Cambodia. Read `docs/requirements.md` in full before implementing features — it is the source of truth for scope and behavior. Key points:

- **Inputs**: forwarded Telegram messages, uploaded files, pasted URLs, and plain text, in Khmer and English.
- **Detection pipeline**: AI-based social engineering/intent detection combined with VirusTotal API v3 (files and URLs). VirusTotal's verdict always takes priority over the AI verdict when available.
- **File handling**: compute SHA-256 before submitting to VirusTotal; supported formats include EXE, DLL, ZIP, RAR, 7Z, PDF, DOCX, XLSX, APK, JS, BAT, VBS.
- **URL handling**: extract and normalize URLs before scanning.
- **Storage**: Postgres (in practice, a Supabase-hosted database) is the intended database for scan results and threat intelligence (URL, domain, SHA-256, filename, VirusTotal verdict, AI verdict, timestamp, language, category), accessed directly via SQLModel/SQLAlchemy.
- **Group protection**: the bot can run in Telegram groups with configurable modes (warn only / delete malicious content / strict / normal), including compromised-account detection (e.g., a trusted user suddenly posting malware or repeated phishing links).
- **Campaign detection & reporting**: aggregating repeated attacks across users/groups, with a human-reviewed (not auto-submitted) reporting workflow to hosting providers, registrars, Cloudflare, Google Safe Browsing, PhishTank, URLhaus, OpenPhish, etc.
- **Phased roadmap**: (1) Telegram bot MVP with AI + VirusTotal detection, (2) real-time group protection, (3) threat intelligence/analytics dashboard, (4) takedown/reporting platform with public API.

Overall data flow as described in the PRD:

```
Telegram User / Group → Telegram Bot → AI Intent Detection → VirusTotal API v3 → Risk Engine → Supabase → Threat Intelligence → Admin Dashboard
```