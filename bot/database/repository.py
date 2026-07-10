import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import Engine
from sqlmodel import Session, select

from bot.models.scan_record import ScanRecord


class ScanRepository:
    def __init__(self, engine: Engine):
        self._engine = engine

    async def insert_scan(self, record: ScanRecord) -> ScanRecord:
        def _insert() -> ScanRecord:
            with Session(self._engine) as session:
                session.add(record)
                session.commit()
                session.refresh(record)
                return record

        return await asyncio.to_thread(_insert)

    async def get_by_id(self, scan_id: UUID) -> ScanRecord | None:
        def _query() -> ScanRecord | None:
            with Session(self._engine) as session:
                return session.get(ScanRecord, scan_id)

        return await asyncio.to_thread(_query)

    async def find_recent_by_hash(self, sha256: str, within_hours: int = 24) -> ScanRecord | None:
        return await self._find_recent(ScanRecord.sha256, sha256, within_hours)

    async def find_recent_by_url(self, url: str, within_hours: int = 24) -> ScanRecord | None:
        return await self._find_recent(ScanRecord.url, url, within_hours)

    async def _find_recent(self, column, value: str, within_hours: int) -> ScanRecord | None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=within_hours)

        def _query() -> ScanRecord | None:
            with Session(self._engine) as session:
                statement = (
                    select(ScanRecord)
                    .where(column == value, ScanRecord.created_at >= cutoff)
                    .order_by(ScanRecord.created_at.desc())
                    .limit(1)
                )
                return session.exec(statement).first()

        return await asyncio.to_thread(_query)
