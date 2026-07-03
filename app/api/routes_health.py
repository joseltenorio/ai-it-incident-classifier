# app/api/routes_health.py

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.runtime_checks import build_runtime_readiness_report
from app.schemas import RuntimeReadinessResponse

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


@router.get(
    "/ready",
    response_model=RuntimeReadinessResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": RuntimeReadinessResponse,
        },
    },
)
def readiness_check() -> JSONResponse:
    """Return runtime readiness based on configuration checks.

    Unlike /health, this endpoint validates whether required runtime settings
    are present for the selected classifier and persistence configuration.
    """

    report = build_runtime_readiness_report()
    status_code = (
        status.HTTP_200_OK
        if report["status"] == "ready"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(status_code=status_code, content=report)