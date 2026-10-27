"""
Representa un ingreso o gasto de la persona.
Guarda el importe, la descripción, la fecha y la categoría opcional.
Las restricciones de la base de datos refuerzan las validaciones de la API.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        CheckConstraint(
            "kind IN ('income', 'expense')",
            name="ck_transactions_kind",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_transactions_amount_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    kind: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    transaction_date: Mapped[date] = mapped_column(
        Date, default=date.today, nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    category = relationship("Category", back_populates="transactions")