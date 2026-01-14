from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.system_field_category import SystemFieldCategory
from app.models.system_field import SystemField
from app.schemas.common import Message
from app.schemas.system_field import SystemFieldCreate, SystemFieldOut, SystemFieldUpdate, FIELD_TYPES
from app.schemas.system_field_category import (
    SystemFieldCategoryCreate,
    SystemFieldCategoryOut,
    SystemFieldCategoryUpdate,
    SystemFieldCategoryWithFields,
)

router = APIRouter(prefix="/api/v1/system-field-categories", tags=["system-field-categories"])


@router.get("", response_model=list[SystemFieldCategoryOut])
def list_categories(db: Session = Depends(get_db), _: object = Depends(require_role("super_admin", "asset_admin"))):
    return (
        db.query(SystemFieldCategory)
        .filter(SystemFieldCategory.is_deleted == False)
        .order_by(SystemFieldCategory.sort_order.asc(), SystemFieldCategory.id.asc())
        .all()
    )


@router.get("/tree", response_model=list[SystemFieldCategoryWithFields])
def list_category_tree(db: Session = Depends(get_db), _: object = Depends(require_role("super_admin", "asset_admin"))):
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
    _: object = Depends(require_role("super_admin", "asset_admin")),
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
    _: object = Depends(require_role("super_admin", "asset_admin")),
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
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(SystemFieldCategory).filter(SystemFieldCategory.id == category_id, SystemFieldCategory.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    item.is_deleted = True
    db.query(SystemField).filter(SystemField.category_id == category_id).update({"is_deleted": True})
    db.commit()
    return Message(message="Deleted")


@router.get("/{category_id}/fields", response_model=list[SystemFieldOut])
def list_fields(
    category_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    return (
        db.query(SystemField)
        .filter(SystemField.category_id == category_id, SystemField.is_deleted == False)
        .order_by(SystemField.sort_order.asc(), SystemField.id.asc())
        .all()
    )


@router.post("/{category_id}/fields", response_model=SystemFieldOut)
def create_field(
    category_id: int,
    payload: SystemFieldCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    if payload.field_type not in FIELD_TYPES:
        raise HTTPException(status_code=400, detail="Invalid field type")
    item = SystemField(category_id=category_id, **payload.model_dump(exclude={"category_id"}))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/fields/{field_id}", response_model=SystemFieldOut)
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


@router.delete("/fields/{field_id}", response_model=Message)
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
