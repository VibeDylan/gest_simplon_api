"""
Réexport de BriefStudent (défini dans app.models.brief pour éviter les imports circulaires).
"""
from app.models.brief import BriefStudent

__all__ = ["BriefStudent"]
