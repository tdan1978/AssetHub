from pydantic import BaseModel


class LdapConfigBase(BaseModel):
    provider: str = "ad"
    is_active: bool = False
    host: str | None = None
    port: int = 389
    use_ssl: bool = False
    use_starttls: bool = False
    base_dn: str | None = None
    bind_dn: str | None = None
    bind_password: str | None = None
    user_filter: str = "(&(objectClass=user)(!(objectClass=computer)))"
    username_attr: str = "sAMAccountName"
    display_name_attr: str = "displayName"
    email_attr: str = "mail"
    phone_attr: str = "mobile"
    dept_attr: str = "department"
    default_role_code: str = "employee"
    allow_login: bool = True
    auto_create: bool = True


class LdapConfigUpdate(LdapConfigBase):
    pass


class LdapConfigOut(LdapConfigBase):
    id: int
    has_password: bool = False

    class Config:
        from_attributes = True


class LdapTestResult(BaseModel):
    ok: bool
    message: str
    users_found: int | None = None


class LdapSyncResult(BaseModel):
    ok: bool
    created: int
    updated: int
    skipped: int
