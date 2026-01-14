from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.system_field import SystemField
from app.schemas.system_field import SystemFieldCreate, SystemFieldOut, SystemFieldUpdate, FIELD_TYPES
from app.schemas.common import Message

router = APIRouter(prefix="/api/v1/system-fields", tags=["system-fields"])


@router.get("", response_model=list[SystemFieldOut])
def list_fields(db: Session = Depends(get_db), _: object = Depends(require_role("super_admin", "asset_admin"))):
    return (
        db.query(SystemField)
        .filter(SystemField.is_deleted == False)
        .order_by(SystemField.sort_order.asc(), SystemField.id.asc())
        .all()
    )


@router.post("", response_model=SystemFieldOut)
def create_field(
    payload: SystemFieldCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    if payload.field_type not in FIELD_TYPES:
        raise HTTPException(status_code=400, detail="Invalid field type")
    item = SystemField(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{field_id}", response_model=SystemFieldOut)
def update_field(
    field_id: int,
    payload: SystemFieldUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(SystemField).filter(SystemField.id == field_id, SystemField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    data = payload.model_dump(exclude_unset=True)
    if "field_type" in data and data["field_type"] not in FIELD_TYPES:
        raise HTTPException(status_code=400, detail="Invalid field type")
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{field_id}", response_model=Message)
def delete_field(
    field_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(SystemField).filter(SystemField.id == field_id, SystemField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    item.is_deleted = True
    db.commit()
    return Message(message="Deleted")
