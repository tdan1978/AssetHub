from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class LicenseBase(BaseModel):
    software_name: str | None = None
    version: str | None = None
    vendor: str | None = None
    category: str | None = None
    vendor_url: str | None = None
    license_type: str | None = None
    billing_mode: str | None = None
    license_key: str | None = None
    total_quantity: int | None = None
    used_quantity: int = 0
    activation_limit: str | None = None
    expiry_type: str | None = None
    expire_at: date | None = None
    renewal_at: date | None = None
    compliance_status: str | None = None
    cost: Decimal | None = None
    purchase_date: date | None = None
    order_no: str | None = None
    supplier: str | None = None


class LicenseCreate(LicenseBase):
    pass


class LicenseOut(LicenseBase):
    id: int

    class Config:
        from_attributes = True
