from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.system_app import SystemApp
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
    return f"{base}{max_seq + 1:04d}"

router = APIRouter(prefix="/api/v1/systems", tags=["systems"])


@router.get("", response_model=Page[SystemAppOut])
def list_systems(
    page: int = 1,
    size: int = 20,
    q: str | None = None,
    app_status: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    query = db.query(SystemApp).filter(SystemApp.is_deleted == False)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(SystemApp.app_name.like(like), SystemApp.app_code.like(like)))
    if app_status:
        query = query.filter(SystemApp.app_status == app_status)
    total, items = paginate(query.order_by(SystemApp.id.desc()), page, size)
    return Page(total=total, items=items)


@router.get("/{system_id}", response_model=SystemAppOut)
def get_system(
    system_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    system = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return system


@router.post("", response_model=SystemAppOut)
def create_system(
    payload: SystemAppCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    prefix = resolve_system_prefix(payload.app_category)
    payload_data = payload.model_dump()
    payload_data["app_code"] = generate_system_code(db, prefix)
    item = SystemApp(**payload_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{system_id}", response_model=SystemAppOut)
def update_system(
    system_id: int,
    payload: SystemAppUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="System not found")
    data = payload.model_dump(exclude_unset=True)
    data.pop("app_code", None)
    if "app_category" in data and data["app_category"] != item.app_category:
        prefix = resolve_system_prefix(data["app_category"])
        data["app_code"] = generate_system_code(db, prefix)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{system_id}", response_model=Message)
def delete_system(
    system_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="System not found")
    item.is_deleted = True
    db.commit()
    return Message(message="Deleted")


@router.get("/{system_id}/fields", response_model=list[SystemFieldValueOut])
def list_system_fields(
    system_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    system = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return db.query(SystemFieldValue).filter(SystemFieldValue.system_id == system_id).all()


@router.put("/{system_id}/fields", response_model=list[SystemFieldValueOut])
def upsert_system_fields(
    system_id: int,
    payload: list[SystemFieldValueIn],
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    system = db.query(SystemApp).filter(SystemApp.id == system_id, SystemApp.is_deleted == False).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    existing = {
        item.field_id: item
        for item in db.query(SystemFieldValue).filter(SystemFieldValue.system_id == system_id).all()
    }
    for item in payload:
        if item.field_id in existing:
            existing[item.field_id].value = item.value
        else:
            db.add(SystemFieldValue(system_id=system_id, field_id=item.field_id, value=item.value))
    db.commit()
    return db.query(SystemFieldValue).filter(SystemFieldValue.system_id == system_id).all()
