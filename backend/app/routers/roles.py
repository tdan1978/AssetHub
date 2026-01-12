from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.role import Role
from app.schemas.role import RoleOut

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


@router.get("", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db), _: object = Depends(get_current_user)):
    return db.query(Role).filter(Role.is_deleted == False).all()
