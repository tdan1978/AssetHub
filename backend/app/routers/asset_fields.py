from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.asset import Asset
from app.models.asset_field_value import AssetFieldValue
from app.schemas.asset_field_value import AssetFieldValueIn, AssetFieldValueOut

router = APIRouter(prefix="/api/v1/assets", tags=["asset-fields"])


@router.get("/{asset_id}/fields", response_model=list[AssetFieldValueOut])
def list_asset_fields(
    asset_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db.query(AssetFieldValue).filter(AssetFieldValue.asset_id == asset_id).all()


@router.put("/{asset_id}/fields", response_model=list[AssetFieldValueOut])
def upsert_asset_fields(
    asset_id: int,
    payload: list[AssetFieldValueIn],
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    existing = {
        item.field_id: item
        for item in db.query(AssetFieldValue).filter(AssetFieldValue.asset_id == asset_id).all()
    }
    for item in payload:
        if item.field_id in existing:
            existing[item.field_id].value = item.value
        else:
            db.add(AssetFieldValue(asset_id=asset_id, field_id=item.field_id, value=item.value))
    db.commit()
    return db.query(AssetFieldValue).filter(AssetFieldValue.asset_id == asset_id).all()
