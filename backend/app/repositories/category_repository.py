"""
Centraliza las consultas y operaciones de persistencia de categorías.
Permite listar, buscar, guardar y eliminar categorías.
Incluye una consulta para detectar nombres duplicados.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, category_id: int):
        return self.db.get(Category, category_id)

    def list(self, active_only: bool = False):
        stmt = select(Category).order_by(Category.name)

        if active_only:
            stmt = stmt.where(Category.is_active.is_(True))

        return list(self.db.scalars(stmt).all())

    def name_exists(self, name: str, exclude_id=None):
        stmt = select(Category.id).where(
            Category.name.ilike(name)
        )

        if exclude_id is not None:
            stmt = stmt.where(Category.id != exclude_id)

        return self.db.scalar(stmt) is not None

    def save(self, category: Category):
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category):
        self.db.delete(category)
        self.db.commit()