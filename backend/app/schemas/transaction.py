"""
Define los datos de entrada y salida de las transacciones.
Valida importes, tipos, fechas y longitudes de los campos de texto.
La clase de actualización permite modificar campos de forma parcial.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    kind: Literal["income", "expense"]
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str = Field(min_length=1, max_length=200)
    transaction_date: date = Field(default_factory=date.today)
    notes: str | None = Field(default=None, max_length=2000)
    category_id: int | None = Field(default=None, gt=0)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    kind: Literal["income", "expense"] | None = None
    amount: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    description: str | None = Field(
        default=None, min_length=1, max_length=200
    )
    transaction_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)
    category_id: int | None = Field(default=None, gt=0)


class TransactionRead(TransactionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)