
"""
Crea el motor de SQLAlchemy para conectarse a PostgreSQL.
Usa la URL definida en la configuración de la aplicación.
Comprueba las conexiones reutilizadas antes de utilizarlas.
"""

from sqlalchemy import create_engine

from backend.app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.sql_echo,
)
