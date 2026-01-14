from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class SystemField(Base, TimestampMixin):
    __tablename__ = "system_fields"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("system_field_categories.id"), nullable=True)
    name = Column(String(100), nullable=False)
    field_key = Column(String(100), nullable=False)
    field_type = Column(String(30), nullable=False)
    is_required = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)
    visibility_rules = Column(JSON, nullable=True)
    reminder_enabled = Column(Boolean, default=False)
    reminder_days = Column(Integer, nullable=True)
    sort_order = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)

    category = relationship("SystemFieldCategory", back_populates="fields")
