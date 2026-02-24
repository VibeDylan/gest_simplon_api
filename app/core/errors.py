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


class FormationNotFound(AppError):
    """Levée lorsqu'aucune formation ne correspond à l'id demandé."""

    code = "FORMATION_NOT_FOUND"

    def __init__(self, message: str = "Formation not found."):
        super().__init__(code=self.code, message=message)


class FormationTitleAlreadyUsed(AppError):
    """Levée lors d'une création ou mise à jour si le titre de formation est déjà utilisé."""

    code = "FORMATION_TITLE_ALREADY_USED"

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "A formation with this title already exists."
        super().__init__(code=self.code, message=message)


class TeacherNotFound(AppError):
    """Levée lorsqu'aucun formateur ne correspond à l'id demandé."""

    code = "TEACHER_NOT_FOUND"

    def __init__(self, message: str = "Teacher not found."):
        super().__init__(code=self.code, message=message)

class UserNotTrainer(AppError):
    """Levée lorsqu'un utilisateur non formateur est tenté d'animer une session."""

    code = "USER_NOT_TRAINER"

    def __init__(self, message: str = "User is not a trainer."):
        super().__init__(code=self.code, message=message)

class SessionStartDateAfterEndDate(AppError):
    """Levée lors d'une création ou mise à jour si la date de début est après la date de fin."""

    code = "SESSION_START_DATE_AFTER_END_DATE"

    def __init__(self, message: str = "Session start date must be before end date."):
        super().__init__(code=self.code, message=message)

class SessionStartDateAlreadyExists(AppError):
    """Levée lors d'une création ou mise à jour si la date de début existe déjà."""

    code = "SESSION_START_DATE_ALREADY_EXISTS"

    def __init__(self, message: str = "Session start date already exists."):
        super().__init__(code=self.code, message=message)

class SessionEndDateAlreadyExists(AppError):
    """Levée lors d'une création ou mise à jour si la date de fin existe déjà."""

    code = "SESSION_END_DATE_ALREADY_EXISTS"

    def __init__(self, message: str = "Session end date already exists."):
        super().__init__(code=self.code, message=message)

class SessionNotFound(AppError):
    """Levée lorsqu'aucune session ne correspond à l'id demandé."""

    code = "SESSION_NOT_FOUND"

    def __init__(self, message: str = "Session not found."):
        super().__init__(code=self.code, message=message)


class EnrollmentNotFound(AppError):
    """Levée lorsqu'aucune inscription ne correspond à l'id ou aux critères demandés."""

    code = "ENROLLMENT_NOT_FOUND"

    def __init__(self, message: str = "Enrollment not found."):
        super().__init__(code=self.code, message=message)


class EnrollmentAlreadyExists(AppError):
    """Levée lors d'une création si l'inscription (session_id, student_id) existe déjà."""

    code = "ENROLLMENT_ALREADY_EXISTS"

    def __init__(self, message: str = "This enrollment already exists."):
        super().__init__(code=self.code, message=message)

class EnrollmentSessionFull(AppError):
    """Levée lors d'une création si la session est pleine."""

    code = "ENROLLMENT_SESSION_FULL"

    def __init__(self, message: str = "This session is full."):
        super().__init__(code=self.code, message=message)

__all__ = [
    "AppError",
    "UserNotFound",
    "EmailAlreadyUsed",
    "FormationNotFound",
    "FormationTitleAlreadyUsed",
    "TeacherNotFound",
    "SessionStartDateAfterEndDate",
    "SessionStartDateAlreadyExists",
    "SessionEndDateAlreadyExists",
    "SessionNotFound",
    "EnrollmentNotFound",
    "EnrollmentAlreadyExists",
    "EnrollmentSessionFull",
]
