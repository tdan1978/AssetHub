from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class DashboardWidget(Base, TimestampMixin):
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("dashboard_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    widget_key = Column(String(100), nullable=False)
    title = Column(String(100), nullable=False)
    widget_type = Column(String(20), nullable=False)  # kpi | chart
    metric_key = Column(String(100), nullable=False)
    col_span = Column(Integer, nullable=False, default=1)
    row_span = Column(Integer, nullable=False, default=1)
    sort_order = Column(Integer, nullable=False, default=0)
    style_config = Column(JSON, nullable=True)
    data_source_config = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    template = relationship("DashboardTemplate", back_populates="widgets")
