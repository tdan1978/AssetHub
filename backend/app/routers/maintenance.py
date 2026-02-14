from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.asset import Asset
from app.models.asset_log import AssetLog
from app.models.maintenance import MaintenanceInfo, RepairRecord
from app.schemas.maintenance import (
    MaintenanceInfoCreate,
    MaintenanceInfoOut,
    MaintenanceInfoUpdate,
    RepairRecordCreate,
    RepairRecordOut,
    RepairRecordUpdate,
)
from app.schemas.common import Message

router = APIRouter(prefix="/api/v1/maintenance", tags=["maintenance"])


def log_change(db: Session, asset_id: int, operator_id: int, action_type: str, change_data: dict):
    db.add(
        AssetLog(
            asset_id=asset_id,
            operator_id=operator_id,
            action_type=action_type,
            change_data=change_data,
            created_at=datetime.utcnow(),
        )
    )


@router.get("/repairs", response_model=list[RepairRecordOut])
def list_repairs(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("maintenance", "view")),
):
    query = db.query(RepairRecord).filter(RepairRecord.is_deleted == False)
    if status:
        query = query.filter(RepairRecord.status == status)
    return query.order_by(RepairRecord.id.desc()).all()


@router.get("/repairs/{repair_id}", response_model=RepairRecordOut)
def get_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("maintenance", "view")),
):
    record = db.query(RepairRecord).filter(RepairRecord.id == repair_id, RepairRecord.is_deleted == False).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.post("/repairs", response_model=RepairRecordOut)
def create_repair(
    payload: RepairRecordCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("maintenance", "create")),
):
    asset = db.query(Asset).filter(Asset.id == payload.asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    record = RepairRecord(**payload.model_dump())
    db.add(record)
    asset.status = 2
    db.commit()
    log_change(db, asset.id, user.id, "REPAIR", {"field": "status", "old": None, "new": 2})
    db.commit()
    db.refresh(record)
    return record


@router.put("/repairs/{repair_id}", response_model=RepairRecordOut)
def update_repair(
    repair_id: int,
    payload: RepairRecordUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("maintenance", "update")),
):
    record = db.query(RepairRecord).filter(RepairRecord.id == repair_id, RepairRecord.is_deleted == False).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)
    if "status" in data and data["status"] == "closed":
        asset = db.query(Asset).filter(Asset.id == record.asset_id, Asset.is_deleted == False).first()
        if asset:
            asset.status = 0
            log_change(db, asset.id, user.id, "REPAIR", {"field": "status", "old": 2, "new": 0})
    db.commit()
    db.refresh(record)
    return record


@router.delete("/repairs/{repair_id}", response_model=Message)
def delete_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("maintenance", "update")),
):
    record = db.query(RepairRecord).filter(RepairRecord.id == repair_id, RepairRecord.is_deleted == False).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    record.is_deleted = True
    db.commit()
    return Message(message="Deleted")


@router.get("/info/{asset_id}", response_model=MaintenanceInfoOut)
def get_info(
    asset_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("maintenance", "view")),
):
    item = db.query(MaintenanceInfo).filter(MaintenanceInfo.asset_id == asset_id, MaintenanceInfo.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Info not found")
    return item


@router.put("/info/{asset_id}", response_model=MaintenanceInfoOut)
def upsert_info(
    asset_id: int,
    payload: MaintenanceInfoUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("maintenance", "update")),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    item = db.query(MaintenanceInfo).filter(MaintenanceInfo.asset_id == asset_id, MaintenanceInfo.is_deleted == False).first()
    data = payload.model_dump(exclude_unset=True)
    if item:
        for key, value in data.items():
            setattr(item, key, value)
    else:
        item = MaintenanceInfo(asset_id=asset_id, **data)
        db.add(item)
    db.commit()
    db.refresh(item)
    return item
