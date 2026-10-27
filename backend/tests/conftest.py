"""
Configura las fixtures compartidas por las pruebas automatizadas.
Utiliza SQLite en memoria para no modificar la base de datos real.
Crea y elimina las tablas temporales para cada prueba.
"""

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database.base import Base
from backend.app.database.session import get_db
from backend.app.main import app

# Importar todos los modelos para registrarlos en Base.metadata.
from backend.app.models import (
    Category,
    Transaction,
    Budget,
    SavingsGoal,
    SavingsContribution,
)


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=TEST_ENGINE,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=TEST_ENGINE)

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=TEST_ENGINE)