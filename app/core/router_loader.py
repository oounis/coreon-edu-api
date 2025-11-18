import importlib
import pkgutil
from fastapi import FastAPI


def load_all_routers(app: FastAPI):
    """
    Auto-load every router under app.api.v1.* dynamically.
    No manual import list needed in api/v1/__init__.py.
    """
    package_name = "app.api.v1"
    pkg = importlib.import_module(package_name)

    for _, module_name, is_pkg in pkgutil.walk_packages(
        pkg.__path__, pkg.__name__ + "."
    ):
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "router"):
                app.include_router(module.router)
        except Exception as e:
            print(f"[Router Loader] Failed to load {module_name}: {e}")
