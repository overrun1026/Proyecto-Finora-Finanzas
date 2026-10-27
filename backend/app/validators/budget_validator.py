"""
Valida las categorías que pueden utilizarse en presupuestos.
Solo permite categorías activas compatibles con gastos.
Las comprobaciones de duplicados se realizan en el servicio y la base de datos.
"""

from sqlalchemy.orm import Session

from backend.app.core.exceptions import ValidationError
from backend.app.models.category import Category


def validate_budget_category(
    db: Session,
    category_id: int,
) -> Category:
    category = db.get(Category, category_id)

    if category is None or not category.is_active:
        raise ValidationError(
            "La categoría no existe o está inactiva."
        )

    if category.kind not in ("expense", "both"):
        raise ValidationError(
            "Los presupuestos solo pueden utilizar categorías de gasto."
        )

    return category