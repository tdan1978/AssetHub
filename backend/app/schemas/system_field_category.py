from pydantic import BaseModel
from app.schemas.system_field import SystemFieldOut


class SystemFieldCategoryBase(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    sort_order: int = 0
    is_active: bool = True


class SystemFieldCategoryCreate(SystemFieldCategoryBase):
    pass


class SystemFieldCategoryUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class SystemFieldCategoryOut(SystemFieldCategoryBase):
    id: int

    class Config:
        from_attributes = True


class SystemFieldCategoryWithFields(SystemFieldCategoryOut):
    fields: list[SystemFieldOut] = []
