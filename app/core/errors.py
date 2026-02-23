"""
Exceptions métier de l'application (sans code HTTP).

Chaque exception porte un `code` (string stable pour le front) et un `message` lisible.
Le code HTTP est géré au niveau des handlers FastAPI (exception_handler).
"""
from typing import Optional


class AppError(Exception):
    """
    Exception de base pour toutes les erreurs métier.

    Attributes:
        code: Identifiant stable (ex. USER_NOT_FOUND), utile pour le front.
        message: Message lisible pour l'utilisateur ou les logs.
    """

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)


class UserNotFound(AppError):
    """Levée lorsqu'aucun utilisateur ne correspond à l'id ou au critère demandé."""

    code = "USER_NOT_FOUND"

    def __init__(self, message: str = "User not found."):
        super().__init__(code=self.code, message=message)


class EmailAlreadyUsed(AppError):
    """Levée lors d'une création ou mise à jour si l'email est déjà pris."""

    code = "EMAIL_ALREADY_USED"

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "This email is already used."
        super().__init__(code=self.code, message=message)


__all__ = ["AppError", "UserNotFound", "EmailAlreadyUsed"]
