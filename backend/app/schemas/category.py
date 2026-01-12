from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    is_active: bool | None = None


class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True
