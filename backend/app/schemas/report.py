"""
Define los formatos de respuesta de los informes.
Cada fila mensual contiene ingresos, gastos y balance del periodo.
El informe de categorías muestra el total gastado en cada una.
"""

from decimal import Decimal

from pydantic import BaseModel


class MonthlyReportRow(BaseModel):
    year: int
    month: int
    income: Decimal
    expenses: Decimal
    balance: Decimal


class CategoryExpenseRow(BaseModel):
    category_id: int | None
    category_name: str
    total: Decimal