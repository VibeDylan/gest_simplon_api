"""
Point d'entrée de l'API GestSimplon.

Expose l'application FastAPI et les routes racines.
Documentation interactive : /docs (Swagger), /redoc.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.errors import AppError, EmailAlreadyUsed, UserNotFound

app = FastAPI(
    title="GestSimplon API",
    description="API REST pour la gestion de formations, sessions et inscriptions (apprenants / formateurs).",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Transforme les exceptions métier en JSON { code, message } avec le bon status HTTP."""
    status_code = 500
    if isinstance(exc, UserNotFound):
        status_code = 404
    elif isinstance(exc, EmailAlreadyUsed):
        status_code = 409
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message},
    )