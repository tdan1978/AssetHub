from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.asset import Asset
from app.models.license import License

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), _: object = Depends(get_current_user)):
    total = db.query(Asset).filter(Asset.is_deleted == False).count()
    in_use = db.query(Asset).filter(Asset.is_deleted == False, Asset.status == 1).count()
    repairing = db.query(Asset).filter(Asset.is_deleted == False, Asset.status == 2).count()
    pending_scrap = db.query(Asset).filter(Asset.is_deleted == False, Asset.status == 3).count()

    warn_date = date.today() + timedelta(days=30)
    license_warn = (
        db.query(License)
        .filter(License.expire_at != None, License.expire_at <= warn_date)
        .count()
    )
    return {
        "total": total,
        "in_use_rate": (in_use / total) if total else 0,
        "repairing": repairing,
        "pending_scrap": pending_scrap,
        "license_expire_warn": license_warn,
    }
