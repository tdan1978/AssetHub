from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint

from app.core.database import Base
from app.models.base import TimestampMixin


class RolePermission(Base, TimestampMixin):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    scope = Column(String(20), nullable=True)

    __table_args__ = (UniqueConstraint("role_id", "resource", "action", name="uq_role_permission"),)
