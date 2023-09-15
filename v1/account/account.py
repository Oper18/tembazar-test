from typing import Any, Optional, Union

from fastapi import (
    APIRouter,
    Header,
    status,
    Response,
    Request,
)

from response_models import Error40xResponse
from .response_models import AccountInfoResponse
from .request_models import AccountManageRequest

from base_obj import (
    login_required,
)

from v1.manager import AccountManager


router = APIRouter(
    prefix="/v1/account",
    tags=["account"]
)


@router.get(
    "/info",
    responses={
        200: {
            "model": AccountInfoResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    },
    summary="account info"
)
@login_required
async def get_account_info_handler(
    request: Request,
    response: Response,
    authorization: Optional[str] = Header(None),
    status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> AccountInfoResponse:
    return AccountInfoResponse.parse_obj(request.user.as_dict)


@router.put(
    "/manage",
    responses={
        200: {
            "model": AccountInfoResponse,
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
    manage_account: AccountManageRequest,
    authorization: Optional[str] = Header(None),
    status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> Union[Error40xResponse, AccountInfoResponse]:
    manager = AccountManager(request.user)
    status, acc = await manager.update_account(manage_account)
    if status:
        return AccountInfoResponse.parse_obj(acc.as_dict())
    return Error40xResponse(reason="update failed")
