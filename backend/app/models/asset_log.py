from sqlalchemy import Column, BigInteger, Integer, String, DateTime, JSON, ForeignKey

from app.core.database import Base
from app.models.base import TimestampMixin


class AssetLog(Base, TimestampMixin):
    __tablename__ = "asset_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(20), nullable=False)
    change_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
