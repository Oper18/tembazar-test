import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from v1.manager import GoodsManager, AccountManager, UserGoodsManager

from v1.goods.request_models import (
    GoodsCreateRequest
)

from v1.account.request_models import (
    AccountCreateRequest,
)

from models.base import AnonymousUser


async def test_manage_account():
    anonym = AnonymousUser()
    manager = GoodsManager(anonym)

    for i in range(10):
        status, _ = await manager.create_item(
            GoodsCreateRequest(
                name=f"good{i}",
                price=10 * i,
            )
        )
        assert status

    goods = await manager.list_goods()
    assert len(goods) == 10

    acc_manager = AccountManager(anonym)
    status, user = await acc_manager.create_account(
        user=AccountCreateRequest(
            username="test",
            password="password",
        )
    )
    assert status
    acc_manager.author = user

    shop_manager = UserGoodsManager(user)
    status = await shop_manager.buy_good_by_user(goods[0].id)
    assert status

    user_goods = await shop_manager.get_user_goods(user.id)
    assert len(user_goods) == 1
