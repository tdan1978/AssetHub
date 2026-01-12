from datetime import date
from datetime import datetime
from pydantic import BaseModel


class MaintenanceInfoBase(BaseModel):
    asset_id: int
    vendor: str | None = None
    contract_no: str | None = None
    support_phone: str | None = None
    warranty_at: date | None = None


class MaintenanceInfoCreate(MaintenanceInfoBase):
    pass


class MaintenanceInfoUpdate(BaseModel):
    vendor: str | None = None
    contract_no: str | None = None
    support_phone: str | None = None
    warranty_at: date | None = None


class MaintenanceInfoOut(MaintenanceInfoBase):
    id: int

    class Config:
        from_attributes = True


class RepairRecordBase(BaseModel):
    asset_id: int
    issue: str
    vendor: str | None = None
    cost: str | None = None
    status: str = "open"
    note: str | None = None


class RepairRecordCreate(RepairRecordBase):
    pass


class RepairRecordUpdate(BaseModel):
    issue: str | None = None
    vendor: str | None = None
    cost: str | None = None
    status: str | None = None
    note: str | None = None


class RepairRecordOut(RepairRecordBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True
