import asyncio

from sqlalchemy import Engine
from sqlmodel import Session, select

from bot.models.secretary_preference import SecretaryPreference
from bot.utils.time import now_phnom_penh


class SecretaryPreferenceRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def set_business_connection(
        self, user_id: int, connection_id: str | None
    ) -> None:
        def _upsert() -> None:
            with Session(self._engine) as session:
                pref = session.get(SecretaryPreference, user_id)

                if pref is None:
                    pref = SecretaryPreference(
                        user_id=user_id,
                        business_connection_id=connection_id,
                    )
                else:
                    pref.business_connection_id = connection_id
                    pref.updated_at = now_phnom_penh()

                pref.enabled = connection_id is not None
                session.add(pref)
                session.commit()

        await asyncio.to_thread(_upsert)

    async def get_by_connection(
        self, connection_id: str
    ) -> SecretaryPreference | None:
        def _query() -> SecretaryPreference | None:
            with Session(self._engine) as session:
                statement = select(SecretaryPreference).where(
                    SecretaryPreference.business_connection_id == connection_id
                )
                return session.exec(statement).first()

        return await asyncio.to_thread(_query)
