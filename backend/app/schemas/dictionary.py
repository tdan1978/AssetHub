from pydantic import BaseModel


class DictTypeBase(BaseModel):
    name: str
    code: str
    scope: str = "global"
    description: str | None = None
    sort_order: int = 0
    is_active: bool = True


class DictTypeCreate(DictTypeBase):
    pass


class DictTypeUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    scope: str | None = None
    description: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class DictTypeOut(DictTypeBase):
    id: int

    class Config:
        from_attributes = True


class DictItemBase(BaseModel):
    type_id: int
    name: str
    value: str | None = None
    sort_order: int = 0
    is_active: bool = True


class DictItemCreate(DictItemBase):
    pass


class DictItemUpdate(BaseModel):
    name: str | None = None
    value: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class DictItemOut(DictItemBase):
    id: int

    class Config:
        from_attributes = True
