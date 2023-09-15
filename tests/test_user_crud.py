import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from v1.manager import AccountManager

from v1.account.request_models import (
    AccountCreateRequest,
    AccountManageRequest,
)

from models.base import AnonymousUser


async def test_manage_account():
    anonym = AnonymousUser()
    manager = AccountManager(anonym)
    status, user = await manager.create_account(
        user=AccountCreateRequest(
            username="test",
            password="password",
        )
    )
    assert status
    assert user.username == "test"
    assert user.password != "password"
    assert user.points == 0

    status, user_changed = await manager.update_account(
        user=AccountManageRequest(
            id=user.id,
            points=100,
        )
    )
    assert status
    assert user_changed.points == 100

    status, _ = await manager.update_account(
        user=AccountManageRequest(
            id=user.id,
            password="test_password",
        )
    )
    assert not status

    manager.author = user
    status, user_changed = await manager.update_account(
        user=AccountManageRequest(
            id=user.id,
            password="new_password",
        )
    )
    assert status
    assert user_changed.password != user.password
