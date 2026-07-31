# Configuration

All configuration lives in `.env` (see `.env.example` for a template):

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `AI_PROVIDER` | `gemini` \| `openai` \| `anthropic` \| `huggingface` |
| `LLM_MODEL` | Model name for the selected provider (used for both text classification and OCR) |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `HUGGINGFACE_API_KEY` | API key for the selected provider |
| `VT_API_KEY` | VirusTotal API v3 key |
| `VT_RPM_LIMIT` / `VT_DAILY_LIMIT` / `VT_MONTHLY_LIMIT` | VirusTotal rate-limit ceilings (defaults match the free tier) |
| `DATABASE_URL` | Postgres connection string — tables are created automatically on startup |
| `GROUP_SCAN_ENABLED` | Enable/disable group scanning |
| `ADMIN_CHAT_ID` | Telegram chat ID that receives report notifications |
| `LOG_LEVEL` | Standard Python logging level |

## Getting API keys

You only need a key for the AI provider you set `AI_PROVIDER` to, plus VirusTotal (always required) and a Telegram bot token.

| Service | Where to get a key | Notes |
|---|---|---|
| Telegram bot token | [@BotFather](https://t.me/BotFather) → `/newbot` | Free. Paste the token into `TELEGRAM_BOT_TOKEN`. |
| VirusTotal | [virustotal.com/gui/join-us](https://www.virustotal.com/gui/join-us) → sign up → [API key page](https://www.virustotal.com/gui/my-apikey) | Free tier matches the defaults in `.env.example` (4 requests/min, 500/day, 15.5K/month). |
| Google Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Free tier available. Set `AI_PROVIDER=gemini`. |
| OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | Requires billing set up on the account. Set `AI_PROVIDER=openai`. |
| Anthropic (Claude) | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) | Requires billing set up on the account. Set `AI_PROVIDER=anthropic`. |
| Hugging Face | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) → create a **read** token | Free tier available (limited monthly inference credits — see the note below). Set `AI_PROVIDER=huggingface`, the default in `.env.example`. |

> **Note:** Hugging Face's free inference credits are limited and reset monthly — once exhausted, calls fail with an HTTP 402 until the quota resets or you add paid credits. If you're running the bot in production, prefer Gemini, OpenAI, or Anthropic for reliability.

Set `LLM_MODEL` to a model name your chosen provider supports (used for both text classification and OCR) — see each provider's docs for current model names, since this changes over time.
