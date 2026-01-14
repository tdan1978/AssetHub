from pydantic import BaseModel


class SoftwareFieldValueIn(BaseModel):
    field_id: int
    value: object | None = None


class SoftwareFieldValueOut(SoftwareFieldValueIn):
    id: int
    license_id: int

    class Config:
        from_attributes = True
