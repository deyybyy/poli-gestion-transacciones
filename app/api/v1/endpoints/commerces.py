"""Endpoints de Commerces."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_comercio_service
from app.schemas.commerce import (
    CommerceActualizar,
    CreateCommerce,
    CommerceResponse,
)
from app.services.commerce_service import CommerceService

router = APIRouter(prefix="/commerces", tags=["Commerces"])


@router.post("", response_model=CommerceResponse, status_code=status.HTTP_201_CREATED)
def crear_comercio(
    datos: CreateCommerce,
    service: CommerceService = Depends(get_comercio_service),
) -> CommerceResponse:
    return service.crear(datos)


@router.get("", response_model=list[CommerceResponse])
def listar_comercios(
    skip: int = 0,
    limit: int = 50,
    service: CommerceService = Depends(get_comercio_service),
) -> list[CommerceResponse]:
    return service.listar(skip, limit)


@router.get("/{commerce_id}", response_model=CommerceResponse)
def obtener_comercio(
    commerce_id: int,
    service: CommerceService = Depends(get_comercio_service),
) -> CommerceResponse:
    return service.obtener(commerce_id)


@router.patch("/{commerce_id}", response_model=CommerceResponse)
def actualizar_comercio(
    commerce_id: int,
    datos: CommerceActualizar,
    service: CommerceService = Depends(get_comercio_service),
) -> CommerceResponse:
    return service.actualizar(commerce_id, datos)
