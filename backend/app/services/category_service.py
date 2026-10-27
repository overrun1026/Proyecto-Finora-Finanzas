"""
Implementa las reglas de negocio para administrar categorías.
Normaliza los nombres y comprueba que no existan duplicados.
Evita eliminar categorías que ya están asociadas a transacciones.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    ConflictError,
    NotFoundError,
)
from backend.app.models.category import Category
from backend.app.models.transaction import Transaction
from backend.app.repositories.category_repository import CategoryRepository
from backend.app.validators.category_validator import normalize_category_name


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoryRepository(db)

    def list(self, active_only: bool = False):
        return self.repo.list(active_only)

    def create(self, data):
        name = normalize_category_name(data.name)

        if self.repo.name_exists(name):
            raise ConflictError(
                "Ya existe una categoría con ese nombre."
            )

        category = Category(
            name=name,
            kind=data.kind,
            is_active=data.is_active,
        )

        return self.repo.save(category)

    def update(self, category_id: int, data):
        category = self.repo.get(category_id)

        if category is None:
            raise NotFoundError("Categoría no encontrada.")

        changes = data.model_dump(exclude_unset=True)

        if "name" in changes and changes["name"] is not None:
            name = normalize_category_name(changes["name"])

            if self.repo.name_exists(name, exclude_id=category_id):
                raise ConflictError(
                    "Ya existe una categoría con ese nombre."
                )

            changes["name"] = name

        for field, value in changes.items():
            setattr(category, field, value)

        return self.repo.save(category)

    def delete(self, category_id: int):
        category = self.repo.get(category_id)

        if category is None:
            raise NotFoundError("Categoría no encontrada.")

        stmt = (
            select(Transaction.id)
            .where(Transaction.category_id == category_id)
            .limit(1)
        )

        if self.db.scalar(stmt) is not None:
            raise ConflictError(
                "La categoría tiene transacciones; "
                "desactívala para conservar el historial."
            )

        self.repo.delete(category)