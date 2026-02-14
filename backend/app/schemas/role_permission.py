from pydantic import BaseModel


class RolePermissionOut(BaseModel):
    resource: str
    action: str
    scope: str | None = None

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    permissions: list[RolePermissionOut]
