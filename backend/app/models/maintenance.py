from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class MaintenanceInfo(Base, TimestampMixin):
    __tablename__ = "maintenance_infos"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, unique=True)
    vendor = Column(String(120), nullable=True)
    contract_no = Column(String(120), nullable=True)
    support_phone = Column(String(50), nullable=True)
    warranty_at = Column(Date, nullable=True)
    is_deleted = Column(Boolean, default=False)

    asset = relationship("Asset")


class RepairRecord(Base, TimestampMixin):
    __tablename__ = "repair_records"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    issue = Column(String(200), nullable=False)
    vendor = Column(String(120), nullable=True)
    cost = Column(String(50), nullable=True)
    status = Column(String(30), nullable=False, default="open")
    note = Column(String(200), nullable=True)
    is_deleted = Column(Boolean, default=False)

    asset = relationship("Asset")
