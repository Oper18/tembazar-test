from pydantic import BaseModel, Field


class GoodResponse(BaseModel):
    id: int = Field(title="good pk")
    name: str = Field(title="item name")
    price: int = Field(title="item price")
