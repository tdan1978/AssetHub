from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total: int
    items: List[T]


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserToken(BaseModel):
    user_id: int
    username: str
    role_code: str
    exp: int


class Pagination(BaseModel):
    page: int = 1
    size: int = 20
    q: Optional[str] = None
