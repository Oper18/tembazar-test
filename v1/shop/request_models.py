from pydantic import BaseModel, Field


class BuyGoodRequest(BaseModel):
    good_id: int = Field(title="buying good")
