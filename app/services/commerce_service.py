"""Servicio: lógica de negocio de Commerce."""

from app.core.exceptions import EntidadNoEncontrada, ReglaDeNegocioInvalida
from app.models import Commerce
from app.repositories.commerce_repository import CommerceRepository
from app.schemas.commerce import CommerceActualizar, CreateCommerce


class CommerceService:
    def __init__(self, repo: CommerceRepository) -> None:
        self.repo = repo

    def crear(self, datos: CreateCommerce) -> Commerce:
        if self.repo.obtener_por_nit(datos.nit):
            raise ReglaDeNegocioInvalida(f"Ya existe un commerce con NIT '{datos.nit}'.")
        commerce = Commerce(name=datos.name, nit=datos.nit)
        return self.repo.crear(commerce)

    def obtener(self, commerce_id: int) -> Commerce:
        commerce = self.repo.obtener_por_id(commerce_id)
        if commerce is None:
            raise EntidadNoEncontrada("Commerce", commerce_id)
        return commerce

    def listar(self, skip: int = 0, limit: int = 50) -> list[Commerce]:
        return self.repo.listar(skip, limit)

    def actualizar(self, commerce_id: int, datos: CommerceActualizar) -> Commerce:
        commerce:Commerce = self.obtener(commerce_id)
        if not commerce:
            raise EntidadNoEncontrada("Commerce", commerce_id)
        if not commerce.active:
            raise ReglaDeNegocioInvalida("No se puede actualizar un commerce inactivo.")
        if datos.name is not None:
            commerce.name = datos.name
        if datos.active is not None:
            commerce.active = datos.active
        return self.repo.guardar(commerce)
