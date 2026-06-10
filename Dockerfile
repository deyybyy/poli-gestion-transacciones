# syntax=docker/dockerfile:1

# ---------- Etapa 1: builder ----------
# Instala dependencias en un entorno virtual aislado.
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------- Etapa 2: runtime ----------
# Imagen final ligera, solo con lo necesario para ejecutar.
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Usuario sin privilegios (buena práctica de seguridad: no correr como root).
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --no-create-home appuser

WORKDIR /app

# Copia el entorno virtual desde la etapa builder.
COPY --from=builder /opt/venv /opt/venv

# Copia solo el código de la aplicación.
COPY ./app ./app

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

# Healthcheck a nivel de contenedor (urllib evita depender de curl).
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/v1/health').status==200 else 1)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
