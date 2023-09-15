from typing import Any

from sqlalchemy import update

from models.session import get_session


class DbsSynchronization(object):

    @classmethod
    async def sync_data(
        cls,
        target_db: str,
        target_model: Any,
        update_data: dict,
        where_clause: list,
    ) -> None:
        async with get_session(bind=target_db) as s:
            await s.execute(
                update(target_model)
                .where(*where_clause)
                .values(update_data)
            )
            await s.commit()
