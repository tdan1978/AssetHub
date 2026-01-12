from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    sn = Column(String(64), unique=True, nullable=False, index=True)
    asset_no = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    category = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    status = Column(Integer, nullable=False, index=True, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    dept = Column(String(100), nullable=True)
    price = Column(Numeric(12, 2), nullable=True)
    purchase_at = Column(Date, nullable=True)
    warranty_at = Column(Date, nullable=True)
    location = Column(String(200), nullable=True)
    is_deleted = Column(Boolean, default=False)

    user = relationship("User")
    category_ref = relationship("Category")


Index("ix_assets_status_dept", Asset.status, Asset.dept)
