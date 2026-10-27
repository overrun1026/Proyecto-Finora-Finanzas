"""
Expone las rutas HTTP para administrar presupuestos mensuales.
Permite filtrar por año y mes y consultar el estado del presupuesto.
Los cálculos de gasto y porcentaje se realizan en BudgetService.
"""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.budget import (
    BudgetCreate,
    BudgetRead,
    BudgetUpdate,
    BudgetStatus,
)
from backend.app.services.budget_service import BudgetService


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
)


@router.get("", response_model=list[BudgetStatus])
def list_budgets(
    year: int | None = Query(default=None, ge=2000, le=2200),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
):
    return BudgetService(db).list_status(year, month)


@router.post(
    "",
    response_model=BudgetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_budget(
    data: BudgetCreate,
    db: Session = Depends(get_db),
):
    return BudgetService(db).create(data)


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    db: Session = Depends(get_db),
):
    return BudgetService(db).update(budget_id, data)


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
):
    BudgetService(db).delete(budget_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)