"""
Centraliza las consultas y operaciones de persistencia de transacciones.
Permite filtrar movimientos y paginar los resultados.
Los servicios utilizan este repositorio para acceder a los datos.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, transaction_id: int):
        return self.db.get(Transaction, transaction_id)

    def list(
        self,
        *,
        kind=None,
        category_id=None,
        date_from=None,
        date_to=None,
        min_amount=None,
        max_amount=None,
        limit=50,
        offset=0,
    ):
        stmt = select(Transaction)

        if kind:
            stmt = stmt.where(Transaction.kind == kind)

        if category_id is not None:
            stmt = stmt.where(
                Transaction.category_id == category_id
            )

        if date_from:
            stmt = stmt.where(
                Transaction.transaction_date >= date_from
            )

        if date_to:
            stmt = stmt.where(
                Transaction.transaction_date <= date_to
            )

        if min_amount is not None:
            stmt = stmt.where(Transaction.amount >= min_amount)

        if max_amount is not None:
            stmt = stmt.where(Transaction.amount <= max_amount)

        stmt = stmt.order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc(),
        )

        stmt = stmt.offset(offset).limit(limit)

        return list(self.db.scalars(stmt).all())

    def add(self, transaction: Transaction):
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, transaction: Transaction):
        self.db.delete(transaction)
        self.db.commit()