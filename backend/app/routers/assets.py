from datetime import datetime, date
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
import pandas as pd

from app.core.database import get_db
from app.core.deps import require_permission, require_any_permission
from app.models.asset import Asset
from app.models.asset_log import AssetLog
from app.models.category import Category
from app.schemas.asset import AssetCreate, AssetOut, AssetUpdate
from app.schemas.common import Page, Message
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


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


def generate_asset_no(db: Session, prefix: str) -> str:
    base = f"{prefix}-"
    candidates = db.query(Asset.asset_no).filter(Asset.asset_no.like(f"{base}%")).all()
    max_seq = 0
    for (asset_no,) in candidates:
        if not asset_no or not asset_no.startswith(base):
            continue
        tail = asset_no.replace(base, "", 1)
        if tail.isdigit():
            max_seq = max(max_seq, int(tail))
    return f"{base}{max_seq + 1:010d}"


def resolve_category_prefix(db: Session, category_id: int | None, category_name: str | None) -> str:
    if category_id:
        category = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
        if category:
            if category.code:
                return category.code.strip().replace(" ", "").upper()
            return f"C{category.id}"
    if category_name:
        category = db.query(Category).filter(Category.name == category_name, Category.is_deleted == False).first()
        if category:
            if category.code:
                return category.code.strip().replace(" ", "").upper()
            return f"C{category.id}"
    return "ASSET"


def ensure_asset_scope(db: Session, asset: Asset, user):
    scopes = get_asset_scopes(user)
    if not scopes:
        return
    category = db.query(Category).filter(Category.id == asset.category_id).first()
    if not category or category.usage_scope not in scopes:
        raise HTTPException(status_code=403, detail="Forbidden")


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


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        "sn": ["sn", "SN", "序列号"],
        "asset_no": ["asset_no", "编号", "资产编号"],
        "name": ["name", "资产名称"],
        "category": ["category", "分类"],
        "purchase_at": ["purchase_at", "采购日期"],
        "price": ["price", "采购原值", "价格"],
        "warranty_at": ["warranty_at", "维保截止日期", "维保期"],
        "location": ["location", "位置"],
        "attachment": ["attachment", "附件", "发票", "合同"],
    }
    columns = {str(col).strip(): col for col in df.columns}
    data = {}
    for key, names in aliases.items():
        for name in names:
            if name in columns:
                data[key] = df[columns[name]]
                break
    return pd.DataFrame(data)


@router.post("/batch-import")
def batch_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(
        require_any_permission(
            [
                ("office_hardware_assets", "create"),
                ("datacenter_hardware_assets", "create"),
            ]
        )
    ),
):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Invalid file type")
    content = file.file.read()
    df = pd.read_excel(BytesIO(content))
    df_norm = normalize_columns(df)

    required = ["sn", "name", "category", "purchase_at"]
    missing = [col for col in required if col not in df_norm.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    categories = {
        item.name: item.id
        for item in db.query(Category).filter(Category.is_deleted == False).all()
    }
    enforce_category = len(categories) > 0
    existing_sn = {row[0] for row in db.query(Asset.sn).filter(Asset.is_deleted == False).all()}
    dup_in_file = df_norm["sn"].astype(str).duplicated(keep=False)

    errors = {}
    created = 0
    for idx, row in df_norm.iterrows():
        row_errors = []
        sn = str(row.get("sn", "")).strip()
        name = str(row.get("name", "")).strip()
        category = str(row.get("category", "")).strip()
        purchase_at = row.get("purchase_at")

        if not sn:
            row_errors.append("SN required")
        if not name:
            row_errors.append("Name required")
        if not category:
            row_errors.append("Category required")
        if pd.isna(purchase_at):
            row_errors.append("Purchase date required")
        else:
            try:
                purchase_at = pd.to_datetime(purchase_at).date()
            except Exception:
                row_errors.append("Invalid purchase date")

        if sn in existing_sn:
            row_errors.append("SN already exists")
        if bool(dup_in_file.loc[idx]):
            row_errors.append("Duplicate SN in file")

        category_id = None
        if enforce_category:
            category_id = categories.get(category)
            if not category_id:
                row_errors.append("Category not found")

        price = row.get("price")
        if price is not None and not pd.isna(price):
            try:
                price_val = float(price)
            except Exception:
                row_errors.append("Invalid price")
                price_val = None
        else:
            price_val = None

        attachment = row.get("attachment")
        if price_val is not None and price_val > 5000:
            if attachment is None or (isinstance(attachment, float) and pd.isna(attachment)) or str(attachment).strip() == "":
                row_errors.append("Attachment required for price > 5000")

        if row_errors:
            errors[idx] = "; ".join(row_errors)
            continue

        prefix = resolve_category_prefix(db, category_id, category)
        asset_no = generate_asset_no(db, prefix)

        asset = Asset(
            sn=sn,
            asset_no=asset_no,
            name=name,
            category=category,
            category_id=category_id,
            status=0,
            location=str(row.get("location", "")).strip() or None,
            price=price_val,
            purchase_at=purchase_at,
            warranty_at=pd.to_datetime(row.get("warranty_at")).date() if not pd.isna(row.get("warranty_at")) else None,
        )
        db.add(asset)
        db.flush()
        log_change(db, asset.id, user.id, "IN", {"field": "create", "old": None, "new": {"sn": sn}})
        created += 1
        existing_sn.add(sn)

    db.commit()

    if errors:
        df_out = df.copy()
        df_out["error"] = ""
        for idx, msg in errors.items():
            df_out.loc[idx, "error"] = msg
        output = BytesIO()
        df_out.to_excel(output, index=False)
        output.seek(0)
        headers = {"Content-Disposition": "attachment; filename=import_errors.xlsx"}
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers,
        )

    return Message(message=f"Imported {created} assets")

@router.get("", response_model=Page[AssetOut])
def list_assets(
    page: int = 1,
    size: int = 20,
    q: str | None = None,
    status: int | None = None,
    scope: str | None = None,
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
    query = db.query(Asset).filter(Asset.is_deleted == False)
    joined_category = False
    role_codes = get_user_role_codes(user)
    scopes = get_asset_scopes(user)
    if scope in ("office", "datacenter"):
        query = query.join(Category, Asset.category_id == Category.id).filter(Category.usage_scope == scope)
        joined_category = True
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Asset.sn.like(like), Asset.name.like(like), Asset.asset_no.like(like)))
    if status is not None:
        query = query.filter(Asset.status == status)
    if scopes:
        if scope and scope not in scopes:
            raise HTTPException(status_code=403, detail="Forbidden")
        if len(scopes) == 1:
            if not joined_category:
                query = query.join(Category, Asset.category_id == Category.id)
                joined_category = True
            query = query.filter(Category.usage_scope.in_(scopes))
    elif "employee" in role_codes:
        query = query.filter(Asset.user_id == user.id)
    elif "auditor" in role_codes and scope in ("office", "datacenter"):
        if not joined_category:
            query = query.join(Category, Asset.category_id == Category.id)
            joined_category = True
        query = query.filter(Category.usage_scope == scope)
    total, items = paginate(query.order_by(Asset.id.desc()), page, size)
    return Page(total=total, items=items)


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(
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
    role_codes = get_user_role_codes(user)
    scopes = get_asset_scopes(user)
    if scopes:
        category = db.query(Category).filter(Category.id == asset.category_id).first()
        if not category or category.usage_scope not in scopes:
            raise HTTPException(status_code=403, detail="Forbidden")
    elif "employee" in role_codes and asset.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return asset


@router.post("", response_model=AssetOut)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_permission(
            [
                ("office_hardware_assets", "create"),
                ("datacenter_hardware_assets", "create"),
            ]
        )
    ),
):
    exists = db.query(Asset).filter(Asset.sn == payload.sn, Asset.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="SN already exists")
    prefix = resolve_category_prefix(db, payload.category_id, payload.category)
    scopes = get_asset_scopes(user)
    if scopes:
        category = db.query(Category).filter(Category.id == payload.category_id, Category.is_deleted == False).first()
        if not category or category.usage_scope not in scopes:
            raise HTTPException(status_code=403, detail="Forbidden")
    payload_data = payload.model_dump()
    payload_data["asset_no"] = generate_asset_no(db, prefix)
    asset = Asset(**payload_data)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    log_change(db, asset.id, user.id, "IN", {"field": "create", "old": None, "new": payload.model_dump()})
    db.commit()
    return asset


@router.put("/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: int,
    payload: AssetUpdate,
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
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"] is not None:
        category = db.query(Category).filter(Category.id == data["category_id"], Category.is_deleted == False).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        if scopes and category.usage_scope not in scopes:
            raise HTTPException(status_code=403, detail="Forbidden")
    data.pop("asset_no", None)
    for key, value in data.items():
        setattr(asset, key, value)
    db.commit()
    log_change(db, asset.id, user.id, "UPDATE", {"field": "bulk", "old": None, "new": data})
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/{asset_id}/checkout", response_model=AssetOut)
def checkout_asset(
    asset_id: int,
    user_id: int | None = Query(None),
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
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).with_for_update().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.status != 0:
        raise HTTPException(status_code=400, detail="Asset not idle")
    ensure_asset_scope(db, asset, user)
    category = db.query(Category).filter(Category.id == asset.category_id).first()
    if category and category.usage_scope == "office" and not user_id:
        raise HTTPException(status_code=400, detail="User required for office assets")
    asset.status = 1
    asset.user_id = user_id if category and category.usage_scope == "office" else None
    db.commit()
    log_change(db, asset.id, user.id, "OUT", {"field": "status", "old": 0, "new": 1})
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/{asset_id}/checkin", response_model=AssetOut)
def checkin_asset(
    asset_id: int,
    damaged: bool = False,
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
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).with_for_update().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.status != 1:
        raise HTTPException(status_code=400, detail="Asset not in use")
    ensure_asset_scope(db, asset, user)
    asset.status = 2 if damaged else 0
    asset.user_id = None
    db.commit()
    log_change(db, asset.id, user.id, "IN", {"field": "status", "old": 1, "new": asset.status})
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/{asset_id}/transfer", response_model=AssetOut)
def transfer_asset(
    asset_id: int,
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
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).with_for_update().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    ensure_asset_scope(db, asset, user)
    db.commit()
    log_change(db, asset.id, user.id, "TRANSFER", {"field": "transfer", "old": None, "new": None})
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/{asset_id}/discard", response_model=AssetOut)
def discard_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("scrap", "update")),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).with_for_update().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    ensure_asset_scope(db, asset, user)
    if asset.status == 1:
        raise HTTPException(status_code=400, detail="Cannot discard in-use asset")
    if asset.status not in (0, 2, 3):
        raise HTTPException(status_code=400, detail="Invalid state")
    asset.status = 3
    db.commit()
    log_change(db, asset.id, user.id, "DISCARD", {"field": "status", "old": None, "new": 3})
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/{asset_id}/scrap", response_model=AssetOut)
def scrap_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("scrap", "update")),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).with_for_update().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    ensure_asset_scope(db, asset, user)
    if asset.status != 3:
        raise HTTPException(status_code=400, detail="Asset not pending scrap")
    asset.status = 4
    db.commit()
    log_change(db, asset.id, user.id, "SCRAP", {"field": "status", "old": 3, "new": 4})
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/{asset_id}/unscrap", response_model=AssetOut)
def unscrap_asset(
    asset_id: int,
    reason: str | None = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_permission("scrap", "update")),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).with_for_update().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    ensure_asset_scope(db, asset, user)
    if asset.status not in (3, 4):
        raise HTTPException(status_code=400, detail="Asset not in scrap state")
    if asset.status == 4 and (not reason or not reason.strip()):
        raise HTTPException(status_code=400, detail="Reason required for recovered scrap asset")
    old_status = asset.status
    asset.status = 0
    db.commit()
    log_change(
        db,
        asset.id,
        user.id,
        "UNSCRAP",
        {"field": "status", "old": old_status, "new": 0, "reason": reason},
    )
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", response_model=Message)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_permission(
            [
                ("office_hardware_assets", "delete"),
                ("datacenter_hardware_assets", "delete"),
            ]
        )
    ),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    asset.is_deleted = True
    db.commit()
    log_change(db, asset.id, user.id, "DELETE", {"field": "is_deleted", "old": False, "new": True})
    db.commit()
    return Message(message="Deleted")
