from sqlalchemy import Column, Integer, String, Text, Date, Numeric

from app.core.database import Base
from app.models.base import TimestampMixin


class License(Base, TimestampMixin):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    software_name = Column("name", String(100), nullable=True)
    version = Column(String(50), nullable=True)
    vendor = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    vendor_url = Column(String(255), nullable=True)
    license_type = Column(String(50), nullable=True)
    billing_mode = Column(String(50), nullable=True)
    license_key = Column(Text, nullable=True)
    total_quantity = Column("total_qty", Integer, nullable=True)
    used_quantity = Column("used_qty", Integer, nullable=False, default=0)
    activation_limit = Column(String(50), nullable=True)
    expiry_type = Column(String(50), nullable=True)
    expire_at = Column(Date, nullable=True)
    renewal_at = Column(Date, nullable=True)
    compliance_status = Column(String(50), nullable=True)
    cost = Column(Numeric(12, 2), nullable=True)
    purchase_date = Column(Date, nullable=True)
    order_no = Column(String(100), nullable=True)
    supplier = Column(String(100), nullable=True)
