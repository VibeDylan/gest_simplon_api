"""
Routes d'authentification.

Connexion, changement de mot de passe.
"""
from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Connexion : renvoie un JWT et l'indication must_change_password."""
    return service.login(request)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    request: ChangePasswordRequest,
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Change le mot de passe de l'utilisateur courant.

    Nécessite un header Authorization: Bearer <token>.
    """
    service.change_password(current_user, request)
    return None