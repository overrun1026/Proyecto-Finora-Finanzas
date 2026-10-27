"""
Representa el presupuesto mensual de una categoría de gasto.
Guarda el año, el mes y el límite monetario establecido.
El gasto consumido se calcula a partir de las transacciones registradas.
"""

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "year",
            "month",
            name="uq_budget_category_period",
        ),
        CheckConstraint(
            "amount_limit > 0",
            name="ck_budget_limit_positive",
        ),
        CheckConstraint(
            "month BETWEEN 1 AND 12",
            name="ck_budget_month",
        ),
        CheckConstraint(
            "year >= 2000",
            name="ck_budget_year",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(nullable=False)
    month: Mapped[int] = mapped_column(nullable=False)
    amount_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    category = relationship("Category", back_populates="budgets")