from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class SystemFieldCategory(Base, TimestampMixin):
    __tablename__ = "system_field_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=True)
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    fields = relationship("SystemField", back_populates="category", cascade="all, delete-orphan")
