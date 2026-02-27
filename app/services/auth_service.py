"""
Service d'authentification.

Connexion (vérification identifiants + émission JWT), changement de mot de passe.
"""
import bcrypt

from app.core.errors import InvalidCredentials
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import ChangePasswordRequest, LoginRequest, TokenResponse
from app.schemas.user import UserUpdate


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def login(self, request: LoginRequest) -> TokenResponse:
        """Vérifie email/password et renvoie un token + must_change_password."""
        email = request.email.lower().strip()
        user = self.repo.get_by_email(email)
        if not user or not verify_password(request.password, user.hashed_password):
            raise InvalidCredentials()
        token = create_access_token(
            data={"sub": user.id, "role": user.role.value}
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            must_change_password=user.must_change_password,
        )

    def _hash_password(self, password: str) -> str:
        """Hash un mot de passe en utilisant bcrypt."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

    def change_password(self, user: User, request: ChangePasswordRequest) -> None:
        """
        Change le mot de passe de l'utilisateur courant.

        - Met à jour le hash sans redemander l'ancien mot de passe.
        - Passe must_change_password à False.
        """
        new_hashed = self._hash_password(request.new_password)
        update_data = UserUpdate(must_change_password=False)
        self.repo.update(user.id, update_data, hashed_password=new_hashed)
