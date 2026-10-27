"""
Centraliza las operaciones de persistencia de presupuestos.
Permite filtrar los presupuestos por año y mes.
Las reglas de negocio y los cálculos se implementan en BudgetService.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.budget import Budget


class BudgetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, budget_id: int):
        return self.db.get(Budget, budget_id)

    def list(self, year=None, month=None):
        stmt = select(Budget).order_by(
            Budget.year.desc(),
            Budget.month.desc(),
        )

        if year is not None:
            stmt = stmt.where(Budget.year == year)

        if month is not None:
            stmt = stmt.where(Budget.month == month)

        return list(self.db.scalars(stmt).all())

    def period_exists(
        self,
        category_id: int,
        year: int,
        month: int,
        exclude_id=None,
    ):
        stmt = select(Budget.id).where(
            Budget.category_id == category_id,
            Budget.year == year,
            Budget.month == month,
        )

        if exclude_id is not None:
            stmt = stmt.where(Budget.id != exclude_id)

        return self.db.scalar(stmt) is not None

    def save(self, budget: Budget):
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete(self, budget: Budget):
        self.db.delete(budget)
        self.db.commit()