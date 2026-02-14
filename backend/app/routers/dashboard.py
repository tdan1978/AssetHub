from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.asset import Asset
from app.models.dashboard_template import DashboardTemplate
from app.models.dashboard_widget import DashboardWidget
from app.models.license import License
from app.models.system_app import SystemApp

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


WIDGET_METRICS = {
    "kpi_total_assets",
    "kpi_in_use_rate",
    "kpi_repairing",
    "kpi_pending_scrap",
    "kpi_license_warn",
    "chart_asset_status",
    "chart_asset_trend",
    "chart_license_expiry",
    "chart_system_dev_lang",
    "chart_system_status",
}


class DashboardWidgetUpdate(BaseModel):
    id: int | None = None
    widget_key: str
    title: str
    widget_type: str = Field(pattern="^(kpi|chart)$")
    metric_key: str
    col_span: int = 1
    row_span: int = 1
    sort_order: int = 0
    style_config: dict = Field(default_factory=dict)
    data_source_config: dict = Field(default_factory=dict)
    is_active: bool = True


class DashboardWidgetsUpdateRequest(BaseModel):
    version: int | None = None
    widgets: list[DashboardWidgetUpdate]


def _dashboard_metrics(db: Session):
    total = db.query(Asset).filter(Asset.is_deleted == False).count()
    idle = db.query(Asset).filter(Asset.is_deleted == False, Asset.status == 0).count()
    in_use = db.query(Asset).filter(Asset.is_deleted == False, Asset.status == 1).count()
    repairing = db.query(Asset).filter(Asset.is_deleted == False, Asset.status == 2).count()
    pending_scrap = db.query(Asset).filter(Asset.is_deleted == False, Asset.status == 3).count()
    scrapped = db.query(Asset).filter(Asset.is_deleted == False, Asset.status == 4).count()

    warn_date = date.today() + timedelta(days=30)
    license_warn = db.query(License).filter(License.expire_at != None, License.expire_at <= warn_date).count()

    today = date.today()
    expire_30 = today + timedelta(days=30)
    expire_60 = today + timedelta(days=60)
    expire_90 = today + timedelta(days=90)
    exp_30 = db.query(License).filter(License.expire_at != None, License.expire_at <= expire_30).count()
    exp_60 = (
        db.query(License)
        .filter(License.expire_at != None, License.expire_at > expire_30, License.expire_at <= expire_60)
        .count()
    )
    exp_90 = (
        db.query(License)
        .filter(License.expire_at != None, License.expire_at > expire_60, License.expire_at <= expire_90)
        .count()
    )

    year = today.year
    month = today.month
    months = []
    for i in range(11, -1, -1):
        mm = month - i
        yy = year
        while mm <= 0:
            mm += 12
            yy -= 1
        months.append((yy, mm))
    start_year, start_month = months[0]
    start_date = date(start_year, start_month, 1)
    assets = db.query(Asset).filter(Asset.is_deleted == False, Asset.created_at >= start_date).all()
    month_counts = {f"{yy}-{mm:02d}": 0 for yy, mm in months}
    for item in assets:
        if not item.created_at:
            continue
        key = f"{item.created_at.year}-{item.created_at.month:02d}"
        if key in month_counts:
            month_counts[key] += 1
    monthly_series = [{"month": key, "count": value} for key, value in month_counts.items()]

    system_status_rows = (
        db.query(SystemApp.app_status, func.count(SystemApp.id))
        .filter(SystemApp.is_deleted == False)
        .group_by(SystemApp.app_status)
        .all()
    )
    system_status_counts = []
    for status, count in system_status_rows:
        label = (status or "").strip() if isinstance(status, str) else (str(status).strip() if status is not None else "")
        if not label:
            label = "未设置"
        system_status_counts.append({"label": label, "value": count})

    dev_lang_rows = (
        db.query(SystemApp.dev_lang, func.count(SystemApp.id))
        .filter(SystemApp.is_deleted == False)
        .group_by(SystemApp.dev_lang)
        .all()
    )
    system_dev_lang_counts = []
    for lang, count in dev_lang_rows:
        label = (lang or "").strip() if isinstance(lang, str) else (str(lang).strip() if lang is not None else "")
        if not label:
            label = "未设置"
        system_dev_lang_counts.append({"label": label, "value": count})

    return {
        "total": total,
        "in_use_rate": (in_use / total) if total else 0,
        "repairing": repairing,
        "pending_scrap": pending_scrap,
        "license_expire_warn": license_warn,
        "status_counts": {
            "idle": idle,
            "in_use": in_use,
            "repairing": repairing,
            "pending_scrap": pending_scrap,
            "scrapped": scrapped,
        },
        "license_expire_buckets": {"d30": exp_30, "d60": exp_60, "d90": exp_90},
        "monthly_assets": monthly_series,
        "system_status_counts": system_status_counts,
        "system_dev_lang_counts": system_dev_lang_counts,
    }


def _widget_payload(widget: DashboardWidget):
    return {
        "id": widget.id,
        "widget_key": widget.widget_key,
        "title": widget.title,
        "widget_type": widget.widget_type,
        "metric_key": widget.metric_key,
        "col_span": widget.col_span,
        "row_span": widget.row_span,
        "sort_order": widget.sort_order,
        "style_config": widget.style_config or {},
        "data_source_config": widget.data_source_config or {},
        "is_active": widget.is_active,
    }


def _template_payload(template: DashboardTemplate):
    widgets = sorted(template.widgets or [], key=lambda item: (item.sort_order, item.id))
    return {
        "id": template.id,
        "name": template.name,
        "code": template.code,
        "description": template.description,
        "version": template.version,
        "is_default": template.is_default,
        "is_published": template.is_published,
        "widgets": [_widget_payload(item) for item in widgets],
    }


def _current_template(db: Session):
    current = (
        db.query(DashboardTemplate)
        .filter(DashboardTemplate.is_deleted == False, DashboardTemplate.is_published == True)
        .order_by(DashboardTemplate.id.asc())
        .first()
    )
    if current:
        return current
    return (
        db.query(DashboardTemplate)
        .filter(DashboardTemplate.is_deleted == False)
        .order_by(DashboardTemplate.id.asc())
        .first()
    )


@router.get("")
def dashboard(db: Session = Depends(get_db), _: object = Depends(require_permission("dashboard", "view"))):
    metrics = _dashboard_metrics(db)
    template = _current_template(db)
    return {
        **metrics,
        "template": _template_payload(template) if template else None,
    }


@router.get("/template/current")
def current_template(db: Session = Depends(get_db), _: object = Depends(require_permission("dashboard", "view"))):
    template = _current_template(db)
    if not template:
        raise HTTPException(status_code=404, detail="No dashboard template")
    return _template_payload(template)


@router.get("/templates")
def list_templates(db: Session = Depends(get_db), _: object = Depends(require_permission("dashboard", "edit"))):
    items = (
        db.query(DashboardTemplate)
        .filter(DashboardTemplate.is_deleted == False)
        .order_by(DashboardTemplate.id.asc())
        .all()
    )
    return [_template_payload(item) for item in items]


@router.put("/templates/{template_id}/widgets")
def update_template_widgets(
    template_id: int,
    payload: DashboardWidgetsUpdateRequest,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dashboard", "edit")),
):
    template = (
        db.query(DashboardTemplate)
        .filter(DashboardTemplate.id == template_id, DashboardTemplate.is_deleted == False)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    existing = {item.widget_key: item for item in db.query(DashboardWidget).filter(DashboardWidget.template_id == template_id).all()}
    incoming_keys = set()
    for idx, item in enumerate(payload.widgets):
        if item.metric_key not in WIDGET_METRICS:
            raise HTTPException(status_code=400, detail=f"Unsupported metric_key: {item.metric_key}")
        incoming_keys.add(item.widget_key)
        target = existing.get(item.widget_key)
        if not target:
            target = DashboardWidget(template_id=template_id, widget_key=item.widget_key)
            db.add(target)
        target.title = item.title.strip() or item.widget_key
        target.widget_type = item.widget_type
        target.metric_key = item.metric_key
        target.col_span = min(3, max(1, int(item.col_span or 1)))
        target.row_span = min(4, max(1, int(item.row_span or 1)))
        target.sort_order = int(item.sort_order if item.sort_order is not None else idx * 10)
        target.style_config = item.style_config or {}
        target.data_source_config = item.data_source_config or {}
        target.is_active = bool(item.is_active)
    for widget_key, item in existing.items():
        if widget_key not in incoming_keys:
            db.delete(item)
    template.version = int(template.version or 1) + 1
    db.commit()
    db.refresh(template)
    return _template_payload(template)


@router.post("/templates/{template_id}/publish")
def publish_template(
    template_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("dashboard", "publish")),
):
    template = (
        db.query(DashboardTemplate)
        .filter(DashboardTemplate.id == template_id, DashboardTemplate.is_deleted == False)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    (
        db.query(DashboardTemplate)
        .filter(DashboardTemplate.is_deleted == False, DashboardTemplate.id != template_id)
        .update({"is_published": False}, synchronize_session=False)
    )
    template.is_published = True
    db.commit()
    db.refresh(template)
    return _template_payload(template)
