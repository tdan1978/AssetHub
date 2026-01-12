from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.category import Category
from app.models.category_field import CategoryField
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.category_field import CategoryFieldCreate, CategoryFieldOut, CategoryFieldUpdate, FIELD_TYPES
from app.schemas.common import Message

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), _: object = Depends(require_role("super_admin", "asset_admin"))):
    return db.query(Category).filter(Category.is_deleted == False).order_by(Category.id.desc()).all()


@router.post("", response_model=CategoryOut)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    exists = db.query(Category).filter(Category.name == payload.name, Category.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category exists")
    item = Category(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
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
    item = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    item.is_deleted = True
    db.query(CategoryField).filter(CategoryField.category_id == category_id).update({"is_deleted": True})
    db.commit()
    return Message(message="Deleted")


@router.get("/{category_id}/fields", response_model=list[CategoryFieldOut])
def list_fields(
    category_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    return (
        db.query(CategoryField)
        .filter(CategoryField.category_id == category_id, CategoryField.is_deleted == False)
        .order_by(CategoryField.sort_order.asc(), CategoryField.id.asc())
        .all()
    )


@router.post("/{category_id}/fields", response_model=CategoryFieldOut)
def create_field(
    category_id: int,
    payload: CategoryFieldCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    if payload.field_type not in FIELD_TYPES:
        raise HTTPException(status_code=400, detail="Invalid field type")
    item = CategoryField(category_id=category_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/fields/{field_id}", response_model=CategoryFieldOut)
def update_field(
    field_id: int,
    payload: CategoryFieldUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(CategoryField).filter(CategoryField.id == field_id, CategoryField.is_deleted == False).first()
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
    item = db.query(CategoryField).filter(CategoryField.id == field_id, CategoryField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    item.is_deleted = True
    db.commit()
    return Message(message="Deleted")
