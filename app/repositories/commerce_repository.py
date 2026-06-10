"""Repositorio: acceso a datos de Commerce."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Commerce


class CommerceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, commerce: Commerce) -> Commerce:
        self.db.add(commerce)
        self.db.commit()
        self.db.refresh(commerce)
        return commerce

    def obtener_por_id(self, commerce_id: int) -> Commerce | None:
        return self.db.get(Commerce, commerce_id)

    def obtener_por_nit(self, nit: str) -> Commerce | None:
        return self.db.scalar(select(Commerce).where(Commerce.nit == nit))

    def listar(self, skip: int = 0, limit: int = 50) -> list[Commerce]:
        stmt = select(Commerce).order_by(Commerce.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def guardar(self, commerce: Commerce) -> Commerce:
        self.db.commit()
        self.db.refresh(commerce)
        return commerce
