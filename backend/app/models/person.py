from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Person(Base, TimestampMixin):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    emp_code = Column(String(50), nullable=True)
    dept_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    status = Column(String(20), nullable=True)
    is_deleted = Column(Boolean, default=False)

    department = relationship("Department")
