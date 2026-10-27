"""
Representa un aporte individual a una meta de ahorro.
Guarda el importe, la fecha del aporte y una nota opcional.
Los aportes se mantienen separados de las transacciones de ingresos y gastos.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class SavingsContribution(Base):
    __tablename__ = "savings_contributions"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_contribution_amount_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    goal_id: Mapped[int] = mapped_column(
        ForeignKey("savings_goals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    contribution_date: Mapped[date] = mapped_column(
        Date, default=date.today, nullable=False
    )
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)

    goal = relationship("SavingsGoal", back_populates="contributions")