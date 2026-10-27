"""
Expone el resumen financiero de la API.
Permite consultar los totales generales o los de un rango de fechas.
Los cálculos se delegan al servicio financiero.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.finance import FinanceSummary
from backend.app.services.finance_service import FinanceService


router = APIRouter(
    prefix="/finance",
    tags=["Finance"],
)


@router.get("/summary", response_model=FinanceSummary)
def finance_summary(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=422,
            detail="date_from no puede ser posterior a date_to.",
        )

    return FinanceService(db).summary(date_from, date_to)