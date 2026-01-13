from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password, create_access_token, hash_password
from app.models.user import User
from app.models.role import Role
from app.schemas.common import Token, Message

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username, User.is_deleted == False).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"user_id": user.id, "username": user.username, "role_code": user.role.code})
    return Token(access_token=token)


@router.post("/init", response_model=Message)
def init_system(db: Session = Depends(get_db)):
    roles = [
        ("超级管理员", "super_admin"),
        ("资产管理员", "asset_admin"),
        ("财务审计", "auditor"),
        ("普通员工", "employee"),
    ]
    for name, code in roles:
        exists = db.query(Role).filter(Role.code == code).first()
        if not exists:
            db.add(Role(name=name, code=code))
    db.commit()

    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        role = db.query(Role).filter(Role.code == "super_admin").first()
        db.add(
            User(
                username="admin",
                full_name="系统管理员",
                password_hash=hash_password("admin123"),
                role_id=role.id,
                dept="IT",
            )
        )
        db.commit()
    return Message(message="Initialized")


@router.post("/change-password", response_model=Message)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return Message(message="Password updated")
