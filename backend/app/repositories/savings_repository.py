"""
Centraliza la persistencia de metas de ahorro y sus aportes.
Permite consultar metas, sumar contribuciones y recuperar su historial.
No convierte los aportes en transacciones de ingresos.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.savings_goal import SavingsGoal
from backend.app.models.savings_contribution import SavingsContribution


class SavingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_goal(self, goal_id: int):
        return self.db.get(SavingsGoal, goal_id)

    def list_goals(self):
        stmt = select(SavingsGoal).order_by(
            SavingsGoal.id.desc()
        )
        return list(self.db.scalars(stmt).all())

    def saved_total(self, goal_id: int):
        stmt = (
            select(func.coalesce(func.sum(SavingsContribution.amount), 0))
            .where(SavingsContribution.goal_id == goal_id)
        )
        return self.db.scalar(stmt)

    def list_contributions(self, goal_id: int):
        stmt = (
            select(SavingsContribution)
            .where(SavingsContribution.goal_id == goal_id)
            .order_by(
                SavingsContribution.contribution_date.desc(),
                SavingsContribution.id.desc(),
            )
        )
        return list(self.db.scalars(stmt).all())

    def save_goal(self, goal: SavingsGoal):
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete_goal(self, goal: SavingsGoal):
        self.db.delete(goal)
        self.db.commit()

    def save_contribution(
        self,
        contribution: SavingsContribution,
    ):
        self.db.add(contribution)
        self.db.commit()
        self.db.refresh(contribution)
        return contribution