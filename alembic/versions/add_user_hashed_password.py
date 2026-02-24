"""Ajout de la colonne hashed_password à la table users.

Revision ID: a1b2c3d4e5f6
Revises: 3b3b56bd9b9d
Create Date: 2026-02-23

"""
from typing import Sequence, Union

import bcrypt
from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "3b3b56bd9b9d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("hashed_password", sa.String(), nullable=True),
    )
    placeholder = bcrypt.hashpw(b"CHANGE_ME", bcrypt.gensalt()).decode("utf-8")
    op.execute(
        sa.text("UPDATE users SET hashed_password = :h WHERE hashed_password IS NULL").bindparams(
            h=placeholder
        )
    )
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
