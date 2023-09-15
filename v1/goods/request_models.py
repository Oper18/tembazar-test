from pydantic import BaseModel, Field


class GoodsCreateRequest(BaseModel):
    name: str = Field(title="item name")
    price: int = Field(title="item price")
