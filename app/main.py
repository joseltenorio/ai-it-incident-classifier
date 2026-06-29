# app/main.py

from fastapi import FastAPI

from app.api.routes_health import router as health_router
from app.config import settings

# FastAPI creates the ASGI application object used by Uvicorn.
# The metadata below is also displayed in the automatic /docs page.
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Classifies IT support incidents with generative AI and stores "
        "results on Google Cloud for operational analysis."
    ),
)

# Routers are registered here so main.py stays as the application entry point,
# while endpoint definitions remain organized in dedicated route modules.
app.include_router(health_router)