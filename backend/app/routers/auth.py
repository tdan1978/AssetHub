from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password, create_access_token, hash_password
from app.models.user import User
from app.models.ldap_config import LdapConfig
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.schemas.common import Token, Message
from app.utils.ldap_client import authenticate_user, extract_attr

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username, User.is_deleted == False).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        ldap_config = db.query(LdapConfig).first()
        if not ldap_config or not ldap_config.is_active or not ldap_config.allow_login:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        entry = authenticate_user(ldap_config, form_data.username, form_data.password)
        if not entry:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            if not ldap_config.auto_create:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
            role = db.query(Role).filter(Role.code == ldap_config.default_role_code).first()
            if not role:
                role = db.query(Role).filter(Role.is_deleted == False).order_by(Role.id.asc()).first()
            full_name = extract_attr(entry, ldap_config.display_name_attr) or form_data.username
            dept = extract_attr(entry, ldap_config.dept_attr)
            phone = extract_attr(entry, ldap_config.phone_attr)
            user = User(
                username=form_data.username,
                full_name=full_name,
                password_hash=hash_password(form_data.password),
                role_id=role.id if role else 1,
                dept=dept,
                phone=phone,
                is_active=True,
                is_deleted=False,
            )
            db.add(user)
            db.commit()
            if role:
                user.roles = [role]
                db.commit()
        else:
            user.is_active = True
            user.is_deleted = False
            db.commit()
    role_codes = []
    if user.role and user.role.is_active:
        role_codes.append(user.role.code)
    if user.roles:
        role_codes.extend([role.code for role in user.roles if role.is_active])
    role_codes = list({code for code in role_codes if code})
    role_code = "super_admin" if "super_admin" in role_codes else (role_codes[0] if role_codes else "")
    token = create_access_token(
        {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role_code": role_code,
            "role_codes": role_codes,
        }
    )
    return Token(access_token=token, username=user.username, full_name=user.full_name)


@router.post("/init", response_model=Message)
def init_system(db: Session = Depends(get_db)):
    roles = [
        ("超级管理员", "super_admin"),
        ("办公资产管理员", "office_asset_admin"),
        ("数据中心资产管理员", "datacenter_asset_admin"),
        ("软件资产管理员", "software_admin"),
        ("系统资产管理员", "system_admin"),
        ("系统资产维护人", "system_maintainer"),
        ("财务审计", "auditor"),
        ("普通员工", "employee"),
    ]
    for name, code in roles:
        exists = db.query(Role).filter(Role.code == code).first()
        if not exists:
            db.add(Role(name=name, code=code))
    db.commit()

    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        role = db.query(Role).filter(Role.code == "super_admin").first()
        db.add(
            User(
                username="admin",
                full_name="系统管理员",
                password_hash=hash_password("admin123"),
                role_id=role.id,
                dept="IT",
            )
        )
        db.commit()
    seed_role_permissions(db)
    return Message(message="Initialized")


def seed_role_permissions(db: Session):
    role_map = {role.code: role.id for role in db.query(Role).all()}
    defaults = {
        "system_admin": [
            ("dashboard", "view"),
            ("dashboard", "edit"),
            ("dashboard", "publish"),
            ("system_assets", "view", "all"),
            ("system_assets", "create"),
            ("system_assets", "update", "all"),
            ("system_assets", "delete"),
            ("system_fields", "view"),
            ("system_fields", "create"),
            ("system_fields", "update"),
            ("system_fields", "delete"),
            ("dictionaries", "view"),
            ("dictionaries", "create"),
            ("dictionaries", "update"),
            ("dictionaries", "delete"),
            ("notifications", "view"),
        ],
        "system_maintainer": [
            ("dashboard", "view"),
            ("system_assets", "view", "own"),
            ("system_assets", "update", "own"),
            ("notifications", "view"),
        ],
        "office_asset_admin": [
            ("dashboard", "view"),
            ("office_hardware_assets", "view"),
            ("office_hardware_assets", "create"),
            ("office_hardware_assets", "update"),
            ("office_hardware_assets", "delete"),
            ("asset_types", "view"),
            ("asset_types", "create"),
            ("asset_types", "update"),
            ("asset_types", "delete"),
            ("dictionaries", "view"),
            ("dictionaries", "create"),
            ("dictionaries", "update"),
            ("dictionaries", "delete"),
            ("maintenance", "view"),
            ("maintenance", "create"),
            ("maintenance", "update"),
            ("scrap", "view"),
            ("scrap", "update"),
            ("stocktakes", "view"),
            ("stocktakes", "create"),
            ("stocktakes", "update"),
            ("scan", "view"),
            ("notifications", "view"),
        ],
        "datacenter_asset_admin": [
            ("dashboard", "view"),
            ("datacenter_hardware_assets", "view"),
            ("datacenter_hardware_assets", "create"),
            ("datacenter_hardware_assets", "update"),
            ("datacenter_hardware_assets", "delete"),
            ("asset_types", "view"),
            ("asset_types", "create"),
            ("asset_types", "update"),
            ("asset_types", "delete"),
            ("dictionaries", "view"),
            ("dictionaries", "create"),
            ("dictionaries", "update"),
            ("dictionaries", "delete"),
            ("maintenance", "view"),
            ("maintenance", "create"),
            ("maintenance", "update"),
            ("scrap", "view"),
            ("scrap", "update"),
            ("stocktakes", "view"),
            ("stocktakes", "create"),
            ("stocktakes", "update"),
            ("scan", "view"),
            ("notifications", "view"),
        ],
        "software_admin": [
            ("dashboard", "view"),
            ("software_assets", "view"),
            ("software_assets", "create"),
            ("software_assets", "update"),
            ("software_assets", "delete"),
            ("software_fields", "view"),
            ("software_fields", "create"),
            ("software_fields", "update"),
            ("software_fields", "delete"),
            ("dictionaries", "view"),
            ("dictionaries", "create"),
            ("dictionaries", "update"),
            ("dictionaries", "delete"),
            ("notifications", "view"),
        ],
        "auditor": [
            ("dashboard", "view"),
            ("reports", "view"),
            ("logs", "view"),
            ("office_hardware_assets", "view"),
            ("datacenter_hardware_assets", "view"),
            ("software_assets", "view"),
            ("system_assets", "view"),
            ("notifications", "view"),
        ],
        "employee": [
            ("dashboard", "view"),
            ("office_hardware_assets", "view"),
            ("datacenter_hardware_assets", "view"),
            ("notifications", "view"),
        ],
    }
    for role_code, perms in defaults.items():
        role_id = role_map.get(role_code)
        if not role_id:
            continue
        for item in perms:
            resource = item[0]
            action = item[1]
            scope = item[2] if len(item) > 2 else None
            existing = (
                db.query(RolePermission)
                .filter(
                    RolePermission.role_id == role_id,
                    RolePermission.resource == resource,
                    RolePermission.action == action,
                )
                .first()
            )
            if existing:
                if scope and existing.scope != scope:
                    existing.scope = scope
                continue
            db.add(RolePermission(role_id=role_id, resource=resource, action=action, scope=scope))
    db.commit()


@router.post("/change-password", response_model=Message)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return Message(message="Password updated")

