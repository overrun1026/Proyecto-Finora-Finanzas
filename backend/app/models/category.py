"""
Representa las categorías utilizadas para clasificar los movimientos financieros.
El campo kind indica si la categoría admite ingresos, gastos o ambos.
Las categorías pueden desactivarse para conservar el historial existente.
"""

from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class Category(Base):
    __tablename__ = "categories"

    __table_args__ = (
        CheckConstraint(
            "kind IN ('income', 'expense', 'both')",
            name="ck_categories_kind",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(80), unique=True, index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(
        String(10), default="both", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")