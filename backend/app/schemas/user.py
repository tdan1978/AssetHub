from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    full_name: str
    role_id: int
    dept: str | None = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
