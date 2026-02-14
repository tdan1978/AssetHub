from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    name: str
    code: str | None = None
    parent_id: int | None = None
    sort_order: int = 0
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    parent_id: int | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class DepartmentOut(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class DepartmentTreeOut(DepartmentOut):
    children: list["DepartmentTreeOut"] = Field(default_factory=list)


DepartmentTreeOut.model_rebuild()
