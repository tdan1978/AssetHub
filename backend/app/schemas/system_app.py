from pydantic import BaseModel


class SystemAppBase(BaseModel):
    app_name: str | None = None
    app_code: str | None = None
    app_status: str | None = None
    access_url: str | None = None
    app_category: str | None = None
    arch_type: str | None = None
    dev_lang: str | None = None
    db_type: str | None = None
    deploy_type: str | None = None
    repo_url: str | None = None
    biz_owner: str | None = None
    tech_owner: str | None = None
    ops_owner: str | None = None
    ops_owner_b: str | None = None
    sec_level: str | None = None


class SystemAppCreate(SystemAppBase):
    pass


class SystemAppUpdate(BaseModel):
    app_name: str | None = None
    app_code: str | None = None
    app_status: str | None = None
    access_url: str | None = None
    app_category: str | None = None
    arch_type: str | None = None
    dev_lang: str | None = None
    db_type: str | None = None
    deploy_type: str | None = None
    repo_url: str | None = None
    biz_owner: str | None = None
    tech_owner: str | None = None
    ops_owner: str | None = None
    ops_owner_b: str | None = None
    sec_level: str | None = None


class SystemAppOut(SystemAppBase):
    id: int
    ops_owner_name: str | None = None
    ops_owner_b_name: str | None = None

    class Config:
        from_attributes = True
