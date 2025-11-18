from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.tenancy.tenant_context import set_tenant

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        school_id = request.headers.get("X-School-ID")
        if school_id:
            try:
                set_tenant(int(school_id))
            except:
                pass
        response = await call_next(request)
        return response
