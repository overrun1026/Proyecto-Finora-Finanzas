"""
Define los esquemas de metas de ahorro y de sus aportes.
Valida importes, nombres, fechas y notas opcionales.
El esquema de respuesta de la meta incluye los cálculos del progreso.
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target_amount: Decimal = Field(
        gt=0, max_digits=12, decimal_places=2
    )
    deadline: date | None = None
    notes: str | None = Field(default=None, max_length=500)


class SavingsGoalUpdate(BaseModel):
    name: str | None = Field(
        default=None, min_length=1, max_length=120
    )
    target_amount: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    deadline: date | None = None
    notes: str | None = Field(default=None, max_length=500)


class SavingsContributionCreate(BaseModel):
    amount: Decimal = Field(
        gt=0, max_digits=12, decimal_places=2
    )
    contribution_date: date = Field(default_factory=date.today)
    note: str | None = Field(default=None, max_length=300)


class SavingsContributionRead(SavingsContributionCreate):
    id: int
    goal_id: int

    model_config = ConfigDict(from_attributes=True)


class SavingsGoalRead(SavingsGoalCreate):
    id: int
    saved_amount: Decimal = Decimal("0.00")
    remaining_amount: Decimal = Decimal("0.00")
    percent_complete: Decimal = Decimal("0.00")

    model_config = ConfigDict(from_attributes=True)