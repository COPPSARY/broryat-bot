import asyncio

from sqlalchemy import Engine
from sqlmodel import Session

from bot.models.user_preference import UserPreference
from bot.utils.time import now_phnom_penh


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
                    pref.updated_at = now_phnom_penh()
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)

    async def set_username(self, user_id: int, username: str | None) -> None:
        def _upsert() -> None:
            with Session(self._engine) as session:
                pref = session.get(UserPreference, user_id)
                if pref is None:
                    pref = UserPreference(user_id=user_id, username=username)
                else:
                    pref.username = username
                    pref.updated_at = now_phnom_penh()
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)

    async def set_name(self, user_id: int, first_name: str | None, last_name: str | None) -> None:
        def _upsert() -> None:
            with Session(self._engine) as session:
                pref = session.get(UserPreference, user_id)
                if pref is None:
                    pref = UserPreference(user_id=user_id, first_name=first_name, last_name=last_name)
                else:
                    pref.first_name = first_name
                    pref.last_name = last_name
                    pref.updated_at = now_phnom_penh()
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)
