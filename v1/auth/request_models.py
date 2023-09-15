from pydantic import BaseModel, Field


class Auth(BaseModel):
    """
        authentication body
    """
    username: str = Field(title="username of registered user")
    password: str = Field(None, title="user password")
    test_link: str = Field(None, title="link to test, for examinee")


class Refresh(BaseModel):
    refresh_token: str = Field(title="token for refresh auth token, getting with auth")
