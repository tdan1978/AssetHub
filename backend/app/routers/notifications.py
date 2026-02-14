from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission, get_permission_scope
from app.models.asset import Asset
from app.models.asset_field_value import AssetFieldValue
from app.models.category import Category
from app.models.category_field import CategoryField
from app.models.license import License
from app.models.role_permission import RolePermission
from app.models.software_field import SoftwareField
from app.models.software_field_value import SoftwareFieldValue
from app.models.system_app import SystemApp
from app.models.system_field import SystemField
from app.models.system_field_value import SystemFieldValue
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


def parse_date(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def get_user_role_codes(user) -> set[str]:
    codes = set()
    if user.role and user.role.is_active:
        codes.add(user.role.code)
    if user.roles:
        codes.update([role.code for role in user.roles if role.is_active])
    return codes


def get_asset_scopes(user) -> set[str]:
    codes = get_user_role_codes(user)
    scopes = set()
    if "office_asset_admin" in codes:
        scopes.add("office")
    if "datacenter_asset_admin" in codes:
        scopes.add("datacenter")
    return scopes


def has_permission(db: Session, user, resource: str, action: str) -> bool:
    role_ids = []
    role_codes = []
    if user.role_id and user.role and user.role.is_active:
        role_ids.append(user.role_id)
        role_codes.append(user.role.code)
    if getattr(user, "roles", None):
        role_ids.extend([role.id for role in user.roles if role.is_active])
        role_codes.extend([role.code for role in user.roles if role.is_active])
    role_ids = list({rid for rid in role_ids if rid})
    role_codes = list({code for code in role_codes if code})
    if "super_admin" in role_codes:
        return True
    if not role_ids:
        return False
    return (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id.in_(role_ids),
            RolePermission.resource == resource,
            RolePermission.action == action,
        )
        .first()
        is not None
    )


def split_owners(value: str | None) -> list[str]:
    if not value:
        return []
    separators = [",", "，", ";", "；", "/", "、", "|"]
    result = [value]
    for sep in separators:
        next_list = []
        for item in result:
            next_list.extend(item.split(sep))
        result = next_list
    return [item.strip() for item in result if item and item.strip()]


def user_is_ops_owner(user, system: SystemApp) -> bool:
    tokens = split_owners(system.ops_owner) + split_owners(system.ops_owner_b)
    if not tokens:
        return False
    user_id = str(user.id)
    if user_id in tokens:
        return True
    candidates = {user.username, user_id}
    if user.full_name:
        candidates.add(user.full_name)
    return any(token in candidates for token in tokens)


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    user: object = Depends(require_permission("notifications", "view")),
):
    today = date.today()
    results: list[NotificationOut] = []
    role_codes = get_user_role_codes(user)
    scopes = get_asset_scopes(user)
    category_cache: dict[int, Category | None] = {}
    can_view_system = has_permission(db, user, "system_assets", "view")
    can_view_software = has_permission(db, user, "software_assets", "view")
    can_view_office_assets = has_permission(db, user, "office_hardware_assets", "view")
    can_view_datacenter_assets = has_permission(db, user, "datacenter_hardware_assets", "view")
    can_view_assets = can_view_office_assets or can_view_datacenter_assets

    asset_fields = (
        db.query(CategoryField)
        .filter(
            CategoryField.is_deleted == False,
            CategoryField.field_type == "date",
            CategoryField.reminder_enabled == True,
        )
        .all()
    )
    if can_view_assets:
        for field in asset_fields:
            days_before = field.reminder_days or 0
            values = (
                db.query(AssetFieldValue, Asset)
                .join(Asset, Asset.id == AssetFieldValue.asset_id)
                .filter(AssetFieldValue.field_id == field.id, Asset.is_deleted == False)
                .all()
            )
            for value_row, asset in values:
                if scopes:
                    category = category_cache.get(asset.category_id)
                    if category is None and asset.category_id:
                        category = (
                            db.query(Category)
                            .filter(Category.id == asset.category_id, Category.is_deleted == False)
                            .first()
                        )
                        category_cache[asset.category_id] = category
                    if not category or category.usage_scope not in scopes:
                        continue
                elif "employee" in role_codes and asset.user_id != user.id:
                    continue
                due_date = parse_date(value_row.value)
                if not due_date:
                    continue
                remind_at = due_date - timedelta(days=days_before)
                if today < remind_at:
                    continue
                message = f"资产 {asset.name or asset.sn} 的 {field.name} 将于 {due_date} 到期"
                results.append(
                    NotificationOut(
                        id=f"asset-{asset.id}-{field.id}",
                        title="资产提醒",
                        message=message,
                        due_date=due_date,
                        remind_at=remind_at,
                        entity_type="asset",
                        entity_id=asset.id,
                        field_id=field.id,
                        field_name=field.name,
                        days_before=field.reminder_days,
                    )
                )

    system_fields = (
        db.query(SystemField)
        .filter(
            SystemField.is_deleted == False,
            SystemField.field_type == "date",
            SystemField.reminder_enabled == True,
        )
        .all()
    )
    if can_view_system:
        system_scope = get_permission_scope(db, user, "system_assets", "view")
        for field in system_fields:
            days_before = field.reminder_days or 0
            values = (
                db.query(SystemFieldValue, SystemApp)
                .join(SystemApp, SystemApp.id == SystemFieldValue.system_id)
                .filter(SystemFieldValue.field_id == field.id, SystemApp.is_deleted == False)
                .all()
            )
            for value_row, system in values:
                if system_scope == "own" and not user_is_ops_owner(user, system):
                    continue
                due_date = parse_date(value_row.value)
                if not due_date:
                    continue
                remind_at = due_date - timedelta(days=days_before)
                if today < remind_at:
                    continue
                message = f"系统 {system.app_name or system.app_code} 的 {field.name} 将于 {due_date} 到期"
                results.append(
                    NotificationOut(
                        id=f"system-{system.id}-{field.id}",
                        title="系统提醒",
                        message=message,
                        due_date=due_date,
                        remind_at=remind_at,
                        entity_type="system",
                        entity_id=system.id,
                        field_id=field.id,
                        field_name=field.name,
                        days_before=field.reminder_days,
                    )
                )

    software_fields = (
        db.query(SoftwareField)
        .filter(
            SoftwareField.is_deleted == False,
            SoftwareField.field_type == "date",
            SoftwareField.reminder_enabled == True,
        )
        .all()
    )
    if can_view_software:
        for field in software_fields:
            days_before = field.reminder_days or 0
            if hasattr(License, field.field_key):
                rows = (
                    db.query(License)
                    .filter(getattr(License, field.field_key) != None)
                    .all()
                )
                for license_row in rows:
                    due_date = getattr(license_row, field.field_key)
                    due_date = parse_date(due_date)
                    if not due_date:
                        continue
                    remind_at = due_date - timedelta(days=days_before)
                    if today < remind_at:
                        continue
                    message = f"软件 {license_row.software_name or license_row.vendor} 的 {field.name} 将于 {due_date} 到期"
                    results.append(
                        NotificationOut(
                            id=f"license-{license_row.id}-{field.id}",
                            title="软件提醒",
                            message=message,
                            due_date=due_date,
                            remind_at=remind_at,
                            entity_type="license",
                            entity_id=license_row.id,
                            field_id=field.id,
                            field_name=field.name,
                            days_before=field.reminder_days,
                        )
                    )
            values = (
                db.query(SoftwareFieldValue, License)
                .join(License, License.id == SoftwareFieldValue.license_id)
                .filter(SoftwareFieldValue.field_id == field.id)
                .all()
            )
            for value_row, license_row in values:
                due_date = parse_date(value_row.value)
                if not due_date:
                    continue
                remind_at = due_date - timedelta(days=days_before)
                if today < remind_at:
                    continue
                message = f"软件 {license_row.software_name or license_row.vendor} 的 {field.name} 将于 {due_date} 到期"
                results.append(
                    NotificationOut(
                        id=f"license-custom-{license_row.id}-{field.id}",
                        title="软件提醒",
                        message=message,
                        due_date=due_date,
                        remind_at=remind_at,
                        entity_type="license",
                        entity_id=license_row.id,
                        field_id=field.id,
                        field_name=field.name,
                        days_before=field.reminder_days,
                    )
                )

    results.sort(key=lambda item: (item.remind_at or today, item.title, item.id))
    return results
