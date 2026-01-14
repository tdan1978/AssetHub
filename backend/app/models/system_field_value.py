from sqlalchemy import Column, Integer, ForeignKey, JSON

from app.core.database import Base
from app.models.base import TimestampMixin


class SystemFieldValue(Base, TimestampMixin):
    __tablename__ = "system_field_values"

    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(Integer, ForeignKey("system_apps.id"), nullable=False)
    field_id = Column(Integer, ForeignKey("system_fields.id"), nullable=False)
    value = Column(JSON, nullable=True)
