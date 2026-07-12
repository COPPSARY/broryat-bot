import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram.ext import Application

from bot.config.settings import get_settings
from bot.database.engine import create_db_and_tables, get_engine
from bot.database.group_preference_repository import GroupPreferenceRepository
from bot.database.report_repository import ReportRepository
from bot.database.repository import ScanRepository
from bot.database.user_preference_repository import UserPreferenceRepository
from bot.handlers import register_handlers, set_bot_commands
from bot.services.ai.factory import get_ai_provider
from bot.services.ai.image_extractor import HuggingFaceImageExtractor
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


def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    _start_health_check_server()

    ai_provider = get_ai_provider(settings)

    rate_limiter = VTRateLimiter(
        rpm_limit=settings.vt_rpm_limit,
        daily_limit=settings.vt_daily_limit,
        monthly_limit=settings.vt_monthly_limit,
    )
    vt_client = VirusTotalClient(api_key=settings.vt_api_key, rate_limiter=rate_limiter)

    engine = get_engine(settings.database_url)
    create_db_and_tables(engine)
    repo = ScanRepository(engine)
    user_pref_repo = UserPreferenceRepository(engine)
    group_pref_repo = GroupPreferenceRepository(engine)
    report_repo = ReportRepository(engine)

    pipeline = ScanPipeline(ai_provider, vt_client, repo)
    breach_client = BreachCheckClient()
    image_extractor = HuggingFaceImageExtractor(
        api_key=settings.huggingface_api_key, model=settings.ocr_model
    )

    app = Application.builder().token(settings.telegram_bot_token).post_init(set_bot_commands).build()
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
    )

    app.run_polling()


if __name__ == "__main__":
    main()
