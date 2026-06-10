"""Repositorio: acceso a datos de Transaccion."""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import EstadoTransaccion
from app.models import Transaction


class TransaccionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, transaccion: Transaction) -> Transaction:
        self.db.add(transaccion)
        self.db.commit()
        self.db.refresh(transaccion)
        return transaccion

    def obtener_por_id(self, transaccion_id: int) -> Transaction | None:
        return self.db.get(Transaction, transaccion_id)

    def obtener_por_reference(self, reference: str) -> Transaction | None:
        return self.db.scalar(select(Transaction).where(Transaction.reference == reference))

    def listar(
        self,
        commerce_id: int | None = None,
        estado: EstadoTransaccion | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Transaction]:
        stmt = select(Transaction)
        if commerce_id is not None:
            stmt = stmt.where(Transaction.commerce_id == commerce_id)
        if estado is not None:
            stmt = stmt.where(Transaction.estado == estado)
        stmt = stmt.order_by(Transaction.creada_en.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def guardar(self, transaccion: Transaction) -> Transaction:
        self.db.commit()
        self.db.refresh(transaccion)
        return transaccion

    def resumen_por_comercio(self, commerce_id: int) -> tuple[int, Decimal, dict[str, int]]:
        """Devuelve (total_transactions, total_aprobado, conteo_por_estado)."""
        total_aprobado = self.db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.commerce_id == commerce_id,
                Transaction.estado == EstadoTransaccion.APROBADA,
            )
        )
        filas = self.db.execute(
            select(Transaction.estado, func.count())
            .where(Transaction.commerce_id == commerce_id)
            .group_by(Transaction.estado)
        ).all()
        conteo = {estado.value: cantidad for estado, cantidad in filas}
        total = sum(conteo.values())
        return total, Decimal(total_aprobado or 0), conteo
