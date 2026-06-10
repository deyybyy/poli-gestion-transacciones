"""Inyección de dependencias: ensambla repositorios y servicios."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.commerce_repository import CommerceRepository
from app.repositories.transaction_repository import TransaccionRepository
from app.services.commerce_service import CommerceService
from app.services.transaction_service import TransaccionService


def get_comercio_service(db: Session = Depends(get_db)) -> CommerceService:
    return CommerceService(CommerceRepository(db))


def get_transaccion_service(db: Session = Depends(get_db)) -> TransaccionService:
    return TransaccionService(TransaccionRepository(db), CommerceRepository(db))
