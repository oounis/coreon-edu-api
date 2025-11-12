from typing import Optional, Callable, Iterable
from datetime import datetime, timedelta
import os

from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError

SECRET_KEY = os.getenv("SECRET_KEY", "coreon_secret")
ALGORITHM = "HS256"
DEFAULT_TTL_HOURS = int(os.getenv("JWT_TTL_HOURS", "8"))

def create_access_token(sub: str, role: str, ttl_hours: Optional[int] = None) -> str:
    expire = datetime.utcnow() + timedelta(hours=ttl_hours or DEFAULT_TTL_HOURS)
    payload = {"sub": sub, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token_or_none(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    claims = decode_token_or_none(token)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return claims  # { sub: username, role: role, exp: ... }

def require_roles(*roles: Iterable[str]) -> Callable:
    roles_set = set(roles)
    def _dependency(user: dict = Depends(get_current_user)):
        if "role" not in user or user["role"] not in roles_set:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        return user
    return _dependency
