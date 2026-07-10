import asyncio
from datetime import datetime, timezone

from sqlalchemy import Engine
from sqlmodel import Session

from bot.models.group_preference import GroupPreference


class GroupPreferenceRepository:
    def __init__(self, engine: Engine):
        self._engine = engine

    async def get_language(self, chat_id: int) -> str | None:
        def _query() -> str | None:
            with Session(self._engine) as session:
                pref = session.get(GroupPreference, chat_id)
                return pref.language if pref else None

        return await asyncio.to_thread(_query)

    async def set_language(self, chat_id: int, language: str) -> None:
        def _upsert() -> None:
            with Session(self._engine) as session:
                pref = session.get(GroupPreference, chat_id)
                if pref is None:
                    pref = GroupPreference(chat_id=chat_id, language=language)
                else:
                    pref.language = language
                    pref.updated_at = datetime.now(timezone.utc)
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)
