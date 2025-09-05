# ---------------------------
#  Stage 1: Build dependencies (Wheels)
# ---------------------------
FROM python:3.11-slim AS builder

# Evita .pyc y usa stdout directo
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias para compilar librerías (ej: numpy, psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements de producción
COPY requirements.txt .

# Genera wheels (paquetes compilados)
RUN pip install --upgrade pip setuptools wheel \
    && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels


# ---------------------------
#  Stage 2: Runtime
# ---------------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias mínimas (ej: para PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crea usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copia wheels y los instala
COPY --from=builder /wheels /wheels 
RUN pip install --no-cache-dir /wheels/*

# Copia solo el código necesario
COPY .  /app/

# Cambia a usuario no-root
USER appuser

# Expone puerto Uvicorn
EXPOSE 8000

# Arranque con Uvicorn (FastAPI)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]