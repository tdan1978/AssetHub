from sqlalchemy import Column, Integer, ForeignKey, JSON

from app.core.database import Base
from app.models.base import TimestampMixin


class SoftwareFieldValue(Base, TimestampMixin):
    __tablename__ = "software_field_values"

    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey("licenses.id"), nullable=False)
    field_id = Column(Integer, ForeignKey("software_fields.id"), nullable=False)
    value = Column(JSON, nullable=True)
