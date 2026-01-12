from sqlalchemy import Column, Integer, String, Text, Date

from app.core.database import Base
from app.models.base import TimestampMixin


class License(Base, TimestampMixin):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    license_key = Column(Text, nullable=False)
    total_qty = Column(Integer, nullable=False)
    used_qty = Column(Integer, nullable=False, default=0)
    expire_at = Column(Date, nullable=True)
