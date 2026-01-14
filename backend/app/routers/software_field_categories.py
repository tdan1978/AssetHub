from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.software_field_category import SoftwareFieldCategory
from app.models.software_field import SoftwareField
from app.schemas.common import Message
from app.schemas.software_field import SoftwareFieldCreate, SoftwareFieldOut, SoftwareFieldUpdate, FIELD_TYPES
from app.schemas.software_field_category import (
    SoftwareFieldCategoryCreate,
    SoftwareFieldCategoryOut,
    SoftwareFieldCategoryUpdate,
    SoftwareFieldCategoryWithFields,
)

router = APIRouter(prefix="/api/v1/software-field-categories", tags=["software-field-categories"])


@router.get("", response_model=list[SoftwareFieldCategoryOut])
def list_categories(db: Session = Depends(get_db), _: object = Depends(require_role("super_admin", "asset_admin"))):
    return (
        db.query(SoftwareFieldCategory)
        .filter(SoftwareFieldCategory.is_deleted == False)
        .order_by(SoftwareFieldCategory.sort_order.asc(), SoftwareFieldCategory.id.asc())
        .all()
    )


@router.get("/tree", response_model=list[SoftwareFieldCategoryWithFields])
def list_category_tree(db: Session = Depends(get_db), _: object = Depends(require_role("super_admin", "asset_admin"))):
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
    _: object = Depends(require_role("super_admin", "asset_admin")),
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
    _: object = Depends(require_role("super_admin", "asset_admin")),
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
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(SoftwareFieldCategory).filter(SoftwareFieldCategory.id == category_id, SoftwareFieldCategory.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    item.is_deleted = True
    db.query(SoftwareField).filter(SoftwareField.category_id == category_id).update({"is_deleted": True})
    db.commit()
    return Message(message="Deleted")


@router.get("/{category_id}/fields", response_model=list[SoftwareFieldOut])
def list_fields(
    category_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    return (
        db.query(SoftwareField)
        .filter(SoftwareField.category_id == category_id, SoftwareField.is_deleted == False)
        .order_by(SoftwareField.sort_order.asc(), SoftwareField.id.asc())
        .all()
    )


@router.post("/{category_id}/fields", response_model=SoftwareFieldOut)
def create_field(
    category_id: int,
    payload: SoftwareFieldCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    if payload.field_type not in FIELD_TYPES:
        raise HTTPException(status_code=400, detail="Invalid field type")
    item = SoftwareField(category_id=category_id, **payload.model_dump(exclude={"category_id"}))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/fields/{field_id}", response_model=SoftwareFieldOut)
def update_field(
    field_id: int,
    payload: SoftwareFieldUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(SoftwareField).filter(SoftwareField.id == field_id, SoftwareField.is_deleted == False).first()
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
    item = db.query(SoftwareField).filter(SoftwareField.id == field_id, SoftwareField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    item.is_deleted = True
    db.commit()
    return Message(message="Deleted")
