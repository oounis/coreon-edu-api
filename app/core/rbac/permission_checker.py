from fastapi import HTTPException, status, Depends
from app.core.security import get_current_user
from app.core.rbac.role_enums import Role

def require_roles(*allowed_roles: Role):
    def wrapper(user=Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied",
            )
        return user
    return wrapper
