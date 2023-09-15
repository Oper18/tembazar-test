# coding: utf-8

from typing import Optional

from pydantic import BaseModel, Field


class AuthResponse(BaseModel):
    access_token: Optional[str] = Field(title="jwt: Authorization: Bearer <access token>")
    refresh_token: Optional[str] = Field(title="token for refresh access token")
    temporary_password: Optional[bool] = Field(None, title="is user password temporary, uses for admins and operators")
