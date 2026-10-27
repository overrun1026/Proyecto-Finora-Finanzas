"""
Crea el esquema inicial de Personal Finance API.
Usa la metadata SQLAlchemy para crear las tablas registradas.
Esta revisión sirve como punto de partida de las migraciones del proyecto.
"""

from alembic import op

from backend.app.database.base import Base
from backend.app.models import (
    Category,
    Transaction,
    Budget,
    SavingsGoal,
    SavingsContribution,
)


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())