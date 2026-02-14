from sqlalchemy import Column, Integer, String, Boolean

from app.core.database import Base
from app.models.base import TimestampMixin


class LdapConfig(Base, TimestampMixin):
    __tablename__ = "ldap_configs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(20), default="ad")
    is_active = Column(Boolean, default=False)
    host = Column(String(200), nullable=True)
    port = Column(Integer, default=389)
    use_ssl = Column(Boolean, default=False)
    use_starttls = Column(Boolean, default=False)
    base_dn = Column(String(255), nullable=True)
    bind_dn = Column(String(255), nullable=True)
    bind_password = Column(String(255), nullable=True)
    user_filter = Column(String(255), default="(&(objectClass=user)(!(objectClass=computer)))")
    username_attr = Column(String(100), default="sAMAccountName")
    display_name_attr = Column(String(100), default="displayName")
    email_attr = Column(String(100), default="mail")
    phone_attr = Column(String(100), default="mobile")
    dept_attr = Column(String(100), default="department")
    default_role_code = Column(String(50), default="employee")
    allow_login = Column(Boolean, default=True)
    auto_create = Column(Boolean, default=True)
