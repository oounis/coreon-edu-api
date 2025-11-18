from contextvars import ContextVar

tenant_id_ctx = ContextVar("tenant_id", default=None)

def set_tenant(school_id: int):
    tenant_id_ctx.set(school_id)

def get_tenant() -> int | None:
    return tenant_id_ctx.get()
