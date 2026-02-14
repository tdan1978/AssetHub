from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.user_role import user_roles


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    dept = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    wecom_name = Column(String(100), nullable=True)
    asset_scope = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    role = relationship("Role", back_populates="primary_users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    @property
    def role_ids(self) -> list[int]:
        if self.roles:
            return [role.id for role in self.roles]
        return [self.role_id] if self.role_id else []
