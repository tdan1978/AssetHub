from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class AssetBase(BaseModel):
    sn: str
    asset_no: str
    name: str
    category: str
    category_id: int | None = None
    status: int = 0
    user_id: int | None = None
    dept: str | None = None
    price: Decimal | None = None
    purchase_at: date | None = None
    warranty_at: date | None = None
    location: str | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    category_id: int | None = None
    status: int | None = None
    user_id: int | None = None
    dept: str | None = None
    price: Decimal | None = None
    purchase_at: date | None = None
    warranty_at: date | None = None
    location: str | None = None


class AssetOut(AssetBase):
    id: int

    class Config:
        from_attributes = True
