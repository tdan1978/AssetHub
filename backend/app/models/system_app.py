from sqlalchemy import Column, Integer, String, Boolean

from app.core.database import Base
from app.models.base import TimestampMixin


class SystemApp(Base, TimestampMixin):
    __tablename__ = "system_apps"

    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String(200), nullable=True)
    app_code = Column(String(100), unique=True, nullable=True)
    app_status = Column(String(50), nullable=True)
    access_url = Column(String(255), nullable=True)
    app_category = Column(String(100), nullable=True)
    arch_type = Column(String(100), nullable=True)
    dev_lang = Column(String(100), nullable=True)
    db_type = Column(String(100), nullable=True)
    deploy_type = Column(String(100), nullable=True)
    repo_url = Column(String(255), nullable=True)
    biz_owner = Column(String(100), nullable=True)
    tech_owner = Column(String(100), nullable=True)
    ops_owner = Column(String(100), nullable=True)
    sec_level = Column(String(100), nullable=True)
    is_deleted = Column(Boolean, default=False)
