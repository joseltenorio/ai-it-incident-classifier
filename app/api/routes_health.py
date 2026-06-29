# app/api/routes_health.py

from fastapi import APIRouter

from app.config import settings

# APIRouter groups related endpoints before they are registered in the main app.
# This keeps the API modular as the project grows.
router = APIRouter(tags=["Health"])


@router.get("/")
def read_root() -> dict[str, str]:
    """Return basic service metadata.

    This endpoint is useful for quickly checking that the API is running
    and for exposing the current application name and version.
    """
    return {
        "service": settings.app_name,
        "status": "running",
        "version": settings.app_version,
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the service health status.

    Cloud platforms and developers can use this endpoint to verify that
    the application process is alive and able to respond to HTTP requests.
    """
    return {"status": "healthy"}