"""
Calcula el resumen financiero a partir de las transacciones registradas.
Permite filtrar los resultados por fecha de inicio y fecha de fin.
Los aportes a metas de ahorro no forman parte de los ingresos.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.app.models.transaction import Transaction


class FinanceService:
    def __init__(self, db: Session):
        self.db = db

    def summary(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
    ):
        income_expression = func.coalesce(
            func.sum(
                case(
                    (Transaction.kind == "income", Transaction.amount),
                    else_=0,
                )
            ),
            0,
        )

        expenses_expression = func.coalesce(
            func.sum(
                case(
                    (Transaction.kind == "expense", Transaction.amount),
                    else_=0,
                )
            ),
            0,
        )

        stmt = select(
            income_expression,
            expenses_expression,
            func.count(Transaction.id),
        )

        if date_from:
            stmt = stmt.where(
                Transaction.transaction_date >= date_from
            )

        if date_to:
            stmt = stmt.where(
                Transaction.transaction_date <= date_to
            )

        income, expenses, count = self.db.execute(stmt).one()

        income = Decimal(income)
        expenses = Decimal(expenses)

        return {
            "currency": "COP",
            "total_income": income,
            "total_expenses": expenses,
            "balance": income - expenses,
            "transaction_count": count,
        }