# coding: utf-8

import datetime
import jwt

from typing import Optional, Any, Union

from fastapi import (
    APIRouter,
    status,
    Response,
    Header,
    Request,
)

from sqlalchemy.future import select

from response_models import Error40xResponse

from .request_models import (
    Auth,
    Refresh,
)
from .response_models import (
    AuthResponse,
)
from v1.account.request_models import (
    AccountCreateRequest,
)

from models.session import get_session
from models.models import (
    Users,
)

from base_obj import (
    check_token,
)
from util import (
    password_hash,
)
from settings import (
    ACCESS_TOKEN_LIFETIME,
    REFRESH_TOKEN_LIFETIME,
    SERVER_SECRET,
)

from v1.manager import AccountManager


router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"]
)


@router.post(
    "",
    responses={
        200: {
            "model": AuthResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    },
    summary="authentication",
)
async def auth_method(
        request: Request,
        auth: Auth,
        response: Response,
        status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> Union[AuthResponse, Error40xResponse]:
    async with get_session() as s:
        user = (
            await s.execute(
                select(Users)
                .filter(Users.username == auth.username)
            )
        ).fetchone()

        if not user:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return Error40xResponse.parse_obj({"reason": "wrong credentials"})
        if auth.password and user.password != password_hash(password=auth.password, salt=user.salt):
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return Error40xResponse.parse_obj({"reason": "wrong credentials"})
        
        access_token_exp_date = datetime.datetime.now().timestamp() + ACCESS_TOKEN_LIFETIME
        refresh_token_exp_date = datetime.datetime.now().timestamp() + REFRESH_TOKEN_LIFETIME
        access_token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'password': user.password,
                'expiration_time': access_token_exp_date,
                'type': user.type,
            },
            SERVER_SECRET,
            algorithm='HS256'
        )
        refresh_token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'password': user.password,
                'expiration_time': refresh_token_exp_date,
                'type': user.type,
            },
            SERVER_SECRET,
            algorithm='HS256'
        )

        return AuthResponse.parse_obj(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "temporary_password": user.temporary_password,
            }
        )


@router.post(
    "/refresh",
    responses={
        200: {
            "model": AuthResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    },
    summary="access token refresh",
)
async def auth_refresh_method(
        request: Request,
        refresh: Refresh,
        response: Response,
        status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> Union[AuthResponse, Error40xResponse]:
    code, response, user = await check_token(refresh.refresh_token)
    if code == status.HTTP_200_OK:
        access_token_exp_date = datetime.datetime.now().timestamp() + ACCESS_TOKEN_LIFETIME
        refresh_token_exp_date = datetime.datetime.now().timestamp() + REFRESH_TOKEN_LIFETIME
        access_token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'password': user.password,
                'expiration_time': access_token_exp_date,
                'type': user.type,
            },
            SERVER_SECRET,
            algorithm='HS256'
        )
        refresh_token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'password': user.password,
                'expiration_time': refresh_token_exp_date,
                'type': user.type,
            },
            SERVER_SECRET,
            algorithm='HS256'
        )
        return AuthResponse.parse_obj({'access_token': access_token, 'refresh_token': refresh_token})

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return Error40xResponse.parse_obj({'reason': 'wrong refresh token'})


@router.post(
    "/register",
    responses={
        200: {
            "model": Error40xResponse,
        },
        401: {
            "model": Error40xResponse,
            "description": "wrong auth token",
        },
    },
    summary="access token refresh",
)
async def register_method(
    request: Request,
    new_acc: AccountCreateRequest,
    response: Response,
    status_code: Optional[Any] = Header(status.HTTP_200_OK, description="internal usage, not used by client"),
) -> Union[AuthResponse, Error40xResponse]:
    manager = AccountManager(request.user)
    status, new_user = await manager.create_account(new_acc)
    if not status:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error40xResponse(reason="registration failed")
    return Error40xResponse(reason="registration success")
