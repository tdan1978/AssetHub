from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.deps import require_permission, get_permission_scope
from app.models.system_app import SystemApp
from app.models.system_field import SystemField
from app.models.user import User
from app.models.system_field_value import SystemFieldValue
from app.schemas.common import Page, Message
from app.schemas.system_app import SystemAppCreate, SystemAppOut, SystemAppUpdate
from app.schemas.system_field_value import SystemFieldValueIn, SystemFieldValueOut
from app.utils.pagination import paginate


def resolve_system_prefix(app_category: str | None) -> str:
    if not app_category:
        return "SYS"
    mapping = {
        "业务系统": "BUS",
        "工具系统": "TOOL",
        "中间件": "MID",
        "内部平台": "PLAT",
    }
    if app_category in mapping:
        return mapping[app_category]
    cleaned = "".join(ch for ch in app_category if ch.isalnum()).upper()
    return cleaned[:6] if cleaned else "SYS"


def generate_system_code(db: Session, prefix: str) -> str:
    base = f"{prefix}-"
    candidates = db.query(SystemApp.app_code).filter(SystemApp.app_code.like(f"{base}%")).all()
    max_seq = 0
    for (code,) in candidates:
        if not code or not code.startswith(base):
            continue
        tail = code.replace(base, "", 1)
        if tail.isdigit():
            max_seq = max(max_seq, int(tail))
    return f"{base}{max_seq + 1:06d}"

router = APIRouter(prefix="/api/v1/systems", tags=["systems"])

LEGACY_SYNC_FIELD_KEYS = {
    "access_url",
    "app_category",
    "arch_type",
    "db_type",
    "deploy_type",
    "repo_url",
    "sec_level",
}


def split_owners(value: str | None) -> list[str]:
    if not value:
        return []
    separators = [",", "，", ";", "；", "/", "、", "|"]
    result = [value]
    for sep in separators:
        next_list = []
        for item in result:
            next_list.extend(item.split(sep))
        result = next_list
    return [item.strip() for item in result if item and item.strip()]


def owner_ids(value: str | None) -> list[str]:
    return [token for token in split_owners(value) if token.isdigit()]


def normalize_owner_value(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text


def build_owner_name_map(db: Session, systems: list[SystemApp]) -> dict[str, str]:
    ids: set[int] = set()
    for system in systems:
        for token in owner_ids(system.ops_owner):
            ids.add(int(token))
        for token in owner_ids(system.ops_owner_b):
            ids.add(int(token))
    if not ids:
        return {}
    users = (
        db.query(User.id, User.full_name, User.username)
        .filter(User.id.in_(ids), User.is_deleted == False)
        .all()
    )
    return {str(item.id): (item.full_name or item.username or str(item.id)) for item in users}


def owner_display(value: str | None, owner_map: dict[str, str]) -> str | None:
    tokens = split_owners(value)
    if not tokens:
        return None
    display_values = []
    for token in tokens:
        display_values.append(owner_map.get(token, token))
    return " / ".join(display_values) if display_values else None


def to_system_out(system: SystemApp, owner_map: dict[str, str]) -> SystemAppOut:
    return SystemAppOut.model_validate(
        {
            "id": system.id,
            "app_name": system.app_name,
            "app_code": system.app_code,
            "app_status": system.app_status,
            "access_url": system.access_url,
            "app_category": system.app_category,
            "arch_type": system.arch_type,
            "dev_lang": system.dev_lang,
            "db_type": system.db_type,
            "deploy_type": system.deploy_type,
            "repo_url": system.repo_url,
            "biz_owner": system.biz_owner,
            "tech_owner": system.tech_owner,
            "ops_owner": system.ops_owner,
            "ops_owner_b": system.ops_owner_b,
            "sec_level": system.sec_level,
            "ops_owner_name": owner_display(system.ops_owner, owner_map),
            "ops_owner_b_name": owner_display(system.ops_owner_b, owner_map),
        }
    )


def user_is_ops_owner(user, system: SystemApp) -> bool:
    tokens = split_owners(system.ops_owner) + split_owners(system.ops_owner_b)
    if not tokens:
        return False
    user_id = str(user.id)
    if user_id in tokens:
        return True
    candidates = {user.username, user_id}
    if user.full_name:
        candidates.add(user.full_name)
    return any(token in candidates for token in tokens)


def get_role_codes(user) -> set[str]:
    codes: set[str] = set()
    if getattr(user, "role", None) and getattr(user.role, "is_active", False):
        code = getattr(user.role, "code", None)
        if code:
            codes.add(code)
    if getattr(user, "roles", None):
        for role in user.roles:
            if getattr(role, "is_active", False):
                code = getattr(role, "code", None)
                if code:
                    codes.add(code)
    return codes


def can_manage_ops_owners(user) -> bool:
    role_codes = get_role_codes(user)
    return "super_admin" in role_codes or "system_admin" in role_codes


@router.get("/options")
def list_system_options(
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_assets", "view")),
):
    query = db.query(SystemApp.id, SystemApp.app_name, SystemApp.app_code).filter(SystemApp.is_deleted == False)
    items = (
        query.order_by(SystemApp.id.desc()).all()
    )
    return [
        {
            "value": item.id,
            "label": item.app_name or item.app_code or str(item.id),
        }
        for item in items
    ]


@router.get("", response_model=Page[SystemAppOut])
def list_systems(
    page: int = 1,
    size: int = 20,
    q: str | None = None,
    app_status: str | None = None,
    db: Session = Depends(get_db),
    user: object = Depends(require_permission("system_assets", "view")),
):
    query = db.query(SystemApp).filter(SystemApp.is_deleted == False)
    scope = get_permission_scope(db, user, "system_assets", "view")
    if scope == "own":
        uid = str(user.id)
        query = query.filter(or_(SystemApp.ops_owner == uid, SystemApp.ops_owner_b == uid))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(SystemApp.app_name.like(like), SystemApp.app_code.like(like)))
    if app_status:
        query = query.filter(SystemApp.app_status == app_status)
    total, items = paginate(query.order_by(SystemApp.id.desc()), page, size)
    owner_map = build_owner_name_map(db, items)
    return Page(total=total, items=[to_system_out(item, owner_map) for item in items])


@router.get("/{system_id}", response_model=SystemAppOut)
def get_system(
    system_id: int,
    db: Session = Depends(get_db),
    user: object = Depends(require_permission("system_assets", "view")),
):
    system = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    scope = get_permission_scope(db, user, "system_assets", "view")
    if scope == "own" and not user_is_ops_owner(user, system):
        raise HTTPException(status_code=403, detail="Forbidden")
    owner_map = build_owner_name_map(db, [system])
    return to_system_out(system, owner_map)


@router.post("", response_model=SystemAppOut)
def create_system(
    payload: SystemAppCreate,
    db: Session = Depends(get_db),
    user: object = Depends(require_permission("system_assets", "create")),
):
    prefix = resolve_system_prefix(payload.app_category)
    payload_data = payload.model_dump()
    payload_data["ops_owner"] = normalize_owner_value(payload_data.get("ops_owner"))
    payload_data["ops_owner_b"] = normalize_owner_value(payload_data.get("ops_owner_b"))
    if not can_manage_ops_owners(user) and (payload_data.get("ops_owner") or payload_data.get("ops_owner_b")):
        raise HTTPException(status_code=403, detail="Only system admins can modify ops owners")
    payload_data["app_code"] = generate_system_code(db, prefix)
    item = SystemApp(**payload_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    owner_map = build_owner_name_map(db, [item])
    return to_system_out(item, owner_map)


@router.put("/{system_id}", response_model=SystemAppOut)
def update_system(
    system_id: int,
    payload: SystemAppUpdate,
    db: Session = Depends(get_db),
    user: object = Depends(require_permission("system_assets", "update")),
):
    item = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="System not found")
    scope = get_permission_scope(db, user, "system_assets", "update")
    if scope == "own" and not user_is_ops_owner(user, item):
        raise HTTPException(status_code=403, detail="Forbidden")
    data = payload.model_dump(exclude_unset=True)
    data.pop("app_code", None)
    if "ops_owner" in data:
        data["ops_owner"] = normalize_owner_value(data.get("ops_owner"))
    if "ops_owner_b" in data:
        data["ops_owner_b"] = normalize_owner_value(data.get("ops_owner_b"))
    if not can_manage_ops_owners(user):
        if "ops_owner" in data and data["ops_owner"] != item.ops_owner:
            raise HTTPException(status_code=403, detail="Only system admins can modify ops owners")
        if "ops_owner_b" in data and data["ops_owner_b"] != item.ops_owner_b:
            raise HTTPException(status_code=403, detail="Only system admins can modify ops owners")
    if "app_category" in data and data["app_category"] != item.app_category:
        prefix = resolve_system_prefix(data["app_category"])
        data["app_code"] = generate_system_code(db, prefix)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    owner_map = build_owner_name_map(db, [item])
    return to_system_out(item, owner_map)


@router.delete("/{system_id}", response_model=Message)
def delete_system(
    system_id: int,
    db: Session = Depends(get_db),
    user: object = Depends(require_permission("system_assets", "delete")),
):
    item = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="System not found")
    scope = get_permission_scope(db, user, "system_assets", "delete")
    if scope == "own" and not user_is_ops_owner(user, item):
        raise HTTPException(status_code=403, detail="Forbidden")
    # Hard delete: remove related custom field values first to satisfy FK constraints.
    db.query(SystemFieldValue).filter(SystemFieldValue.system_id == system_id).delete(synchronize_session=False)
    db.delete(item)
    db.commit()
    return Message(message="Deleted")


@router.get("/{system_id}/fields", response_model=list[SystemFieldValueOut])
def list_system_fields(
    system_id: int,
    db: Session = Depends(get_db),
    user: object = Depends(require_permission("system_assets", "view")),
):
    system = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    scope = get_permission_scope(db, user, "system_assets", "view")
    if scope == "own" and not user_is_ops_owner(user, system):
        raise HTTPException(status_code=403, detail="Forbidden")
    return db.query(SystemFieldValue).filter(SystemFieldValue.system_id == system_id).all()


@router.put("/{system_id}/fields", response_model=list[SystemFieldValueOut])
def upsert_system_fields(
    system_id: int,
    payload: list[SystemFieldValueIn],
    db: Session = Depends(get_db),
    user: object = Depends(require_permission("system_assets", "update")),
):
    system = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    scope = get_permission_scope(db, user, "system_assets", "update")
    if scope == "own" and not user_is_ops_owner(user, system):
        raise HTTPException(status_code=403, detail="Forbidden")

    existing = {
        item.field_id: item
        for item in db.query(SystemFieldValue).filter(SystemFieldValue.system_id == system_id).all()
    }
    field_ids = [item.field_id for item in payload]
    field_map = {}
    if field_ids:
        fields = db.query(SystemField.id, SystemField.field_key).filter(SystemField.id.in_(field_ids)).all()
        field_map = {item.id: item.field_key for item in fields}
    for item in payload:
        if item.field_id in existing:
            existing[item.field_id].value = item.value
        else:
            db.add(SystemFieldValue(system_id=system_id, field_id=item.field_id, value=item.value))
        field_key = field_map.get(item.field_id)
        if field_key in LEGACY_SYNC_FIELD_KEYS:
            value = item.value
            if isinstance(value, list):
                value = "，".join([str(v) for v in value if str(v).strip() != ""])
            if value is not None:
                text = str(value).strip()
                setattr(system, field_key, text if text else None)
            else:
                setattr(system, field_key, None)
    db.commit()
    return db.query(SystemFieldValue).filter(SystemFieldValue.system_id == system_id).all()
