"""
Point d'entrée de l'API GestSimplon.

Expose l'application FastAPI et les routes racines.
Documentation interactive : /docs (Swagger), /redoc.
"""
from fastapi import FastAPI

app = FastAPI(
    title="GestSimplon API",
    description="API REST pour la gestion de formations, sessions et inscriptions (apprenants / formateurs).",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Health check / racine de l'API. Retourne un message de bienvenue."""
    return {"message": "Hello, World!"}