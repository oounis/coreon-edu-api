from fastapi import APIRouter, Depends
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

router = APIRouter(prefix="/admin-test", tags=["AdminTest"])

@router.get("/secure")
def secure_check(user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN))):
    return {"status": "ok", "message": "You are allowed"}
