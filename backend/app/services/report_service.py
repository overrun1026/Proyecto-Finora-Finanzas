"""
Genera informes mensuales y resúmenes de gastos por categoría.
Agrupa las transacciones por periodo o categoría.
Solo utiliza transacciones financieras, sin sumar aportes de ahorro.
"""

from sqlalchemy import case, extract, func, select
from sqlalchemy.orm import Session

from backend.app.models.category import Category
from backend.app.models.transaction import Transaction


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def monthly(self, year: int):
        year_expression = extract(
            "year",
            Transaction.transaction_date,
        )
        month_expression = extract(
            "month",
            Transaction.transaction_date,
        )

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

        stmt = (
            select(
                year_expression.label("year"),
                month_expression.label("month"),
                income_expression.label("income"),
                expenses_expression.label("expenses"),
            )
            .where(year_expression == year)
            .group_by(year_expression, month_expression)
            .order_by(month_expression)
        )

        rows = self.db.execute(stmt).all()

        return [
            {
                "year": int(row.year),
                "month": int(row.month),
                "income": row.income,
                "expenses": row.expenses,
                "balance": row.income - row.expenses,
            }
            for row in rows
        ]

    def expenses_by_category(
        self,
        date_from=None,
        date_to=None,
    ):
        stmt = (
            select(
                Transaction.category_id,
                func.coalesce(
                    Category.name,
                    "Sin categoría",
                ).label("category_name"),
                func.sum(Transaction.amount).label("total"),
            )
            .outerjoin(
                Category,
                Transaction.category_id == Category.id,
            )
            .where(Transaction.kind == "expense")
            .group_by(
                Transaction.category_id,
                Category.name,
            )
            .order_by(func.sum(Transaction.amount).desc())
        )

        if date_from:
            stmt = stmt.where(
                Transaction.transaction_date >= date_from
            )

        if date_to:
            stmt = stmt.where(
                Transaction.transaction_date <= date_to
            )

        rows = self.db.execute(stmt).all()

        return [
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "total": row.total,
            }
            for row in rows
        ]