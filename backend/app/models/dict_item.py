from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class DictItem(Base, TimestampMixin):
    __tablename__ = "dict_items"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey("dict_types.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    value = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    type = relationship("DictType", back_populates="items")


Index("ix_dict_items_type_name", DictItem.type_id, DictItem.name, unique=True)
