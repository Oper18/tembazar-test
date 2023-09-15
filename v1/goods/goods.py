from typing import Any, List, Optional, Union

from fastapi import (
    APIRouter,
    Header,
    status,
    Response,
    Request,
)

from response_models import Error40xResponse
from .response_models import GoodResponse
from .request_models import GoodsCreateRequest

from base_obj import (
    login_required,
)

from v1.manager import GoodsManager


router = APIRouter(
    prefix="/v1/goods",
    tags=["goods"]
)


@router.get(
    "/list",
    responses={
        200: {
            "model": List[GoodResponse],
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    },
    summary="goods list"
)
async def get_goods_list_handler(
    request: Request,
    response: Response,
    status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> List[GoodResponse]:
    manager = GoodsManager(request.user)
    goods = await manager.list_goods()
    return [
        GoodResponse.parse_obj(good.as_dict())
        for good in goods
    ]


@router.get(
    "/{good_id}",
    responses={
        200: {
            "model": GoodResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    },
    summary="good info"
)
async def get_good_info_handler(
    request: Request,
    response: Response,
    good_id: int,
    status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> Union[GoodResponse, Error40xResponse]:
    manager = GoodsManager(request.user)
    good = await manager.list_goods(good_id)
    if not good:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error40xResponse(reason="good not found")

    return GoodResponse.parse_obj(good.as_dict())


@router.post(
    "/create",
    responses={
        200: {
            "model": GoodResponse,
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
    good_request: GoodsCreateRequest,
    authorization: Optional[str] = Header(None),
    status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> Union[GoodResponse, Error40xResponse]:
    manager = GoodsManager(request.user)
    status, good = await manager.create_item(good_request)
    if status:
        return GoodResponse.parse_obj(good.as_dict())
    response.status_code = status.HTTP_400_BAD_REQUEST
    return Error40xResponse(reason="create failed")
