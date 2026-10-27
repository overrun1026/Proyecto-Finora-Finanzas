"""
Expone los informes financieros disponibles.
Permite consultar resultados mensuales y gastos por categoría.
Los informes se generan en ReportService.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.report import (
    MonthlyReportRow,
    CategoryExpenseRow,
)
from backend.app.services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/monthly", response_model=list[MonthlyReportRow])
def monthly_report(
    year: int = Query(ge=2000, le=2200),
    db: Session = Depends(get_db),
):
    return ReportService(db).monthly(year)


@router.get(
    "/expenses-by-category",
    response_model=list[CategoryExpenseRow],
)
def expenses_by_category(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=422,
            detail="date_from no puede ser posterior a date_to.",
        )

    return ReportService(db).expenses_by_category(
        date_from,
        date_to,
    )