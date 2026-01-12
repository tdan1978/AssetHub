from datetime import datetime
from pydantic import BaseModel


class StocktakeCreate(BaseModel):
    name: str
    scope: str | None = None


class StocktakeItemOut(BaseModel):
    id: int
    asset_id: int
    status: str
    scanned_at: datetime | None = None
    note: str | None = None

    class Config:
        from_attributes = True


class StocktakeOut(BaseModel):
    id: int
    name: str
    scope: str | None = None
    status: str
    items: list[StocktakeItemOut] = []

    class Config:
        from_attributes = True
