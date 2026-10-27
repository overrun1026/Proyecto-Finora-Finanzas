
"""
Centraliza la configuración de Personal Finance API.
Lee las variables de entorno y los valores del archivo .env.
DATABASE_URL determina cómo se conecta SQLAlchemy a PostgreSQL.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Finance API"
    app_version: str = "1.0.0"
    app_description: str = (
        "API REST para administrar ingresos, gastos y presupuestos personales."
    )

    database_url: str = (
        "postgresql+psycopg://finance_user:local_dev_password"
        "@localhost:5432/personal_finance"
    )

    sql_echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
