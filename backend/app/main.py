"""
Crea la aplicación FastAPI y registra sus rutas.
Convierte las excepciones de negocio en respuestas HTTP consistentes.
Expone endpoints de salud y documentación interactiva.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)

# Importar los modelos registra sus tablas en Base.metadata.
from backend.app.models import category, transaction, budget
from backend.app.models import savings_goal, savings_contribution

from backend.app.api.routes import (
    transactions,
    categories,
    finance,
    reports,
    budgets,
    savings_goals,
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)


for route_module in (
    transactions,
    categories,
    finance,
    reports,
    budgets,
    savings_goals,
):
    app.include_router(
        route_module.router,
        prefix="/api/v1",
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(
    request: Request,
    exc: NotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(ConflictError)
async def conflict_handler(
    request: Request,
    exc: ConflictError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


@app.exception_handler(ValidationError)
async def validation_handler(
    request: Request,
    exc: ValidationError,
):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


@app.get("/", tags=["Health"])
def root():
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "api_prefix": "/api/v1",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}