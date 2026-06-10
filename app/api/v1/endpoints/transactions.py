"""Endpoints de transactions y resumen por commerce."""

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_comercio_service, get_transaccion_service
from app.core.enums import EstadoTransaccion
from app.schemas.transaction import (
    CambioEstado,
    ResumenCommerce,
    TransaccionCrear,
    TransaccionRespuesta,
)
from app.services.commerce_service import CommerceService
from app.services.transaction_service import TransaccionService

router = APIRouter(tags=["transactions"])


@router.post(
    "/transactions",
    response_model=TransaccionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_transaccion(
    datos: TransaccionCrear,
    service: TransaccionService = Depends(get_transaccion_service),
) -> TransaccionRespuesta:
    return service.crear(datos)


@router.get("/transactions", response_model=list[TransaccionRespuesta])
def listar_transactions(
    commerce_id: int | None = Query(None, gt=0),
    estado: EstadoTransaccion | None = Query(None),
    skip: int = 0,
    limit: int = 50,
    service: TransaccionService = Depends(get_transaccion_service),
) -> list[TransaccionRespuesta]:
    return service.listar(commerce_id, estado, skip, limit)


@router.get("/transactions/{transaccion_id}", response_model=TransaccionRespuesta)
def obtener_transaccion(
    transaccion_id: int,
    service: TransaccionService = Depends(get_transaccion_service),
) -> TransaccionRespuesta:
    return service.obtener(transaccion_id)


@router.patch(
    "/transactions/{transaccion_id}/estado",
    response_model=TransaccionRespuesta,
)
def cambiar_estado_transaccion(
    transaccion_id: int,
    datos: CambioEstado,
    service: TransaccionService = Depends(get_transaccion_service),
) -> TransaccionRespuesta:
    return service.cambiar_estado(transaccion_id, datos.estado)


@router.get(
    "/commerces/{commerce_id}/resumen",
    response_model=ResumenCommerce,
    tags=["Commerces"],
)
def resumen_comercio(
    commerce_id: int,
    t_service: TransaccionService = Depends(get_transaccion_service),
    c_service: CommerceService = Depends(get_comercio_service),
) -> ResumenCommerce:
    commerce = c_service.obtener(commerce_id)  # lanza 404 si no existe
    total, total_aprobado, conteo = t_service.resumen_por_comercio(commerce_id)
    return ResumenCommerce(
        commerce_id=commerce.id,
        name=commerce.name,
        total_transactions=total,
        total_aprobado=total_aprobado,
        conteo_por_estado=conteo,
    )
