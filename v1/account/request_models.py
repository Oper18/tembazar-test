from typing import Optional

from pydantic import BaseModel, Field


class AccountCreateRequest(BaseModel):
    username: str = Field(title="account username")
    password: str = Field(title="account password")


class AccountManageRequest(BaseModel):
    id: int = Field(title="account pk")
    username: Optional[str] = Field(None, title="account username")
    points: Optional[int] = Field(None, title="user's balance")
    password: Optional[str] = Field(None, title="account password")
