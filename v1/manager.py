import uuid

from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy.future import select
from sqlalchemy import delete

from models.session import get_session, AsyncSession
from models.models import Users, Goods, UserGoods
from models.base import AnonymousUser

from v1.account.request_models import (
    AccountCreateRequest,
    AccountManageRequest,
)
from v1.goods.request_models import GoodsCreateRequest

from util import password_hash

from settings import ACTIVE_DB


class BaseManager(object):
    """
    Base class for crud operation on objects
    """
    def __init__(self, author: Union[Users, AnonymousUser]):
        self.author = author

    async def _create_record(
        self,
        model: Any,
        create_fields: Dict[str, Any],
        s: AsyncSession,
    ) -> Any:
        """
        Create record inside passed table
        :param model - SQLAlchemy model defined in models.models
        :param create_fields - dict where keys are fields of the sent model
        :param s - session where record creating
        """
        record = model(**create_fields)
        s.add(record)
        await s.flush()
        await s.refresh(record)
        return record

    async def _update_record(
        self,
        model: Any,
        update_fields: Dict[str, Any],
        s: AsyncSession,
    ) -> Any:
        """
        Update passed record
        :param model - instance of SQLAlchemy model defined in models.models
        :param update_fields - dict where keys are fields of the sent model
        :param s - session where record creating
        """
        for k, v in update_fields.values():
            if k == "id":
                continue
            if v is not None:
                setattr(model, k, v)

        s.add(model)
        await s.flush()

        return model


class AccountManager(BaseManager):

    async def create_account(
        self, user: AccountCreateRequest
    ) -> Tuple[bool, Optional[Users]]:
        """
        Create new user record
        :param user - pydantic model of new user
        """
        try:
            async with get_session(ACTIVE_DB) as s:
                salt = uuid.uuid4().hex
                new_user = await self._create_record(
                    Users,
                    {
                        "username": user.username,
                        "password": password_hash(user.password, salt),
                        "salt": salt,
                    },
                    s,
                )
                await s.commit()
        except Exception:
            return False, None
        else:
            return True, new_user

    async def update_account(
        self,
        user: AccountManageRequest,
    ) -> Tuple[bool, Users]:
        """
        Update user record
        :param user - pydantic model of changing user
        """
        try:
            async with get_session(ACTIVE_DB) as s:
                account = (
                    await s.execute(
                        select(Users)
                        .filter(Users.id == user.id)
                    )
                ).scalars().first()
                if not account:
                    return False, None
                if not self.author.admin and user.points is not None:
                    return False, account

                account = await self._update_record(
                    account, user.dict(), s
                )

                await s.commit()
        except Exception:
            return False, None
        else:
            return True, account

    async def remove_account(
        self,
        user_id: int,
    ) -> bool:
        """
        Remove user record
        :param user_id - pk of removing user
        """
        try:
            if self.author.id != user_id and not self.author.admin:
                return False
            async with get_session(ACTIVE_DB) as s:
                account = (
                    await s.execute(
                        select(Users)
                        .filter(Users.id == user_id)
                    )
                ).scalars().first()
                if not account:
                    return False
                await (
                    s.execute(
                        delete(Users)
                        .filter(Users.id == user_id)
                    )
                )
        except Exception:
            return False
        else:
            return True


class GoodsManager(BaseManager):
    async def create_item(self, good: GoodsCreateRequest) -> Goods:
        """
        Create new good record
        :param good - pydantic model of new good
        """
        try:
            async with get_session(ACTIVE_DB) as s:
                new_good = await self._create_record(
                    Goods, good.dict(), s
                )
            await s.commit()
        except Exception:
            return False, None
        else:
            return True, new_good

    async def _get_goods(
        self,
        s: AsyncSession,
    ) -> List[Goods]:
        """
        Get full goods list
        """
        return (
            await s.execute(select(Goods))
        ).scalars().all()

    async def _get_good(
        self,
        good_id: int,
        s: AsyncSession,
    ) -> Goods:
        """
        Get one good
        """
        return (
            await s.execute(
                select(Goods).filter(Goods.id == good_id)
            )
        ).scalars().first()

    async def list_goods(
        self,
        good_id: Optional[int] = None,
    ) -> Union[Goods, List[Goods], None]:
        async with get_session(ACTIVE_DB) as s:
            if good_id:
                return await self._get_good(good_id, s)
            return await self._get_goods(s)


class UserGoodsManager(BaseManager):
    async def get_user_goods(self, user_id: int) -> List[Goods]:
        async with get_session(ACTIVE_DB) as s:
            return (
                await s.execute(
                    select(Goods)
                    .join(UserGoods, UserGoods.good_id == Goods.id)
                    .filter(UserGoods.user_id == user_id)
                )
            ).fetchall()

    async def _get_object_for_update(self, model: Any, pk: int, s: AsyncSession) -> Any:
        return (
            await s.execute(
                select(model)
                .filter(model.id == pk)
                .with_for_update()
            )
        ).scalars().first()

    async def buy_good_by_user(self, good_id: int) -> bool:
        try:
            async with get_session(ACTIVE_DB) as s:
                user = await self._get_object_for_update(Users, self.author.id, s)
                if not user:
                    return False
                
                good = await self._get_object_for_update(Goods, good_id, s)
                if not good:
                    return False

                if good.price > user.points:
                    return False

                s.add(UserGoods(user_id=self.author.id, good_id=good_id))
                await s.flush()
                user.points = user.points - good.price
                await s.flush()
                
                await s.commit()
        except Exception:
            return False
        else:
            return True

