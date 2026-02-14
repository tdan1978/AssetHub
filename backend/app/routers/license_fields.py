from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.license import License
from app.models.software_field_value import SoftwareFieldValue
from app.schemas.software_field_value import SoftwareFieldValueIn, SoftwareFieldValueOut

router = APIRouter(prefix="/api/v1/licenses", tags=["license-fields"])


@router.get("/{license_id}/fields", response_model=list[SoftwareFieldValueOut])
def list_license_fields(
    license_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("software_assets", "view")),
):
    item = db.query(License).filter(License.id == license_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="License not found")
    return db.query(SoftwareFieldValue).filter(SoftwareFieldValue.license_id == license_id).all()


@router.put("/{license_id}/fields", response_model=list[SoftwareFieldValueOut])
def upsert_license_fields(
    license_id: int,
    payload: list[SoftwareFieldValueIn],
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("software_assets", "update")),
):
    item = db.query(License).filter(License.id == license_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="License not found")

    existing = {
        row.field_id: row
        for row in db.query(SoftwareFieldValue).filter(SoftwareFieldValue.license_id == license_id).all()
    }
    for field in payload:
        if field.field_id in existing:
            existing[field.field_id].value = field.value
        else:
            db.add(SoftwareFieldValue(license_id=license_id, field_id=field.field_id, value=field.value))
    db.commit()
    return db.query(SoftwareFieldValue).filter(SoftwareFieldValue.license_id == license_id).all()
