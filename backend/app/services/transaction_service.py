"""
Implementa las reglas de negocio para las transacciones.
Valida categorías, filtros y existencia de registros.
Coordina las operaciones de creación, actualización y eliminación.
"""

from sqlalchemy.orm import Session

from backend.app.core.exceptions import NotFoundError, ValidationError
from backend.app.models.transaction import Transaction
from backend.app.repositories.transaction_repository import TransactionRepository
from backend.app.validators.transaction_validator import (
    validate_category_for_kind,
)


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TransactionRepository(db)

    def list(self, **filters):
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise ValidationError(
                "date_from no puede ser posterior a date_to."
            )

        min_amount = filters.get("min_amount")
        max_amount = filters.get("max_amount")

        if (
            min_amount is not None
            and max_amount is not None
            and min_amount > max_amount
        ):
            raise ValidationError(
                "min_amount no puede superar max_amount."
            )

        return self.repo.list(**filters)

    def get(self, transaction_id: int):
        transaction = self.repo.get(transaction_id)

        if transaction is None:
            raise NotFoundError("Transacción no encontrada.")

        return transaction

    def create(self, data):
        validate_category_for_kind(
            self.db,
            data.category_id,
            data.kind,
        )

        transaction = Transaction(**data.model_dump())
        return self.repo.add(transaction)

    def update(self, transaction_id: int, data):
        transaction = self.get(transaction_id)
        changes = data.model_dump(exclude_unset=True)

        kind = changes.get("kind", transaction.kind)
        category_id = changes.get(
            "category_id",
            transaction.category_id,
        )

        validate_category_for_kind(
            self.db,
            category_id,
            kind,
        )

        for field, value in changes.items():
            setattr(transaction, field, value)

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def delete(self, transaction_id: int):
        transaction = self.get(transaction_id)
        self.repo.delete(transaction)