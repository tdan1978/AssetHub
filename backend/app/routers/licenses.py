from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, get_current_user
from app.models.license import License
from app.schemas.license import LicenseCreate, LicenseOut
from app.schemas.common import Page
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/licenses", tags=["licenses"])


@router.get("", response_model=Page[LicenseOut])
def list_licenses(page: int = 1, size: int = 20, db: Session = Depends(get_db), _: object = Depends(get_current_user)):
    query = db.query(License)
    total, items = paginate(query.order_by(License.id.desc()), page, size)
    return Page(total=total, items=items)


@router.post("", response_model=LicenseOut)
def create_license(
    payload: LicenseCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = License(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{license_id}", response_model=LicenseOut)
def update_license(
    license_id: int,
    payload: LicenseCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin", "asset_admin")),
):
    item = db.query(License).filter(License.id == license_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="License not found")
    data = payload.model_dump()
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{license_id}")
def delete_license(
    license_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin")),
):
    item = db.query(License).filter(License.id == license_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="License not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
