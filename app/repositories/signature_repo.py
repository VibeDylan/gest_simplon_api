"""
Repository pour l'émargement (signatures).

Création, lecture, listes par session+date et par session+user.
Vérification d'existence (session_id, user_id, date) pour éviter les doublons.
"""
from datetime import date, datetime, time
from typing import List, Optional

from sqlmodel import Session, select

from app.models.signature import Signature


class SignatureRepository:
    """
    Accès données pour les signatures (pad d'émargement).

    Une signature = un jour signé pour (session_id, user_id).
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, session_id: int, user_id: int, sign_date: date) -> Signature:
        """Crée une signature (date stockée à 00:00:00). Retourne l'instance avec id."""
        dt = datetime.combine(sign_date, time.min)
        sig = Signature(session_id=session_id, user_id=user_id, date=dt)
        self.session.add(sig)
        self.session.commit()
        self.session.refresh(sig)
        return sig

    def get_by_id(self, id: int) -> Optional[Signature]:
        """Retourne la signature d'id donné ou None."""
        return self.session.get(Signature, id)

    def exists_for_date(self, session_id: int, user_id: int, sign_date: date) -> bool:
        """True si une signature existe déjà pour (session_id, user_id, sign_date)."""
        dt = datetime.combine(sign_date, time.min)
        return (
            self.session.exec(
                select(Signature).where(
                    Signature.session_id == session_id,
                    Signature.user_id == user_id,
                    Signature.date == dt,
                )
            ).first()
            is not None
        )

    def list_by_session_and_date(self, session_id: int, sign_date: date) -> List[Signature]:
        """Liste toutes les signatures pour une session et un jour donnés."""
        dt = datetime.combine(sign_date, time.min)
        return list(
            self.session.exec(
                select(Signature).where(
                    Signature.session_id == session_id,
                    Signature.date == dt,
                )
            ).all()
        )

    def list_by_session_and_user(self, session_id: int, user_id: int) -> List[Signature]:
        """Liste toutes les dates signées par un utilisateur pour une session (historique pad)."""
        return list(
            self.session.exec(
                select(Signature)
                .where(
                    Signature.session_id == session_id,
                    Signature.user_id == user_id,
                )
                .order_by(Signature.date)
            ).all()
        )
