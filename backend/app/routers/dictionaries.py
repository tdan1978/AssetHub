from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.dict_type import DictType
from app.models.dict_item import DictItem
from app.schemas.dictionary import (
    DictTypeCreate,
    DictTypeOut,
    DictTypeUpdate,
    DictItemCreate,
    DictItemOut,
    DictItemUpdate,
)

router = APIRouter(prefix="/api/v1/dictionaries", tags=["dictionaries"])

ALLOWED_SCOPES = {"global", "office", "datacenter", "software", "system"}


@router.get("/types", response_model=list[DictTypeOut])
def list_types(
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dictionaries", "view")),
):
    return (
        db.query(DictType)
        .filter(DictType.is_deleted == False)
        .order_by(DictType.sort_order.asc(), DictType.id.asc())
        .all()
    )


@router.post("/types", response_model=DictTypeOut)
def create_type(
    payload: DictTypeCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dictionaries", "create")),
):
    if payload.scope not in ALLOWED_SCOPES:
        raise HTTPException(status_code=400, detail="Invalid scope")
    exists = db.query(DictType).filter(DictType.code == payload.code, DictType.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="Code already exists")
    item = DictType(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/types/{type_id}", response_model=DictTypeOut)
def update_type(
    type_id: int,
    payload: DictTypeUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dictionaries", "update")),
):
    item = db.query(DictType).filter(DictType.id == type_id, DictType.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Type not found")
    data = payload.model_dump(exclude_unset=True)
    if "code" in data and data["code"] != item.code:
        exists = db.query(DictType).filter(DictType.code == data["code"], DictType.is_deleted == False).first()
        if exists:
            raise HTTPException(status_code=400, detail="Code already exists")
    if "scope" in data and data["scope"] not in ALLOWED_SCOPES:
        raise HTTPException(status_code=400, detail="Invalid scope")
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/types/{type_id}")
def delete_type(
    type_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dictionaries", "delete")),
):
    item = db.query(DictType).filter(DictType.id == type_id, DictType.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Type not found")
    db.query(DictItem).filter(DictItem.type_id == type_id).delete(synchronize_session=False)
    db.delete(item)
    db.commit()
    return {"message": "deleted"}


@router.get("/items", response_model=list[DictItemOut])
def list_items(
    type: str | None = Query(None),
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dictionaries", "view")),
):
    query = db.query(DictItem).filter(DictItem.is_deleted == False)
    if type:
        if type.isdigit():
            query = query.filter(DictItem.type_id == int(type))
        else:
            dtype = db.query(DictType).filter(DictType.code == type, DictType.is_deleted == False).first()
            if not dtype:
                return []
            query = query.filter(DictItem.type_id == dtype.id)
    return query.order_by(DictItem.sort_order.asc(), DictItem.id.asc()).all()


@router.post("/items", response_model=DictItemOut)
def create_item(
    payload: DictItemCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dictionaries", "create")),
):
    dtype = db.query(DictType).filter(DictType.id == payload.type_id, DictType.is_deleted == False).first()
    if not dtype:
        raise HTTPException(status_code=400, detail="Type not found")
    exists = (
        db.query(DictItem)
        .filter(DictItem.type_id == payload.type_id, DictItem.name == payload.name, DictItem.is_deleted == False)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Item already exists")
    item = DictItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=DictItemOut)
def update_item(
    item_id: int,
    payload: DictItemUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dictionaries", "update")),
):
    item = db.query(DictItem).filter(DictItem.id == item_id, DictItem.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] != item.name:
        exists = (
            db.query(DictItem)
            .filter(DictItem.type_id == item.type_id, DictItem.name == data["name"], DictItem.is_deleted == False)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="Item already exists")
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dictionaries", "delete")),
):
    item = db.query(DictItem).filter(DictItem.id == item_id, DictItem.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "deleted"}
