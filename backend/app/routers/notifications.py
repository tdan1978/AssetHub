from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.asset import Asset
from app.models.asset_field_value import AssetFieldValue
from app.models.category_field import CategoryField
from app.models.license import License
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


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    today = date.today()
    results: list[NotificationOut] = []

    asset_fields = (
        db.query(CategoryField)
        .filter(
            CategoryField.is_deleted == False,
            CategoryField.field_type == "date",
            CategoryField.reminder_enabled == True,
        )
        .all()
    )
    for field in asset_fields:
        days_before = field.reminder_days or 0
        values = (
            db.query(AssetFieldValue, Asset)
            .join(Asset, Asset.id == AssetFieldValue.asset_id)
            .filter(AssetFieldValue.field_id == field.id, Asset.is_deleted == False)
            .all()
        )
        for value_row, asset in values:
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
    for field in system_fields:
        days_before = field.reminder_days or 0
        values = (
            db.query(SystemFieldValue, SystemApp)
            .join(SystemApp, SystemApp.id == SystemFieldValue.system_id)
            .filter(SystemFieldValue.field_id == field.id, SystemApp.is_deleted == False)
            .all()
        )
        for value_row, system in values:
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
