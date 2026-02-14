from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.system_field import SystemField
from app.models.system_field_value import SystemFieldValue
from app.schemas.system_field import SystemFieldCreate, SystemFieldOut, SystemFieldUpdate, FIELD_TYPES
from app.schemas.common import Message

router = APIRouter(prefix="/api/v1/system-fields", tags=["system-fields"])


def normalize_select_config(data: dict):
    field_type = data.get("field_type")
    if field_type == "combo_select":
        data["field_type"] = "single_select"
        data["searchable"] = True
    current_type = data.get("field_type")
    if current_type not in ("single_select", "multi_select"):
        data["searchable"] = False


@router.get("", response_model=list[SystemFieldOut])
def list_fields(db: Session = Depends(get_db), _: object = Depends(require_permission("system_fields", "view"))):
    fields = (
        db.query(SystemField)
        .filter(SystemField.is_deleted == False)
        .order_by(SystemField.sort_order.asc(), SystemField.id.asc())
        .all()
    )
    if not fields:
        return fields
    field_ids = [item.id for item in fields]
    counts = dict(
        db.query(SystemFieldValue.field_id, func.count(1))
        .filter(SystemFieldValue.field_id.in_(field_ids))
        .group_by(SystemFieldValue.field_id)
        .all()
    )
    for item in fields:
        item.in_use = item.id in counts
    return fields


@router.post("", response_model=SystemFieldOut)
def create_field(
    payload: SystemFieldCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_fields", "create")),
):
    if payload.field_type not in FIELD_TYPES and payload.field_type != "combo_select":
        raise HTTPException(status_code=400, detail="Invalid field type")
    data = payload.model_dump()
    normalize_select_config(data)
    item = SystemField(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{field_id}", response_model=SystemFieldOut)
def update_field(
    field_id: int,
    payload: SystemFieldUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_fields", "update")),
):
    item = db.query(SystemField).filter(SystemField.id == field_id, SystemField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    data = payload.model_dump(exclude_unset=True)
    if "field_type" in data and data["field_type"] not in FIELD_TYPES and data["field_type"] != "combo_select":
        raise HTTPException(status_code=400, detail="Invalid field type")
    normalize_select_config(data)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{field_id}", response_model=Message)
def delete_field(
    field_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_fields", "delete")),
):
    item = db.query(SystemField).filter(SystemField.id == field_id, SystemField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    if item.is_builtin:
        raise HTTPException(status_code=400, detail="Built-in field cannot be deleted")
    in_use = (
        db.query(SystemFieldValue.id)
        .filter(SystemFieldValue.field_id == item.id)
        .first()
    )
    if in_use:
        raise HTTPException(status_code=400, detail="Field is in use")
    db.delete(item)
    db.commit()
    return Message(message="Deleted")
