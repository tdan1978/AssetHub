from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class CategoryField(Base, TimestampMixin):
    __tablename__ = "category_fields"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    field_key = Column(String(100), nullable=False)
    field_type = Column(String(30), nullable=False)
    is_required = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)
    visibility_rules = Column(JSON, nullable=True)
    reminder_enabled = Column(Boolean, default=False)
    reminder_days = Column(Integer, nullable=True)
    repeatable = Column(Boolean, default=False)
    data_source = Column(String(50), nullable=True)
    searchable = Column(Boolean, default=False)
    multi_select_mode = Column(String(20), nullable=True)
    usage_scope = Column(String(20), nullable=True)
    sort_order = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)

    category = relationship("Category", back_populates="fields")
