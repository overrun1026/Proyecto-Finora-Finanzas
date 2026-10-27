"""
Expone las rutas HTTP para administrar categorías.
Permite listar categorías activas, crear nuevas, editarlas y eliminarlas.
Las reglas de duplicados y protección del historial están en CategoryService.
"""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryRead,
)
from backend.app.services.category_service import CategoryService


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("", response_model=list[CategoryRead])
def list_categories(
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return CategoryService(db).list(active_only)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
):
    return CategoryService(db).create(data)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
):
    return CategoryService(db).update(category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    CategoryService(db).delete(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)