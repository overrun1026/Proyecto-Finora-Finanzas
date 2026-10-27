"""
Expone las rutas HTTP para administrar transacciones.
Permite crear, consultar, filtrar, actualizar y eliminar movimientos.
Los servicios aplican las reglas de negocio y acceden a la base de datos.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionRead,
)
from backend.app.services.transaction_service import TransactionService


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    kind: Literal["income", "expense"] | None = None,
    category_id: int | None = Query(default=None, gt=0),
    date_from: date | None = None,
    date_to: date | None = None,
    min_amount: Decimal | None = Query(default=None, ge=0),
    max_amount: Decimal | None = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return TransactionService(db).list(
        kind=kind,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
):
    return TransactionService(db).create(data)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    return TransactionService(db).get(transaction_id)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
):
    return TransactionService(db).update(transaction_id, data)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    TransactionService(db).delete(transaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)