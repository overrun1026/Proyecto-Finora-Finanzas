# Imagen Python ligera para ejecutar la API.
# Instala dependencias y copia el backend dentro del contenedor.
# Aplica las migraciones antes de iniciar el servidor FastAPI.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

COPY backend/requirements.txt /code/backend/requirements.txt

RUN pip install --no-cache-dir -r /code/backend/requirements.txt

COPY backend /code/backend

EXPOSE 8000

CMD ["sh", "-c", "alembic -c backend/alembic.ini upgrade head && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]