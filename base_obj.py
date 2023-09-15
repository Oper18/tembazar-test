# coding: utf-8

import datetime
import logging
from functools import wraps

import jwt
from fastapi import status
from sqlalchemy.future import select

from models.base import (
    AnonymousUser,
)
from models.models import (
    Users,
)
from models.session import get_session
from response_models import Error40xResponse
from settings import (
    SERVER_SECRET,
    ACTIVE_DB,
)

logger = logging.getLogger('verum_base_obj')


async def check_token(token):
    try:
        token_info = jwt.decode(token, SERVER_SECRET, algorithms=['HS256'])
    except Exception as e:
        return status.HTTP_401_UNAUTHORIZED, 'wrong token type', AnonymousUser()
    else:
        user_info = AnonymousUser()
        async with get_session(ACTIVE_DB) as s:
            user_info = (
                await s.execute(
                    select(Users)
                    .filter(Users.id == token_info['user_id'])
                )
            ).fetchone()
        if not user_info.is_anonymous:
            if user_info.password == token_info['password'] and \
                    token_info['expiration_time'] >= datetime.datetime.now().timestamp():
                return status.HTTP_200_OK, 'user authenticated', user_info
            else:
                return status.HTTP_401_UNAUTHORIZED, 'token expired', AnonymousUser()
        else:
            return status.HTTP_401_UNAUTHORIZED, 'no user', AnonymousUser()


def accept_user_type(user_type):
    def decorator(func):
        @wraps(func)
        async def wrapper(**kwargs):
            if kwargs.get('request').user and kwargs['request'].user.type in user_type:
                return await func(**kwargs)
            else:
                kwargs['response'].status_code = status.HTTP_406_NOT_ACCEPTABLE
                return Error40xResponse.parse_obj({'reason': 'wrong user_type'})
        return wrapper
    return decorator


def login_required(func):
    @wraps(func)
    async def wrapper(**kwargs):
        if kwargs.get('request').user and not kwargs['request'].user.is_anonymous:
            return await func(**kwargs)
        else:
            kwargs['response'].status_code = status.HTTP_401_UNAUTHORIZED
            return Error40xResponse.parse_obj({'reason': kwargs.get('request').auth.get("reason")})
    return wrapper
