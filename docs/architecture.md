# Architecture

```
Telegram User / Group → Telegram Bot → AI Intent Detection → VirusTotal API v3 → Risk Engine → Postgres
```

| Layer | Location |
|---|---|
| Telegram transport | `bot/handlers/` (`private.py`, `group.py`, `media.py`, `commands.py`, `report.py`) |
| Orchestration | `bot/services/pipeline.py` (`ScanPipeline`) |
| AI text classification | `bot/services/ai/providers/` (`base.py`, `factory.py`, `gemini.py`, `openai.py`, `anthropic.py`, `huggingface.py`) |
| AI image OCR | `bot/services/ai/image_extractors/` — mirrors `providers/`, one OCR backend per AI provider |
| VirusTotal client | `bot/services/virustotal/` (`client.py`, `rate_limiter.py`, `cache.py`, `polling.py`) |
| Persistence | `bot/database/` + `bot/models/` (SQLModel over Postgres/Supabase) |
| Shared utilities | `bot/utils/` (URL extraction/validation, trusted domains, language detection, hashing) |

Adding a new AI provider means adding one file under `providers/` (and `image_extractors/` for OCR support) and one branch in the matching `factory.py` — no changes needed anywhere else in the pipeline.
