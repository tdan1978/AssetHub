from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.role_permission import RolePermission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = (
        db.query(User)
        .options(joinedload(User.roles), joinedload(User.role))
        .filter(User.id == user_id, User.is_deleted == False)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*role_codes: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role and user.role.is_active and user.role.code in role_codes:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return checker


def require_permission(resource: str, action: str):
    def checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        role_ids = []
        role_codes = []
        if user.role_id and user.role and user.role.is_active:
            role_ids.append(user.role_id)
            role_codes.append(user.role.code)
        if user.roles:
            role_ids.extend([role.id for role in user.roles if role.is_active])
            role_codes.extend([role.code for role in user.roles if role.is_active])
        role_ids = list({rid for rid in role_ids if rid})
        role_codes = list({code for code in role_codes if code})
        if "super_admin" in role_codes:
            return user
        if not role_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        exists = (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id.in_(role_ids),
                RolePermission.resource == resource,
                RolePermission.action == action,
            )
            .first()
        )
        if exists:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return checker


def require_any_permission(perms: list[tuple[str, str]]):
    def checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        role_ids = []
        role_codes = []
        if user.role_id and user.role and user.role.is_active:
            role_ids.append(user.role_id)
            role_codes.append(user.role.code)
        if user.roles:
            role_ids.extend([role.id for role in user.roles if role.is_active])
            role_codes.extend([role.code for role in user.roles if role.is_active])
        role_ids = list({rid for rid in role_ids if rid})
        role_codes = list({code for code in role_codes if code})
        if "super_admin" in role_codes:
            return user
        if not role_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        for resource, action in perms:
            exists = (
                db.query(RolePermission)
                .filter(
                    RolePermission.role_id.in_(role_ids),
                    RolePermission.resource == resource,
                    RolePermission.action == action,
                )
                .first()
            )
            if exists:
                return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return checker


def get_permission_scope(db: Session, user: User, resource: str, action: str) -> str | None:
    role_ids = []
    role_codes = []
    if user.role_id and user.role and user.role.is_active:
        role_ids.append(user.role_id)
        role_codes.append(user.role.code)
    if user.roles:
        role_ids.extend([role.id for role in user.roles if role.is_active])
        role_codes.extend([role.code for role in user.roles if role.is_active])
    role_ids = list({rid for rid in role_ids if rid})
    role_codes = list({code for code in role_codes if code})
    if "super_admin" in role_codes:
        return "all"
    if not role_ids:
        return None
    records = (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id.in_(role_ids),
            RolePermission.resource == resource,
            RolePermission.action == action,
        )
        .all()
    )
    if not records:
        return None
    if any((rec.scope or "all") == "all" for rec in records):
        return "all"
    return "own"
