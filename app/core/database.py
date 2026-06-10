"""Configuración de la capa de persistencia (SQLAlchemy 2.0)."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping evita usar conexiones muertas (clave en entornos productivos
# donde la BD puede reiniciarse). pool_recycle renueva conexiones longevas.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM."""


def get_db() -> Generator[Session]:
    """Dependencia de FastAPI que entrega una sesión y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
