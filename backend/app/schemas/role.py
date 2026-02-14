from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    code: str


class RoleOut(BaseModel):
    id: int
    name: str
    code: str
    is_active: bool = True

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    is_active: bool
