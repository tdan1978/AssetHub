from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission, require_any_permission
from app.models.asset import Asset
from app.models.category import Category
from app.models.asset_field_value import AssetFieldValue
from app.schemas.asset_field_value import AssetFieldValueIn, AssetFieldValueOut

router = APIRouter(prefix="/api/v1/assets", tags=["asset-fields"])


@router.get("/{asset_id}/fields", response_model=list[AssetFieldValueOut])
def list_asset_fields(
    asset_id: int,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_permission(
            [
                ("office_hardware_assets", "view"),
                ("datacenter_hardware_assets", "view"),
            ]
        )
    ),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    scopes = get_asset_scopes(user)
    if scopes:
        category = db.query(Category).filter(Category.id == asset.category_id).first()
        if not category or category.usage_scope not in scopes:
            raise HTTPException(status_code=403, detail="Forbidden")
    elif "employee" in get_user_role_codes(user) and asset.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return db.query(AssetFieldValue).filter(AssetFieldValue.asset_id == asset_id).all()


@router.put("/{asset_id}/fields", response_model=list[AssetFieldValueOut])
def upsert_asset_fields(
    asset_id: int,
    payload: list[AssetFieldValueIn],
    db: Session = Depends(get_db),
    user=Depends(
        require_any_permission(
            [
                ("office_hardware_assets", "update"),
                ("datacenter_hardware_assets", "update"),
            ]
        )
    ),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    scopes = get_asset_scopes(user)
    if scopes:
        category = db.query(Category).filter(Category.id == asset.category_id).first()
        if not category or category.usage_scope not in scopes:
            raise HTTPException(status_code=403, detail="Forbidden")
    elif "employee" in get_user_role_codes(user) and asset.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

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


def get_user_role_codes(user) -> set[str]:
    codes = set()
    if user.role:
        codes.add(user.role.code)
    if user.roles:
        codes.update([role.code for role in user.roles])
    return codes


def get_asset_scopes(user) -> set[str]:
    codes = get_user_role_codes(user)
    scopes = set()
    if "office_asset_admin" in codes:
        scopes.add("office")
    if "datacenter_asset_admin" in codes:
        scopes.add("datacenter")
    return scopes
