from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.role import Role
from app.models.user import User
from app.models.role_permission import RolePermission
from app.models.user_role import user_roles
from app.schemas.role import RoleOut, RoleCreate, RoleUpdate
from app.schemas.role_permission import RolePermissionOut, RolePermissionUpdate

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])

PROTECTED_ROLE_CODES = {
    "super_admin",
}


@router.get("", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db), _: object = Depends(require_permission("roles", "view"))):
    return db.query(Role).filter(Role.is_deleted == False).order_by(Role.id.asc()).all()


@router.get("/me/permissions", response_model=list[RolePermissionOut])
def list_my_permissions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    role_ids = []
    role_codes = []
    if user.role_id and user.role and user.role.is_active:
        role_ids.append(user.role_id)
        role_codes.append(user.role.code)
    if user.roles:
        role_ids.extend([role.id for role in user.roles if role.is_active])
        role_codes.extend([role.code for role in user.roles if role.is_active])
    role_ids = list({rid for rid in role_ids if rid})
    role_codes = list({code for code in role_codes if code})
    if "super_admin" in role_codes:
        return []
    if not role_ids:
        return []
    items = db.query(RolePermission).filter(RolePermission.role_id.in_(role_ids)).all()
    merged = {}
    for item in items:
        key = f"{item.resource}:{item.action}"
        scope = item.scope or "all"
        if key not in merged or merged[key] == "own" and scope == "all":
            merged[key] = scope
    return [
        {"resource": k.split(":")[0], "action": k.split(":")[1], "scope": v}
        for k, v in merged.items()
    ]


@router.get("/{role_id}/permissions", response_model=list[RolePermissionOut])
def list_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("roles", "view")),
):
    items = db.query(RolePermission).filter(RolePermission.role_id == role_id).all()
    return items


@router.put("/{role_id}/permissions", response_model=list[RolePermissionOut])
def update_role_permissions(
    role_id: int,
    payload: RolePermissionUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("roles", "update")),
):
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    for item in payload.permissions:
        db.add(RolePermission(role_id=role_id, resource=item.resource, action=item.action, scope=item.scope))
    db.commit()
    return db.query(RolePermission).filter(RolePermission.role_id == role_id).all()


@router.post("", response_model=RoleOut)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("roles", "update")),
):
    exists = db.query(Role).filter(Role.code == payload.code, Role.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="Role code exists")
    exists = db.query(Role).filter(Role.name == payload.name, Role.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="Role name exists")
    item = Role(name=payload.name, code=payload.code, is_active=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("roles", "update")),
):
    role = db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.code in PROTECTED_ROLE_CODES:
        raise HTTPException(status_code=400, detail="Role is protected")
    role.is_active = payload.is_active
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("roles", "update")),
):
    role = db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.code in PROTECTED_ROLE_CODES:
        raise HTTPException(status_code=400, detail="Role is protected")
    user_exists = (
        db.query(User)
        .join(user_roles, user_roles.c.user_id == User.id)
        .filter(user_roles.c.role_id == role_id, User.is_deleted == False)
        .first()
    )
    if user_exists:
        raise HTTPException(status_code=400, detail="Role has users")
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    db.execute(user_roles.delete().where(user_roles.c.role_id == role_id))
    role.is_deleted = True
    db.commit()
    return {"message": "Deleted"}
