from pydantic import BaseModel
from app.schemas.software_field import SoftwareFieldOut


class SoftwareFieldCategoryBase(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    sort_order: int = 0
    is_active: bool = True


class SoftwareFieldCategoryCreate(SoftwareFieldCategoryBase):
    pass


class SoftwareFieldCategoryUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class SoftwareFieldCategoryOut(SoftwareFieldCategoryBase):
    id: int

    class Config:
        from_attributes = True


class SoftwareFieldCategoryWithFields(SoftwareFieldCategoryOut):
    fields: list[SoftwareFieldOut] = []
