from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    full_name: str
    role_id: int
    dept: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    role_id: int | None = None
    dept: str | None = None
    is_active: bool | None = None
    password: str | None = None


class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
