# coding: utf-8

from typing import Optional

from enum import IntEnum

from pydantic import BaseModel, Field


class Error40xResponse(BaseModel):
    reason: Optional[str]


class MethodStatus(IntEnum):
    actual = 1
    outdated = 2
    ineffectual = 3


class CheckMethodResponse(BaseModel):
    endpoint: str = Field(description="path of api endpoint without domain")
    method: str = Field(description="http method type")
    status: MethodStatus = Field(MethodStatus.actual, description="status of method actual")


class HttpExceptionResponse(BaseModel):
    detail: Optional[str]
