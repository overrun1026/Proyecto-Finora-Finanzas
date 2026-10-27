"""
Contiene las validaciones básicas de nombres de categorías.
Elimina espacios al principio y al final del texto.
Rechaza nombres vacíos para mantener datos consistentes.
"""

from backend.app.core.exceptions import ValidationError


def normalize_category_name(name: str) -> str:
    normalized = name.strip()

    if not normalized:
        raise ValidationError(
            "El nombre de la categoría no puede estar vacío."
        )

    return normalized