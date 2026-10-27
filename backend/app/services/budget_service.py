"""
Administra presupuestos y calcula su consumo mensual.
Suma los gastos de la categoría dentro del mes presupuestado.
Devuelve el límite, el gasto acumulado, el saldo y el porcentaje consumido.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.models.budget import Budget
from backend.app.models.transaction import Transaction
from backend.app.repositories.budget_repository import BudgetRepository
from backend.app.validators.budget_validator import validate_budget_category


class BudgetService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BudgetRepository(db)

    def create(self, data):
        validate_budget_category(self.db, data.category_id)

        if self.repo.period_exists(
            data.category_id,
            data.year,
            data.month,
        ):
            raise ConflictError(
                "Ya existe un presupuesto para esa categoría y periodo."
            )

        budget = Budget(**data.model_dump())
        return self.repo.save(budget)

    def update(self, budget_id: int, data):
        budget = self.repo.get(budget_id)

        if budget is None:
            raise NotFoundError("Presupuesto no encontrado.")

        budget.amount_limit = data.amount_limit
        return self.repo.save(budget)

    def delete(self, budget_id: int):
        budget = self.repo.get(budget_id)

        if budget is None:
            raise NotFoundError("Presupuesto no encontrado.")

        self.repo.delete(budget)

    def list_status(self, year=None, month=None):
        budgets = self.repo.list(year, month)
        output = []

        for budget in budgets:
            start = date(budget.year, budget.month, 1)

            if budget.month == 12:
                end = date(budget.year + 1, 1, 1)
            else:
                end = date(budget.year, budget.month + 1, 1)

            stmt = (
                select(
                    func.coalesce(
                        func.sum(Transaction.amount),
                        0,
                    )
                )
                .where(
                    Transaction.kind == "expense",
                    Transaction.category_id == budget.category_id,
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date < end,
                )
            )

            spent = Decimal(self.db.scalar(stmt))
            limit = Decimal(budget.amount_limit)

            percent_used = (
                spent / limit * Decimal("100")
            ).quantize(Decimal("0.01"))

            output.append(
                {
                    "id": budget.id,
                    "category_id": budget.category_id,
                    "category_name": budget.category.name,
                    "year": budget.year,
                    "month": budget.month,
                    "amount_limit": limit,
                    "spent": spent,
                    "remaining": limit - spent,
                    "percent_used": percent_used,
                }
            )

        return output