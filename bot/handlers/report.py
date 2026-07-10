from uuid import UUID

from telegram import Update
from telegram.ext import ContextTypes

from bot.database.report_repository import ReportRepository
from bot.database.repository import ScanRepository
from bot.models.report import UrlReport

_CONFIRMATION = {
    "en": "🚩 Reported. Thank you for helping keep the community safe.",
    "km": "🚩 បានរាយការណ៍។ អរគុណសម្រាប់ការជួយធានាសុវត្ថិភាពសហគមន៍។",
}
_ALREADY_GONE = {
    "en": "This report could no longer be processed.",
    "km": "មិនអាចដំណើរការរបាយការណ៍នេះបានទៀតទេ។",
}


async def handle_report_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    report_repo: ReportRepository,
    scan_repo: ScanRepository,
    admin_chat_id: int | None,
) -> None:
    query = update.callback_query
    scan_id = UUID(query.data.split(":", 1)[1])

    record = await scan_repo.get_by_id(scan_id)
    if record is None:
        await query.answer(_ALREADY_GONE["en"])
        return

    await report_repo.insert_report(
        UrlReport(
            scan_record_id=scan_id,
            chat_id=update.effective_chat.id,
            user_id=update.effective_user.id,
            url=record.url,
        )
    )

    await query.answer(_CONFIRMATION[record.language])

    if admin_chat_id is not None:
        await context.bot.send_message(
            chat_id=admin_chat_id,
            text=(
                f"🚩 URL reported by user {update.effective_user.id} in chat {update.effective_chat.id}\n"
                f"URL: {record.url}\n"
                f"Verdict: {record.final_risk_level}"
            ),
        )
