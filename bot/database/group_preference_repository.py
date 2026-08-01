import asyncio

from sqlalchemy import Engine
from sqlmodel import Session

from bot.models.group_preference import GroupPreference
from bot.utils.time import now_phnom_penh


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
                    pref.updated_at = now_phnom_penh()
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)

    async def set_group_name(self, chat_id: int, group_name: str | None) -> None:
        def _upsert() -> None:
            with Session(self._engine) as session:
                pref = session.get(GroupPreference, chat_id)
                if pref is None:
                    pref = GroupPreference(chat_id=chat_id, group_name=group_name)
                else:
                    pref.group_name = group_name
                    pref.updated_at = now_phnom_penh()
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)

    async def set_added_by(self, chat_id: int, added_by_user_id: int) -> None:
        def _upsert() -> None:
            with Session(self._engine) as session:
                pref = session.get(GroupPreference, chat_id)
                if pref is None:
                    pref = GroupPreference(chat_id=chat_id, added_by_user_id=added_by_user_id)
                else:
                    pref.added_by_user_id = added_by_user_id
                    pref.updated_at = now_phnom_penh()
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)
