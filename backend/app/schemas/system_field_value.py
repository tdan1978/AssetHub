from pydantic import BaseModel


class SystemFieldValueIn(BaseModel):
    field_id: int
    value: object | None = None


class SystemFieldValueOut(SystemFieldValueIn):
    id: int
    system_id: int

    class Config:
        from_attributes = True
