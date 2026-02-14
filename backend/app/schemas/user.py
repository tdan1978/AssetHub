from pydantic import BaseModel

from app.schemas.role import RoleOut


class UserBase(BaseModel):
    username: str
    full_name: str
    dept: str | None = None
    phone: str | None = None
    wecom_name: str | None = None
    role_ids: list[int]


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    dept: str | None = None
    phone: str | None = None
    wecom_name: str | None = None
    role_ids: list[int] | None = None
    is_active: bool | None = None
    password: str | None = None


class UserOut(UserBase):
    id: int
    is_active: bool
    roles: list[RoleOut] = []

    class Config:
        from_attributes = True
