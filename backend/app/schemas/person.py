from pydantic import BaseModel


class PersonBase(BaseModel):
    name: str
    emp_code: str | None = None
    dept_id: int | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    name: str | None = None
    emp_code: str | None = None
    dept_id: int | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None


class PersonOut(PersonBase):
    id: int

    class Config:
        from_attributes = True
