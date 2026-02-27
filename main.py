"""
Point d'entrée de l'API GestSimplon.

Expose l'application FastAPI et les routes racines.
Documentation interactive : /docs (Swagger), /redoc.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.errors import (
    AppError,
    BriefNotFound,
    EmailAlreadyUsed,
    EnrollmentAlreadyExists,
    EnrollmentSessionFull,
    FormationNotFound,
    FormationTitleAlreadyUsed,
    GroupNotFound,
    InvalidCredentials,
    SessionEndDateAlreadyExists,
    SessionNotFound,
    SessionStartDateAfterEndDate,
    SessionStartDateAlreadyExists,
    TeacherNotFound,
    UserNotFound,
    UserNotTrainer,
    EnrollmentNotFound,
)

app = FastAPI(
    title="GestSimplon API",
    description="API REST pour la gestion de formations, sessions et inscriptions (apprenants / formateurs).",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


def _format_validation_error_loc(loc: tuple) -> str:
    """Retourne un libellé lisible pour un 'loc' de validation (ex. body → corps, body,email → email)."""
    if not loc:
        return "?"
    if loc == ("body",):
        return "corps de la requête (body)"
    # ("body", "email") → "email", ("body", "nested", "field") → "nested.field"
    return ".".join(str(x) for x in loc if x != "body")


# Messages Pydantic courants → français
_VALIDATION_MSG_FR = {
    "Field required": "Champ requis",
    "field required": "Champ requis",
    "Input should be a valid list": "Doit être une liste",
    "Input should be a valid integer": "Doit être un entier",
    "Input should be a valid string": "Doit être une chaîne de caractères",
    "Value error,": "Valeur invalide",
}


def _translate_validation_message(msg: str) -> str:
    for en, fr in _VALIDATION_MSG_FR.items():
        if msg.lower().startswith(en.lower()) or en.lower() in msg.lower():
            return fr
    return msg


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Reformate les erreurs de validation Pydantic pour indiquer clairement
    les champs manquants ou invalides.
    """
    details = []
    for err in exc.errors():
        loc = err.get("loc", ())
        msg = err.get("msg", "Invalid")
        msg = _translate_validation_message(msg)
        field = _format_validation_error_loc(tuple(loc))
        details.append({"field": field, "message": msg})
    # Message résumé : lister les champs concernés
    fields = [d["field"] for d in details]
    if len(fields) == 1 and "corps de la requête" in fields[0]:
        summary = (
            "Corps de la requête manquant ou invalide. "
            "Envoie un JSON avec l'en-tête Content-Type: application/json."
        )
    elif len(fields) == 1:
        summary = f"Champ invalide ou manquant : {fields[0]}."
    else:
        summary = f"Champs invalides ou manquants : {', '.join(fields)}."
    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": summary,
            "details": details,
        },
    )


@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Transforme les exceptions métier en JSON { code, message } avec le bon status HTTP."""
    status_code = 500
    if isinstance(
        exc,
        (
            UserNotFound,
            FormationNotFound,
            TeacherNotFound,
            SessionNotFound,
            EnrollmentNotFound,
            BriefNotFound,
            GroupNotFound,
        ),
    ):
        status_code = 404
    elif isinstance(exc, (EmailAlreadyUsed, FormationTitleAlreadyUsed, EnrollmentAlreadyExists)):
        status_code = 409
    elif isinstance(exc, InvalidCredentials):
        status_code = 401
    elif isinstance(
        exc,
        (
            SessionStartDateAfterEndDate,
            SessionStartDateAlreadyExists,
            SessionEndDateAlreadyExists,
            UserNotTrainer,
            EnrollmentSessionFull,
        ),
    ):
        status_code = 400
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message},
    )