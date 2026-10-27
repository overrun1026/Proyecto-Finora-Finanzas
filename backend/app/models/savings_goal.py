"""
Representa una meta de ahorro personal.
Guarda el importe objetivo y, opcionalmente, una fecha límite y notas.
Los aportes asociados se almacenan por separado en SavingsContribution.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    __table_args__ = (
        CheckConstraint(
            "target_amount > 0",
            name="ck_savings_target_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    contributions = relationship(
        "SavingsContribution",
        back_populates="goal",
        cascade="all, delete-orphan",
    )