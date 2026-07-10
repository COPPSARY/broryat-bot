import asyncio

from sqlalchemy import Engine
from sqlmodel import Session

from bot.models.report import UrlReport


class ReportRepository:
    def __init__(self, engine: Engine):
        self._engine = engine

    async def insert_report(self, report: UrlReport) -> UrlReport:
        def _insert() -> UrlReport:
            with Session(self._engine) as session:
                session.add(report)
                session.commit()
                session.refresh(report)
                return report

        return await asyncio.to_thread(_insert)
