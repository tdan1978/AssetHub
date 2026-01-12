from sqlalchemy import Column, Integer, ForeignKey, JSON

from app.core.database import Base
from app.models.base import TimestampMixin


class AssetFieldValue(Base, TimestampMixin):
    __tablename__ = "asset_field_values"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    field_id = Column(Integer, ForeignKey("category_fields.id"), nullable=False)
    value = Column(JSON, nullable=True)
