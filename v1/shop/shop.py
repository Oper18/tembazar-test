from typing import Any, List, Optional, Union

from fastapi import (
    APIRouter,
    Header,
    status,
    Response,
    Request,
)

from response_models import Error40xResponse
from .request_models import BuyGoodRequest

from base_obj import (
    login_required,
)

from v1.manager import UserGoodsManager


router = APIRouter(
    prefix="/v1/shop",
    tags=["shop"]
)


@router.post(
    "/buy",
    responses={
        200: {
            "model": Error40xResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    },
    summary="account info"
)
@login_required
async def change_account_info_handler(
    request: Request,
    response: Response,
    buy_request: BuyGoodRequest,
    authorization: Optional[str] = Header(None),
    status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> Error40xResponse:
    manager = UserGoodsManager(request.user)
    status = await manager.buy_good_by_user(buy_request.good_id)
    if status:
        return Error40xResponse(reason="bought")
    response.status_code = status.HTTP_400_BAD_REQUEST
    return Error40xResponse(reason="buying failed")
