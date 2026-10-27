"""
Expone las rutas HTTP para metas de ahorro y sus contribuciones.
Permite crear, consultar, editar y eliminar metas, además de registrar aportes.
El progreso de cada meta se calcula desde los aportes guardados.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.savings_goal import (
    SavingsGoalCreate,
    SavingsGoalUpdate,
    SavingsGoalRead,
    SavingsContributionCreate,
    SavingsContributionRead,
)
from backend.app.services.savings_service import SavingsService


router = APIRouter(
    prefix="/savings-goals",
    tags=["Savings goals"],
)


@router.get("", response_model=list[SavingsGoalRead])
def list_goals(db: Session = Depends(get_db)):
    return SavingsService(db).list_goals()


@router.post(
    "",
    response_model=SavingsGoalRead,
    status_code=status.HTTP_201_CREATED,
)
def create_goal(
    data: SavingsGoalCreate,
    db: Session = Depends(get_db),
):
    return SavingsService(db).create_goal(data)


@router.get("/{goal_id}", response_model=SavingsGoalRead)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
):
    return SavingsService(db).get_goal(goal_id)


@router.patch("/{goal_id}", response_model=SavingsGoalRead)
def update_goal(
    goal_id: int,
    data: SavingsGoalUpdate,
    db: Session = Depends(get_db),
):
    return SavingsService(db).update_goal(goal_id, data)


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
):
    SavingsService(db).delete_goal(goal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{goal_id}/contributions",
    response_model=list[SavingsContributionRead],
)
def list_contributions(
    goal_id: int,
    db: Session = Depends(get_db),
):
    return SavingsService(db).list_contributions(goal_id)


@router.post(
    "/{goal_id}/contributions",
    response_model=SavingsContributionRead,
    status_code=status.HTTP_201_CREATED,
)
def add_contribution(
    goal_id: int,
    data: SavingsContributionCreate,
    db: Session = Depends(get_db),
):
    return SavingsService(db).add_contribution(goal_id, data)