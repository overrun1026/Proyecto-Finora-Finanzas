
"""
Define la fábrica de sesiones de SQLAlchemy.
Proporciona una sesión de base de datos a cada solicitud de FastAPI.
Cierra la sesión al terminar la petición, incluso si ocurre un error.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from backend.app.database.connection import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
