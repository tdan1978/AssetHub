from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.schemas.common import Page, Message
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=Page[UserOut])
def list_users(page: int = 1, size: int = 20, db: Session = Depends(get_db), _: object = Depends(require_role("super_admin"))):
    query = db.query(User).filter(User.is_deleted == False)
    total, items = paginate(query.order_by(User.id.desc()), page, size)
    return Page(total=total, items=items)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: object = Depends(require_role("super_admin"))):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: object = Depends(require_role("super_admin"))):
    exists = db.query(User).filter(User.username == payload.username, User.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username exists")
    user = User(
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role_id=payload.role_id,
        dept=payload.dept,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin")),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("super_admin")),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_deleted = True
    db.commit()
    return Message(message="Deleted")
