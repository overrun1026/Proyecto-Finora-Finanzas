"""
Valida que una transacción utilice una categoría permitida.
Comprueba que la categoría exista, esté activa y admita el tipo de movimiento.
Las transacciones sin categoría siguen estando permitidas.
"""

from sqlalchemy.orm import Session

from backend.app.core.exceptions import ValidationError
from backend.app.models.category import Category


def validate_category_for_kind(
    db: Session,
    category_id: int | None,
    kind: str,
) -> None:
    if category_id is None:
        return

    category = db.get(Category, category_id)

    if category is None or not category.is_active:
        raise ValidationError(
            "La categoría no existe o está inactiva."
        )

    if category.kind not in (kind, "both"):
        raise ValidationError(
            "La categoría no admite este tipo de transacción."
        )