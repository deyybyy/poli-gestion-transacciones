"""Servicio: lógica de negocio de Transaccion."""

import uuid
from decimal import Decimal

from app.core.enums import EstadoTransaccion
from app.core.exceptions import EntidadNoEncontrada, ReglaDeNegocioInvalida
from app.models import Transaction
from app.repositories.commerce_repository import CommerceRepository
from app.repositories.transaction_repository import TransaccionRepository
from app.schemas.transaction import TransaccionCrear

# Máquina de estados: define qué transiciones son válidas desde cada estado.
TRANSICIONES_VALIDAS: dict[EstadoTransaccion, set[EstadoTransaccion]] = {
    EstadoTransaccion.PENDIENTE: {
        EstadoTransaccion.APROBADA,
        EstadoTransaccion.RECHAZADA,
    },
    EstadoTransaccion.APROBADA: {EstadoTransaccion.REVERSADA},
    EstadoTransaccion.RECHAZADA: set(),
    EstadoTransaccion.REVERSADA: set(),
}


class TransaccionService:
    def __init__(self, repo: TransaccionRepository, comercio_repo: CommerceRepository) -> None:
        self.repo = repo
        self.comercio_repo = comercio_repo

    def crear(self, datos: TransaccionCrear) -> Transaction:
        commerce = self.comercio_repo.obtener_por_id(datos.commerce_id)
        if commerce is None:
            raise EntidadNoEncontrada("Commerce", datos.commerce_id)
        if not commerce.active:
            raise ReglaDeNegocioInvalida(
                "No se pueden crear transacciones para un commerce inactivo."
            )

        reference = datos.reference or self._generar_reference()
        if self.repo.obtener_por_reference(reference):
            raise ReglaDeNegocioInvalida(f"La reference '{reference}' ya existe.")

        transaccion = Transaction(
            commerce_id=datos.commerce_id,
            reference=reference,
            amount=str(datos.amount).upper(),
            currency=datos.currency,
            description=datos.description,
            status=EstadoTransaccion.PENDIENTE,
        )
        return self.repo.crear(transaccion)

    def obtener(self, transaccion_id: int) -> Transaction:
        transaccion = self.repo.obtener_por_id(transaccion_id)
        if transaccion is None:
            raise EntidadNoEncontrada("Transaccion", transaccion_id)
        return transaccion

    def listar(
        self,
        commerce_id: int | None = None,
        estado: EstadoTransaccion | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Transaction]:
        return self.repo.listar(commerce_id, estado, skip, limit)

    def cambiar_estado(self, transaccion_id: int, nuevo_estado: EstadoTransaccion) -> Transaction:
        transaccion = self.obtener(transaccion_id)
        permitidos = TRANSICIONES_VALIDAS[transaccion.estado]
        if nuevo_estado not in permitidos:
            raise ReglaDeNegocioInvalida(
                f"Transición no permitida: {transaccion.estado.value} -> {nuevo_estado.value}."
            )
        transaccion.estado = nuevo_estado
        return self.repo.guardar(transaccion)

    def resumen_por_comercio(self, commerce_id: int) -> tuple[int, Decimal, dict[str, int]]:
        return self.repo.resumen_por_comercio(commerce_id)

    @staticmethod
    def _generar_reference() -> str:
        return f"TX-{uuid.uuid4().hex[:12].upper()}"
