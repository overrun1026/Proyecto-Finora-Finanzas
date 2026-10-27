"""
Define los esquemas para crear, actualizar y consultar categorías.
Limita el tipo de categoría a ingresos, gastos o ambos.
Las respuestas incluyen el identificador de la categoría.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    kind: Literal["income", "expense", "both"] = "both"
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None, min_length=1, max_length=80
    )
    kind: Literal["income", "expense", "both"] | None = None
    is_active: bool | None = None


class CategoryRead(CategoryCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)