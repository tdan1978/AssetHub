from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.system_field_category import SystemFieldCategory
from app.models.system_field import SystemField
from app.models.system_field_value import SystemFieldValue
from app.schemas.common import Message
from app.schemas.system_field import SystemFieldCreate, SystemFieldOut, SystemFieldUpdate, FIELD_TYPES
from app.schemas.system_field_category import (
    SystemFieldCategoryCreate,
    SystemFieldCategoryOut,
    SystemFieldCategoryUpdate,
    SystemFieldCategoryWithFields,
)

router = APIRouter(prefix="/api/v1/system-field-categories", tags=["system-field-categories"])


def normalize_select_config(data: dict):
    field_type = data.get("field_type")
    if field_type == "combo_select":
        data["field_type"] = "single_select"
        data["searchable"] = True
    current_type = data.get("field_type")
    if current_type not in ("single_select", "multi_select"):
        data["searchable"] = False


@router.get("", response_model=list[SystemFieldCategoryOut])
def list_categories(db: Session = Depends(get_db), _: object = Depends(require_permission("system_fields", "view"))):
    return (
        db.query(SystemFieldCategory)
        .filter(SystemFieldCategory.is_deleted == False)
        .order_by(SystemFieldCategory.sort_order.asc(), SystemFieldCategory.id.asc())
        .all()
    )


@router.get("/tree", response_model=list[SystemFieldCategoryWithFields])
def list_category_tree(db: Session = Depends(get_db), _: object = Depends(require_permission("system_fields", "view"))):
    categories = (
        db.query(SystemFieldCategory)
        .filter(SystemFieldCategory.is_deleted == False)
        .order_by(SystemFieldCategory.sort_order.asc(), SystemFieldCategory.id.asc())
        .all()
    )
    for category in categories:
        category.fields = (
            db.query(SystemField)
            .filter(SystemField.category_id == category.id, SystemField.is_deleted == False)
            .order_by(SystemField.sort_order.asc(), SystemField.id.asc())
            .all()
        )
    return categories


@router.post("", response_model=SystemFieldCategoryOut)
def create_category(
    payload: SystemFieldCategoryCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_fields", "create")),
):
    exists = db.query(SystemFieldCategory).filter(SystemFieldCategory.name == payload.name, SystemFieldCategory.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category exists")
    item = SystemFieldCategory(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{category_id}", response_model=SystemFieldCategoryOut)
def update_category(
    category_id: int,
    payload: SystemFieldCategoryUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_fields", "update")),
):
    item = db.query(SystemFieldCategory).filter(SystemFieldCategory.id == category_id, SystemFieldCategory.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{category_id}", response_model=Message)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_fields", "delete")),
):
    item = db.query(SystemFieldCategory).filter(SystemFieldCategory.id == category_id, SystemFieldCategory.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    has_builtin = (
        db.query(SystemField.id)
        .filter(
            SystemField.category_id == category_id,
            SystemField.is_deleted == False,
            SystemField.is_builtin == True,
        )
        .first()
    )
    if has_builtin:
        raise HTTPException(status_code=400, detail="Built-in fields cannot be deleted")
    field_ids = [
        row[0]
        for row in db.query(SystemField.id).filter(SystemField.category_id == category_id).all()
    ]
    if field_ids:
        db.query(SystemFieldValue).filter(SystemFieldValue.field_id.in_(field_ids)).delete(synchronize_session=False)
    db.query(SystemField).filter(SystemField.category_id == category_id).delete(synchronize_session=False)
    db.delete(item)
    db.commit()
    return Message(message="Deleted")


@router.get("/{category_id}/fields", response_model=list[SystemFieldOut])
def list_fields(
    category_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_fields", "view")),
):
    fields = (
        db.query(SystemField)
        .filter(SystemField.category_id == category_id, SystemField.is_deleted == False)
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


@router.post("/{category_id}/fields", response_model=SystemFieldOut)
def create_field(
    category_id: int,
    payload: SystemFieldCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("system_fields", "create")),
):
    if payload.field_type not in FIELD_TYPES and payload.field_type != "combo_select":
        raise HTTPException(status_code=400, detail="Invalid field type")
    data = payload.model_dump(exclude={"category_id"})
    normalize_select_config(data)
    item = SystemField(category_id=category_id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/fields/{field_id}", response_model=SystemFieldOut)
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


@router.delete("/fields/{field_id}", response_model=Message)
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
