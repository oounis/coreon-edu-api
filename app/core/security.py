from datetime import datetime, timedelta, timezone
from typing import Optional
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models

# --- JWT / Crypto config ---
SECRET_KEY = os.getenv("SECRET_KEY", "coreon_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_TTL_HOURS", "8"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This tells FastAPI how to read "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# --- Password helpers ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT helpers ---
def create_access_token(sub: str, role: str, expires_hours: Optional[int] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours or ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": sub, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Current user + RBAC ---
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    payload = decode_access_token(token)
    sub = payload.get("sub")

    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(*allowed_roles: str):
    """
    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
        async def admin_only(...):
            ...
    """

    def dependency(current_user: models.User = Depends(get_current_user)) -> models.User:
        if not allowed_roles:
            return current_user

        if getattr(current_user, "role", None) not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dependency

# --- Compatibility function for audit_mw ---
def decode_token_or_none(token: str):
    """
    Older audit middleware expects this helper.
    For backward compatibility, we keep it simple:
    - Return decoded payload if valid
    - Return None on ANY error without raising
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None

# --- Backward compatibility: require_roles (plural) ---
def require_roles(*roles: str):
    """
    Legacy alias that behaves exactly like require_role.
    Allows importing either name without breaking old routes.
    """
    return require_role(*roles)

