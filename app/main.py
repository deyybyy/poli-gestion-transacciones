"""Punto de entrada de la aplicación FastAPI."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text

import app.models  # noqa: F401  (registra los modelos en el metadata)
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.exceptions import EntidadNoEncontrada, ReglaDeNegocioInvalida

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")
settings = get_settings()


def _esperar_base_de_datos(reintentos: int = 10, espera: float = 3.0) -> None:
    """Reintenta la conexión a la BD (la BD puede tardar en arrancar)."""
    for intento in range(1, reintentos + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Conexión con la base de datos establecida.")
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning("BD no disponible (intento %s/%s): %s", intento, reintentos, exc)
            time.sleep(espera)
    raise RuntimeError("No fue posible conectar con la base de datos.")


def _sembrar_datos_demo() -> None:
    """Inserta un commerce de ejemplo solo en desarrollo."""
    from app.models import Commerce

    with SessionLocal() as db:
        if db.scalar(select(Commerce)) is None:
            db.add(Commerce(name="Commerce Demo", nit="900000000-1"))
            db.commit()
            logger.info("Datos de demostración insertados.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _esperar_base_de_datos()
    # En producción se recomienda usar migraciones (Alembic) en lugar de create_all.
    Base.metadata.create_all(bind=engine)
    if settings.app_env == "development":
        _sembrar_datos_demo()
    yield
    logger.info("Apagando la aplicación.")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "API de gestión de transacciones de pago. "
        "Proyecto del curso de Integración Continua (Docker)."
    ),
    lifespan=lifespan,
)


@app.exception_handler(EntidadNoEncontrada)
async def _manejar_no_encontrada(request: Request, exc: EntidadNoEncontrada):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ReglaDeNegocioInvalida)
async def _manejar_regla(request: Request, exc: ReglaDeNegocioInvalida):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/", tags=["Raíz"])
def raiz() -> dict:
    return {
        "servicio": settings.app_name,
        "version": "1.0.0",
        "documentacion": "/docs",
    }


app.include_router(api_router, prefix="/api/v1")
