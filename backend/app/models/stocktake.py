from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Stocktake(Base, TimestampMixin):
    __tablename__ = "stocktakes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    scope = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, default="open")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    items = relationship("StocktakeItem", back_populates="stocktake", cascade="all, delete-orphan")


class StocktakeItem(Base, TimestampMixin):
    __tablename__ = "stocktake_items"

    id = Column(Integer, primary_key=True, index=True)
    stocktake_id = Column(Integer, ForeignKey("stocktakes.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    scanned_at = Column(DateTime, nullable=True)
    note = Column(String(200), nullable=True)

    stocktake = relationship("Stocktake", back_populates="items")
