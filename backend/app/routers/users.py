from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import require_permission
from app.core.security import hash_password
from app.models.asset import Asset
from app.models.asset_log import AssetLog
from app.models.user import User
from app.models.role import Role
from app.models.stocktake import Stocktake
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.schemas.common import Page, Message
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=Page[UserOut])
def list_users(page: int = 1, size: int = 20, db: Session = Depends(get_db), _: object = Depends(require_permission("users", "view"))):
    query = db.query(User).options(joinedload(User.roles)).filter(User.is_deleted == False)
    total, items = paginate(query.order_by(User.id.desc()), page, size)
    return Page(total=total, items=items)


@router.get("/options")
def list_user_options(
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("users", "view")),
):
    items = (
        db.query(User.id, User.full_name, User.username)
        .filter(User.is_deleted == False, User.is_active == True)
        .order_by(User.id.desc())
        .all()
    )
    return [
        {
            "value": item.id,
            "label": item.full_name or item.username,
        }
        for item in items
    ]


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: object = Depends(require_permission("users", "view"))):
    user = (
        db.query(User)
        .options(joinedload(User.roles))
        .filter(User.id == user_id, User.is_deleted == False)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: object = Depends(require_permission("users", "create"))):
    exists = db.query(User).filter(User.username == payload.username, User.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username exists")
    if not payload.role_ids:
        raise HTTPException(status_code=400, detail="Role required")
    roles = db.query(Role).filter(Role.id.in_(payload.role_ids), Role.is_deleted == False).all()
    if len(roles) != len(set(payload.role_ids)):
        raise HTTPException(status_code=400, detail="Role not found")
    primary_role_id = roles[0].id
    user = User(
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role_id=primary_role_id,
        dept=payload.dept,
        phone=payload.phone,
        wecom_name=payload.wecom_name,
    )
    db.add(user)
    db.commit()
    user.roles = roles
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("users", "update")),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    role_ids = data.pop("role_ids", None)
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))
    for key, value in data.items():
        setattr(user, key, value)
    if role_ids is not None:
        if not role_ids:
            raise HTTPException(status_code=400, detail="Role required")
        roles = db.query(Role).filter(Role.id.in_(role_ids), Role.is_deleted == False).all()
        if len(roles) != len(set(role_ids)):
            raise HTTPException(status_code=400, detail="Role not found")
        user.roles = roles
        user.role_id = roles[0].id
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("users", "delete")),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    has_logs = db.query(AssetLog.id).filter(AssetLog.operator_id == user_id).first()
    if has_logs:
        raise HTTPException(status_code=400, detail="User has asset logs, cannot delete")
    has_stocktakes = db.query(Stocktake.id).filter(Stocktake.created_by == user_id).first()
    if has_stocktakes:
        raise HTTPException(status_code=400, detail="User has stocktakes, cannot delete")
    db.query(Asset).filter(Asset.user_id == user_id).update({Asset.user_id: None}, synchronize_session=False)
    user.roles = []
    db.delete(user)
    db.commit()
    return Message(message="Deleted")
