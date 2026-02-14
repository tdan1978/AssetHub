from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.software_field_category import SoftwareFieldCategory
from app.models.software_field import SoftwareField
from app.models.software_field_value import SoftwareFieldValue
from app.models.license import License
from app.schemas.common import Message
from app.schemas.software_field import SoftwareFieldCreate, SoftwareFieldOut, SoftwareFieldUpdate, FIELD_TYPES
from app.schemas.software_field_category import (
    SoftwareFieldCategoryCreate,
    SoftwareFieldCategoryOut,
    SoftwareFieldCategoryUpdate,
    SoftwareFieldCategoryWithFields,
)

router = APIRouter(prefix="/api/v1/software-field-categories", tags=["software-field-categories"])


def normalize_select_config(data: dict):
    field_type = data.get("field_type")
    if field_type == "combo_select":
        data["field_type"] = "single_select"
        data["searchable"] = True
    current_type = data.get("field_type")
    if current_type not in ("single_select", "multi_select"):
        data["searchable"] = False


@router.get("", response_model=list[SoftwareFieldCategoryOut])
def list_categories(db: Session = Depends(get_db), _: object = Depends(require_permission("software_fields", "view"))):
    return (
        db.query(SoftwareFieldCategory)
        .filter(SoftwareFieldCategory.is_deleted == False)
        .order_by(SoftwareFieldCategory.sort_order.asc(), SoftwareFieldCategory.id.asc())
        .all()
    )


@router.get("/tree", response_model=list[SoftwareFieldCategoryWithFields])
def list_category_tree(db: Session = Depends(get_db), _: object = Depends(require_permission("software_fields", "view"))):
    categories = (
        db.query(SoftwareFieldCategory)
        .filter(SoftwareFieldCategory.is_deleted == False)
        .order_by(SoftwareFieldCategory.sort_order.asc(), SoftwareFieldCategory.id.asc())
        .all()
    )
    for category in categories:
        category.fields = (
            db.query(SoftwareField)
            .filter(SoftwareField.category_id == category.id, SoftwareField.is_deleted == False)
            .order_by(SoftwareField.sort_order.asc(), SoftwareField.id.asc())
            .all()
        )
    return categories


@router.post("", response_model=SoftwareFieldCategoryOut)
def create_category(
    payload: SoftwareFieldCategoryCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("software_fields", "create")),
):
    exists = (
        db.query(SoftwareFieldCategory)
        .filter(SoftwareFieldCategory.name == payload.name, SoftwareFieldCategory.is_deleted == False)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Category exists")
    item = SoftwareFieldCategory(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{category_id}", response_model=SoftwareFieldCategoryOut)
def update_category(
    category_id: int,
    payload: SoftwareFieldCategoryUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("software_fields", "update")),
):
    item = db.query(SoftwareFieldCategory).filter(SoftwareFieldCategory.id == category_id, SoftwareFieldCategory.is_deleted == False).first()
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
    _: object = Depends(require_permission("software_fields", "delete")),
):
    item = db.query(SoftwareFieldCategory).filter(SoftwareFieldCategory.id == category_id, SoftwareFieldCategory.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    field_ids = [
        row[0]
        for row in db.query(SoftwareField.id).filter(SoftwareField.category_id == category_id).all()
    ]
    if field_ids:
        db.query(SoftwareFieldValue).filter(SoftwareFieldValue.field_id.in_(field_ids)).delete(synchronize_session=False)
    db.query(SoftwareField).filter(SoftwareField.category_id == category_id).delete(synchronize_session=False)
    db.delete(item)
    db.commit()
    return Message(message="Deleted")


@router.get("/{category_id}/fields", response_model=list[SoftwareFieldOut])
def list_fields(
    category_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("software_fields", "view")),
):
    fields = (
        db.query(SoftwareField)
        .filter(SoftwareField.category_id == category_id, SoftwareField.is_deleted == False)
        .order_by(SoftwareField.sort_order.asc(), SoftwareField.id.asc())
        .all()
    )
    if not fields:
        return fields
    field_ids = [item.id for item in fields]
    counts = dict(
        db.query(SoftwareFieldValue.field_id, func.count(1))
        .filter(SoftwareFieldValue.field_id.in_(field_ids))
        .group_by(SoftwareFieldValue.field_id)
        .all()
    )
    for item in fields:
        item.in_use = item.id in counts
    return fields


@router.post("/{category_id}/fields", response_model=SoftwareFieldOut)
def create_field(
    category_id: int,
    payload: SoftwareFieldCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("software_fields", "create")),
):
    if payload.field_type not in FIELD_TYPES and payload.field_type != "combo_select":
        raise HTTPException(status_code=400, detail="Invalid field type")
    data = payload.model_dump(exclude={"category_id"})
    normalize_select_config(data)
    item = SoftwareField(category_id=category_id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/fields/{field_id}", response_model=SoftwareFieldOut)
def update_field(
    field_id: int,
    payload: SoftwareFieldUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("software_fields", "update")),
):
    item = db.query(SoftwareField).filter(SoftwareField.id == field_id, SoftwareField.is_deleted == False).first()
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
    _: object = Depends(require_permission("software_fields", "delete")),
):
    item = db.query(SoftwareField).filter(SoftwareField.id == field_id, SoftwareField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    in_use = (
        db.query(SoftwareFieldValue.id)
        .filter(SoftwareFieldValue.field_id == item.id)
        .first()
    )
    if not in_use and hasattr(License, item.field_key):
        in_use = (
            db.query(License.id)
            .filter(getattr(License, item.field_key) != None)
            .first()
        )
    if in_use:
        raise HTTPException(status_code=400, detail="Field is in use")
    db.delete(item)
    db.commit()
    return Message(message="Deleted")
