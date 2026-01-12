from pydantic import BaseModel


class RoleOut(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True
