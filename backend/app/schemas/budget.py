"""
Define los esquemas para los presupuestos mensuales.
Valida categoría, periodo e importe límite antes de procesar la solicitud.
El estado incluye gasto acumulado, saldo disponible y porcentaje utilizado.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    category_id: int = Field(gt=0)
    year: int = Field(ge=2000, le=2200)
    month: int = Field(ge=1, le=12)
    amount_limit: Decimal = Field(
        gt=0, max_digits=12, decimal_places=2
    )


class BudgetUpdate(BaseModel):
    amount_limit: Decimal = Field(
        gt=0, max_digits=12, decimal_places=2
    )


class BudgetRead(BudgetCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BudgetStatus(BaseModel):
    id: int
    category_id: int
    category_name: str
    year: int
    month: int
    amount_limit: Decimal
    spent: Decimal
    remaining: Decimal
    percent_used: Decimal