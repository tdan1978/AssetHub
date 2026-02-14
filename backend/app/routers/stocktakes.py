from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.stocktake import Stocktake, StocktakeItem
from app.models.asset import Asset
from app.schemas.stocktake import StocktakeCreate, StocktakeOut
from app.schemas.common import Message

router = APIRouter(prefix="/api/v1/stocktakes", tags=["stocktakes"])


@router.get("", response_model=list[StocktakeOut])
def list_stocktakes(db: Session = Depends(get_db), _: object = Depends(require_permission("stocktakes", "view"))):
    return db.query(Stocktake).order_by(Stocktake.id.desc()).all()


@router.post("", response_model=StocktakeOut)
def create_stocktake(
    payload: StocktakeCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("stocktakes", "create")),
):
    task = Stocktake(name=payload.name, scope=payload.scope, created_by=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)

    assets = db.query(Asset).filter(Asset.is_deleted == False).all()
    for asset in assets:
        db.add(StocktakeItem(stocktake_id=task.id, asset_id=asset.id))
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=StocktakeOut)
def update_stocktake(
    task_id: int,
    payload: StocktakeCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("stocktakes", "update")),
):
    task = db.query(Stocktake).filter(Stocktake.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.name = payload.name
    task.scope = payload.scope
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=StocktakeOut)
def get_stocktake(task_id: int, db: Session = Depends(get_db), _: object = Depends(require_permission("stocktakes", "view"))):
    task = db.query(Stocktake).filter(Stocktake.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", response_model=Message)
def delete_stocktake(
    task_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("stocktakes", "update")),
):
    task = db.query(Stocktake).filter(Stocktake.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return Message(message="Deleted")


@router.post("/{task_id}/scan")
def scan_asset(
    task_id: int,
    asset_id: int,
    status: str = "normal",
    note: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("stocktakes", "update")),
):
    item = db.query(StocktakeItem).filter(StocktakeItem.stocktake_id == task_id, StocktakeItem.asset_id == asset_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = status
    item.note = note
    item.scanned_at = datetime.utcnow()
    db.commit()
    return {"message": "Scanned"}


@router.get("/{task_id}/progress")
def stocktake_progress(task_id: int, db: Session = Depends(get_db), _: object = Depends(require_permission("stocktakes", "view"))):
    total = db.query(StocktakeItem).filter(StocktakeItem.stocktake_id == task_id).count()
    scanned = db.query(StocktakeItem).filter(StocktakeItem.stocktake_id == task_id, StocktakeItem.scanned_at != None).count()
    return {"total": total, "scanned": scanned, "missing": total - scanned}
