import asyncio
from datetime import datetime, timezone

from sqlalchemy import Engine
from sqlmodel import Session

from bot.models.user_preference import UserPreference


class UserPreferenceRepository:
    def __init__(self, engine: Engine):
        self._engine = engine

    async def get_language(self, user_id: int) -> str | None:
        def _query() -> str | None:
            with Session(self._engine) as session:
                pref = session.get(UserPreference, user_id)
                return pref.language if pref else None

        return await asyncio.to_thread(_query)

    async def set_language(self, user_id: int, language: str) -> None:
        def _upsert() -> None:
            with Session(self._engine) as session:
                pref = session.get(UserPreference, user_id)
                if pref is None:
                    pref = UserPreference(user_id=user_id, language=language)
                else:
                    pref.language = language
                    pref.updated_at = datetime.now(timezone.utc)
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)
