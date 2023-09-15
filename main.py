# coding: utf-8

import traceback
from json import JSONDecodeError
from typing import List

from fastapi import FastAPI, Response, Request, status
from pydantic.error_wrappers import ValidationError
from starlette.responses import JSONResponse

from base_obj import (
    check_token,
)
from models.base import AnonymousUser
from response_models import Error40xResponse
from v1.auth.auth import router as auth_router
from v1.account.account import router as account_router
from v1.goods.goods import router as goods_router
from v1.shop.shop import router as shop_router


app = FastAPI(title="Test TemBazar API", version="1.0", root_path="/api")


app.include_router(auth_router)
app.include_router(account_router)
app.include_router(goods_router)
app.include_router(shop_router)


@app.middleware("http")
async def login_requests(request: Request, call_next, *args, **kwargs):
    request.scope["user"] = AnonymousUser()
    request.scope["auth"] = {"status": False, "reason": ""}
    if request.headers.get("authorization"):
        try:
            user_type, token = request.headers.get("authorization").split(' ')
            code, reason, user_info = await check_token(token=token)
        except:
            request.scope["auth"]["reason"] = "wrong token type"
        else:
            request.scope["user"] = user_info
            request.scope["auth"]["reason"] = reason
    else:
        request.scope["auth"]["reason"] = "no token"

    try:
        response = await call_next(request)
    except Exception:
        trace = traceback.format_exc()
        print(trace)
        response = Response(
            content=Error40xResponse(reason="Internal error").json(),
            status_code=status.HTTP_409_CONFLICT,
            media_type="application/json",
        )

    return response


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "reason": type(exc).__name__,
            "model": exc.model.__name__,
            "errors": exc.errors(),
        }
    )


@app.exception_handler(JSONDecodeError)
async def json_decode_handler(request, exc: JSONDecodeError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "reason": type(exc).__name__
        }
    )
