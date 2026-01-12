from datetime import date
from pydantic import BaseModel


class LicenseBase(BaseModel):
    name: str
    license_key: str
    total_qty: int
    used_qty: int = 0
    expire_at: date | None = None


class LicenseCreate(LicenseBase):
    pass


class LicenseOut(LicenseBase):
    id: int

    class Config:
        from_attributes = True
