"""
Expone los modelos de base de datos desde un punto común.
Facilita el registro de todas las tablas en SQLAlchemy.
"""

from backend.app.models.category import Category
from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget
from backend.app.models.savings_goal import SavingsGoal
from backend.app.models.savings_contribution import SavingsContribution

__all__ = [
    "Category",
    "Transaction",
    "Budget",
    "SavingsGoal",
    "SavingsContribution",
]