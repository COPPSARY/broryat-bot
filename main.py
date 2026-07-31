import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import AIORateLimiter, Application, ContextTypes

from bot.config.settings import get_settings
from bot.database.engine import create_db_and_tables, get_engine
from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.report_repository import ReportRepository
from bot.database.repository import ScanRepository
from bot.database.secretary_preference_repository import SecretaryPreferenceRepository
from bot.database.user_preference_repository import UserPreferenceRepository
from bot.handlers import register_handlers, set_bot_commands
from bot.services.ai.providers.factory import get_ai_provider
from bot.services.ai.image_extractors.factory import get_image_extractor
from bot.services.breach_check.client import BreachCheckClient
from bot.services.pipeline import ScanPipeline
from bot.services.virustotal.client import VirusTotalClient
from bot.services.virustotal.rate_limiter import VTRateLimiter


class _HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass


def _start_health_check_server() -> None:
    """Bind a dummy HTTP port so free-tier hosts (e.g. Render) treat this as a live web service."""
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), _HealthCheckHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    update_id = update.update_id if isinstance(update, Update) else None
    logging.getLogger(__name__).error(
        "Unhandled error while processing update %s: %s", update_id, context.error
    )


def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    _start_health_check_server()

    ai_provider = get_ai_provider(settings)

    vt_keys = settings.vt_api_keys
    rate_limiter = VTRateLimiter(
        rpm_limit=settings.vt_rpm_limit * len(vt_keys),
        daily_limit=settings.vt_daily_limit * len(vt_keys),
        monthly_limit=settings.vt_monthly_limit * len(vt_keys),
    )
    vt_client = VirusTotalClient(
        api_key=None,
        api_keys=vt_keys,
        rate_limiter=rate_limiter,
    )
    engine = get_engine(
        settings.database_url,
        pool_size=20,
        max_overflow=20,
        pool_pre_ping=True,
    )
    create_db_and_tables(engine)
    repo = ScanRepository(engine)
    user_pref_repo = UserPreferenceRepository(engine)
    group_pref_repo = GroupPreferenceRepository(engine)
    report_repo = ReportRepository(engine)
    secretary_pref_repo = SecretaryPreferenceRepository(engine)

    pipeline = ScanPipeline(ai_provider, vt_client, repo)
    breach_client = BreachCheckClient()
    image_extractor = get_image_extractor(settings)

    app = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .rate_limiter(AIORateLimiter())
        .concurrent_updates(True)
        .post_init(set_bot_commands)
        .build()
    )
    app.add_error_handler(_error_handler)
    register_handlers(
        app,
        pipeline,
        settings.group_scan_enabled,
        user_pref_repo,
        group_pref_repo,
        report_repo,
        repo,
        settings.admin_chat_id,
        breach_client,
        image_extractor,
        settings.max_file_size_bytes,
        secretary_pref_repo=secretary_pref_repo,
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
