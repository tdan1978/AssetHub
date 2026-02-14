from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class DashboardTemplate(Base, TimestampMixin):
    __tablename__ = "dashboard_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    is_default = Column(Boolean, nullable=False, default=False)
    is_published = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    widgets = relationship(
        "DashboardWidget",
        back_populates="template",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
