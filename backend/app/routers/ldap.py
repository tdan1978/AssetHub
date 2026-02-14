from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.core.security import hash_password
from app.models.ldap_config import LdapConfig
from app.models.role import Role
from app.models.user import User
from app.schemas.ldap import LdapConfigUpdate, LdapConfigOut, LdapTestResult, LdapSyncResult
from app.utils.ldap_client import authenticate_user, search_users, extract_attr

router = APIRouter(prefix="/api/v1/ldap", tags=["ldap"])


def get_or_create_config(db: Session) -> LdapConfig:
    config = db.query(LdapConfig).first()
    if not config:
        config = LdapConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def to_out(config: LdapConfig) -> LdapConfigOut:
    return LdapConfigOut(
        id=config.id,
        provider=config.provider,
        is_active=config.is_active,
        host=config.host,
        port=config.port,
        use_ssl=config.use_ssl,
        use_starttls=config.use_starttls,
        base_dn=config.base_dn,
        bind_dn=config.bind_dn,
        bind_password="",
        user_filter=config.user_filter,
        username_attr=config.username_attr,
        display_name_attr=config.display_name_attr,
        email_attr=config.email_attr,
        phone_attr=config.phone_attr,
        dept_attr=config.dept_attr,
        default_role_code=config.default_role_code,
        allow_login=config.allow_login,
        auto_create=config.auto_create,
        has_password=bool(config.bind_password),
    )


@router.get("/config", response_model=LdapConfigOut)
def get_config(db: Session = Depends(get_db), _: object = Depends(require_permission("users", "update"))):
    config = get_or_create_config(db)
    return to_out(config)


@router.put("/config", response_model=LdapConfigOut)
def update_config(
    payload: LdapConfigUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("users", "update")),
):
    config = get_or_create_config(db)
    data = payload.model_dump()
    bind_password = data.pop("bind_password", None)
    for key, value in data.items():
        setattr(config, key, value)
    if bind_password:
        config.bind_password = bind_password
    db.commit()
    db.refresh(config)
    return to_out(config)


@router.post("/test", response_model=LdapTestResult)
def test_config(db: Session = Depends(get_db), _: object = Depends(require_permission("users", "update"))):
    config = get_or_create_config(db)
    if not config.host or not config.base_dn:
        raise HTTPException(status_code=400, detail="LDAP config incomplete")
    try:
        entries = search_users(config)
        return LdapTestResult(ok=True, message="LDAP connection ok", users_found=len(entries))
    except Exception as exc:
        return LdapTestResult(ok=False, message=str(exc))


@router.post("/sync", response_model=LdapSyncResult)
def sync_users(db: Session = Depends(get_db), _: object = Depends(require_permission("users", "update"))):
    config = get_or_create_config(db)
    if not config.is_active:
        raise HTTPException(status_code=400, detail="LDAP not enabled")
    if not config.host or not config.base_dn:
        raise HTTPException(status_code=400, detail="LDAP config incomplete")
    role = db.query(Role).filter(Role.code == config.default_role_code).first()
    if not role:
        role = db.query(Role).filter(Role.is_deleted == False).order_by(Role.id.asc()).first()
    if not role:
        raise HTTPException(status_code=400, detail="No default role available")
    try:
        entries = search_users(config)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    created = 0
    updated = 0
    skipped = 0
    for entry in entries:
        username = extract_attr(entry, config.username_attr)
        if not username:
            skipped += 1
            continue
        full_name = extract_attr(entry, config.display_name_attr) or username
        dept = extract_attr(entry, config.dept_attr)
        phone = extract_attr(entry, config.phone_attr)
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(
                username=username,
                full_name=full_name,
                password_hash=hash_password(username),
                role_id=role.id,
                dept=dept,
                phone=phone,
                is_active=True,
                is_deleted=False,
            )
            db.add(user)
            db.commit()
            user.roles = [role]
            db.commit()
            created += 1
            continue
        user.full_name = full_name
        user.dept = dept
        user.phone = phone
        user.is_active = True
        db.commit()
        updated += 1

    return LdapSyncResult(ok=True, created=created, updated=updated, skipped=skipped)
