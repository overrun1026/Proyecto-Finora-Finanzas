"""
Define la clase base de los modelos SQLAlchemy.
Todos los modelos heredan de esta clase para registrar sus tablas.
Los modelos se importan desde los módulos que necesitan su metadata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass