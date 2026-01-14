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
    if payload.app_code:
        exists = (
            db.query(SystemApp)
            .filter(SystemApp.app_code == payload.app_code, SystemApp.is_deleted == False)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="System code exists")
    item = SystemApp(**payload.model_dump())
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
    if "app_code" in data and data["app_code"]:
        exists = (
            db.query(SystemApp)
            .filter(
                SystemApp.app_code == data["app_code"],
                SystemApp.id != system_id,
                SystemApp.is_deleted == False,
            )
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="System code exists")
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
