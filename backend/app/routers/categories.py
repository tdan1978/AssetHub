from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.category import Category
from app.models.category_field import CategoryField
from app.models.asset_field_value import AssetFieldValue
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.category_field import CategoryFieldCreate, CategoryFieldOut, CategoryFieldUpdate, FIELD_TYPES
from app.schemas.common import Message

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


def normalize_select_config(data: dict):
    field_type = data.get("field_type")
    if field_type == "combo_select":
        data["field_type"] = "single_select"
        data["searchable"] = True
    current_type = data.get("field_type")
    if current_type not in ("single_select", "multi_select"):
        data["searchable"] = False


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

OFFICE_BASE_FIELDS = [
    ("品牌型号", "brand_model", "text", 1, False, None),
    ("使用人", "user_name", "text", 2, False, None),
    ("所属部门", "dept_name", "text", 3, False, None),
    ("办公地点", "office_location", "text", 4, False, None),
    ("领用日期", "assigned_at", "date", 5, False, None),
    ("供应商", "supplier", "text", 6, False, None),
    ("保修截止", "warranty_due", "date", 7, True, 30),
    ("网络标识", "network_id", "text", 8, False, None),
    ("最近维护日期", "last_maint_at", "date", 9, False, None),
    ("维修记录", "repair_notes", "textarea", 10, False, None),
    ("备注", "remark", "textarea", 11, False, None),
]
DATACENTER_BASE_FIELDS = [
    ("品牌型号", "brand_model", "text", 1, False, None, None),
    ("数据中心/机房", "dc_room", "single_select", 2, False, None, ["机房A", "机房B", "机房C"]),
    ("机柜编号", "cabinet_no", "single_select", 3, False, None, ["柜A", "柜B", "柜C"]),
    ("起始U位", "rack_u_start", "text", 4, False, None, None),
    ("所属项目/业务", "service_name", "text", 5, False, None, None),
    ("保修日期", "warranty_due", "date", 6, True, 30, None),
    ("维保状态", "maintenance_status", "single_select", 7, False, None, ["在保", "过保"]),
    ("维修记录", "repair_notes", "text", 8, False, None, None),
]


def seed_office_fields_for_category(db: Session, category_id: int):
    for name, key, ftype, order, reminder_enabled, reminder_days in OFFICE_BASE_FIELDS:
        field = (
            db.query(CategoryField)
            .filter(
                CategoryField.category_id == category_id,
                CategoryField.field_key == key,
                CategoryField.is_deleted == False,
            )
            .first()
        )
        if not field:
            db.add(
                CategoryField(
                    category_id=category_id,
                    name=name,
                    field_key=key,
                    field_type=ftype,
                    sort_order=order,
                    reminder_enabled=reminder_enabled,
                    reminder_days=reminder_days,
                    usage_scope="office",
                    is_locked=False,
                )
            )
        else:
            if field.usage_scope != "office":
                field.usage_scope = "office"
            if field.is_locked:
                field.is_locked = False
            if reminder_enabled and not field.reminder_enabled:
                field.reminder_enabled = True
            if reminder_enabled and field.reminder_days != reminder_days:
                field.reminder_days = reminder_days


def seed_datacenter_fields_for_category(db: Session, category_id: int):
    for name, key, ftype, order, reminder_enabled, reminder_days, options in DATACENTER_BASE_FIELDS:
        field = (
            db.query(CategoryField)
            .filter(
                CategoryField.category_id == category_id,
                CategoryField.field_key == key,
                CategoryField.is_deleted == False,
            )
            .first()
        )
        if not field:
            db.add(
                CategoryField(
                    category_id=category_id,
                    name=name,
                    field_key=key,
                    field_type=ftype,
                    sort_order=order,
                    reminder_enabled=reminder_enabled,
                    reminder_days=reminder_days,
                    options=options,
                    usage_scope="datacenter",
                    is_locked=False,
                )
            )
        else:
            if field.usage_scope != "datacenter":
                field.usage_scope = "datacenter"
            if field.is_locked:
                field.is_locked = False
            if options and not field.options:
                field.options = options
            if reminder_enabled and not field.reminder_enabled:
                field.reminder_enabled = True
            if reminder_enabled and field.reminder_days != reminder_days:
                field.reminder_days = reminder_days


@router.get("", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    user=Depends(require_permission("asset_types", "view")),
):
    query = db.query(Category).filter(Category.is_deleted == False)
    scopes = get_asset_scopes(user)
    if len(scopes) == 1:
        query = query.filter(Category.usage_scope.in_(scopes))
    return query.order_by(Category.id.desc()).all()


@router.get("/by-scope", response_model=list[CategoryOut])
def list_categories_by_scope(
    dept: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_permission("asset_types", "view")),
):
    query = db.query(Category).filter(Category.is_deleted == False)
    scope = None
    if dept == "办公和业务":
        scope = "office"
    elif dept == "数据中心":
        scope = "datacenter"
    scopes = get_asset_scopes(user)
    if len(scopes) == 1:
        scope = list(scopes)[0]
    elif scopes and scope and scope not in scopes:
        raise HTTPException(status_code=403, detail="Forbidden")
    if scope:
        query = query.filter(Category.usage_scope == scope)
    return query.order_by(Category.id.desc()).all()


@router.post("", response_model=CategoryOut)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("asset_types", "create")),
):
    scopes = get_asset_scopes(user)
    if scopes and payload.usage_scope not in scopes:
        raise HTTPException(status_code=403, detail="Forbidden")
    exists = db.query(Category).filter(Category.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category exists")
    item = Category(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Category exists")
    db.refresh(item)
    if item.usage_scope == "office":
        seed_office_fields_for_category(db, item.id)
        db.commit()
    if item.usage_scope == "datacenter":
        seed_datacenter_fields_for_category(db, item.id)
        db.commit()
    return item


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("asset_types", "update")),
):
    item = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    scopes = get_asset_scopes(user)
    if scopes and item.usage_scope not in scopes:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = payload.model_dump(exclude_unset=True)
    usage_changed_to_office = data.get("usage_scope") == "office" and item.usage_scope != "office"
    usage_changed_to_datacenter = data.get("usage_scope") == "datacenter" and item.usage_scope != "datacenter"
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    if usage_changed_to_office:
        seed_office_fields_for_category(db, item.id)
        db.commit()
    if usage_changed_to_datacenter:
        seed_datacenter_fields_for_category(db, item.id)
        db.commit()
    return item


@router.delete("/{category_id}", response_model=Message)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("asset_types", "delete")),
):
    item = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    field_ids = [
        row[0]
        for row in db.query(CategoryField.id).filter(CategoryField.category_id == category_id).all()
    ]
    if field_ids:
        db.query(AssetFieldValue).filter(AssetFieldValue.field_id.in_(field_ids)).delete(synchronize_session=False)
    db.query(CategoryField).filter(CategoryField.category_id == category_id).delete(synchronize_session=False)
    db.delete(item)
    db.commit()
    return Message(message="Deleted")


@router.get("/{category_id}/fields", response_model=list[CategoryFieldOut])
def list_fields(
    category_id: int,
    dept: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_permission("asset_types", "view")),
):
    query = db.query(CategoryField).filter(
        CategoryField.category_id == category_id,
        CategoryField.is_deleted == False,
    )
    scope = None
    if dept == "办公和业务":
        scope = "office"
    elif dept == "数据中心":
        scope = "datacenter"
    scopes = get_asset_scopes(user)
    if len(scopes) == 1:
        scope = list(scopes)[0]
    elif scopes and scope and scope not in scopes:
        raise HTTPException(status_code=403, detail="Forbidden")
    if scope:
        if scope == "office":
            has_office_fields = (
                db.query(CategoryField)
                .filter(
                    CategoryField.category_id == category_id,
                    CategoryField.usage_scope == "office",
                    CategoryField.is_deleted == False,
                )
                .first()
            )
            if not has_office_fields:
                category = (
                    db.query(Category)
                    .filter(Category.id == category_id, Category.is_deleted == False)
                    .first()
                )
                if category and category.usage_scope == "office":
                    seed_office_fields_for_category(db, category_id)
                    db.commit()
        if scope == "datacenter":
            has_datacenter_fields = (
                db.query(CategoryField)
                .filter(
                    CategoryField.category_id == category_id,
                    CategoryField.usage_scope == "datacenter",
                    CategoryField.is_deleted == False,
                )
                .first()
            )
            if not has_datacenter_fields:
                category = (
                    db.query(Category)
                    .filter(Category.id == category_id, Category.is_deleted == False)
                    .first()
                )
                if category and category.usage_scope == "datacenter":
                    seed_datacenter_fields_for_category(db, category_id)
                    db.commit()
        query = query.filter(CategoryField.usage_scope == scope)
    fields = query.order_by(CategoryField.sort_order.asc(), CategoryField.id.asc()).all()
    if not fields:
        return fields
    field_ids = [item.id for item in fields]
    counts = dict(
        db.query(AssetFieldValue.field_id, func.count(1))
        .filter(AssetFieldValue.field_id.in_(field_ids))
        .group_by(AssetFieldValue.field_id)
        .all()
    )
    for item in fields:
        item.in_use = item.id in counts
    return fields


@router.post("/{category_id}/fields", response_model=CategoryFieldOut)
def create_field(
    category_id: int,
    payload: CategoryFieldCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("asset_types", "create")),
):
    if payload.field_type not in FIELD_TYPES and payload.field_type != "combo_select":
        raise HTTPException(status_code=400, detail="Invalid field type")
    category = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    scopes = get_asset_scopes(user)
    if scopes and category.usage_scope not in scopes:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = payload.model_dump()
    normalize_select_config(data)
    if category.usage_scope in ("office", "datacenter"):
        data["usage_scope"] = category.usage_scope
    item = CategoryField(category_id=category_id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/fields/{field_id}", response_model=CategoryFieldOut)
def update_field(
    field_id: int,
    payload: CategoryFieldUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("asset_types", "update")),
):
    item = db.query(CategoryField).filter(CategoryField.id == field_id, CategoryField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    scopes = get_asset_scopes(user)
    if scopes and item.usage_scope not in scopes:
        raise HTTPException(status_code=403, detail="Forbidden")
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
    user=Depends(require_permission("asset_types", "delete")),
):
    item = db.query(CategoryField).filter(CategoryField.id == field_id, CategoryField.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Field not found")
    in_use = (
        db.query(AssetFieldValue.id)
        .filter(AssetFieldValue.field_id == item.id)
        .first()
    )
    if in_use:
        raise HTTPException(status_code=400, detail="Field is in use")
    scopes = get_asset_scopes(user)
    if scopes and item.usage_scope not in scopes:
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(item)
    db.commit()
    return Message(message="Deleted")
