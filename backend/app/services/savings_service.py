"""
Administra metas de ahorro y sus contribuciones.
Calcula el progreso de cada meta sumando sus aportes registrados.
Mantiene las contribuciones separadas de los ingresos y gastos habituales.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.core.exceptions import NotFoundError
from backend.app.models.savings_contribution import SavingsContribution
from backend.app.models.savings_goal import SavingsGoal
from backend.app.repositories.savings_repository import SavingsRepository


class SavingsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SavingsRepository(db)

    def _serialize_goal(self, goal):
        saved = Decimal(self.repo.saved_total(goal.id))
        target = Decimal(goal.target_amount)

        remaining = max(
            target - saved,
            Decimal("0.00"),
        )

        percent = min(
            saved / target * Decimal("100"),
            Decimal("100"),
        ).quantize(Decimal("0.01"))

        return {
            "id": goal.id,
            "name": goal.name,
            "target_amount": target,
            "deadline": goal.deadline,
            "notes": goal.notes,
            "saved_amount": saved,
            "remaining_amount": remaining,
            "percent_complete": percent,
        }

    def list_goals(self):
        return [
            self._serialize_goal(goal)
            for goal in self.repo.list_goals()
        ]

    def create_goal(self, data):
        goal = SavingsGoal(**data.model_dump())
        goal = self.repo.save_goal(goal)
        return self._serialize_goal(goal)

    def get_goal(self, goal_id: int):
        goal = self.repo.get_goal(goal_id)

        if goal is None:
            raise NotFoundError("Meta de ahorro no encontrada.")

        return self._serialize_goal(goal)

    def update_goal(self, goal_id: int, data):
        goal = self.repo.get_goal(goal_id)

        if goal is None:
            raise NotFoundError("Meta de ahorro no encontrada.")

        changes = data.model_dump(exclude_unset=True)

        for field, value in changes.items():
            setattr(goal, field, value)

        self.repo.save_goal(goal)
        return self._serialize_goal(goal)

    def delete_goal(self, goal_id: int):
        goal = self.repo.get_goal(goal_id)

        if goal is None:
            raise NotFoundError("Meta de ahorro no encontrada.")

        self.repo.delete_goal(goal)

    def add_contribution(self, goal_id: int, data):
        if self.repo.get_goal(goal_id) is None:
            raise NotFoundError("Meta de ahorro no encontrada.")

        contribution = SavingsContribution(
            goal_id=goal_id,
            **data.model_dump(),
        )

        return self.repo.save_contribution(contribution)

    def list_contributions(self, goal_id: int):
        if self.repo.get_goal(goal_id) is None:
            raise NotFoundError("Meta de ahorro no encontrada.")

        return self.repo.list_contributions(goal_id)