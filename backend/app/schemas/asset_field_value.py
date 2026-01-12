from pydantic import BaseModel


class AssetFieldValueIn(BaseModel):
    field_id: int
    value: object | None = None


class AssetFieldValueOut(BaseModel):
    id: int
    asset_id: int
    field_id: int
    value: object | None = None

    class Config:
        from_attributes = True
