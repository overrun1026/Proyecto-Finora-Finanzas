"""
Define la estructura de respuesta del resumen financiero.
Incluye ingresos, gastos, balance y cantidad de movimientos.
Los importes se representan como Decimal para conservar precisión monetaria.
"""

from decimal import Decimal

from pydantic import BaseModel


class FinanceSummary(BaseModel):
    currency: str = "COP"
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    transaction_count: int