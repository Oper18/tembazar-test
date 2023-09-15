from typing import Optional

from pydantic import BaseModel, Field


class AccountInfoResponse(BaseModel):
    id: int = Field(title="user pk")
    username: str = Field(title="username")
    points: int = Field(title="user's balance")
