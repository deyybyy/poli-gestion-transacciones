"""Esquemas Pydantic para Transaccion."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import EstadoTransaccion

Monto = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2, examples=["50000.00"])]


class TransaccionCrear(BaseModel):
    commerce_id: int = Field(..., gt=0)
    amount: Monto
    currency: str = Field("COP", min_length=3, max_length=3)
    description: str | None = Field(None, max_length=255)
    reference: str | None = Field(
        None, max_length=60, description="Si no se envía, se genera automáticamente."
    )


class CambioEstado(BaseModel):
    estado: EstadoTransaccion


class TransaccionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    commerce_id: int
    reference: str
    amount: Decimal
    currency: str
    status: EstadoTransaccion
    description: str | None
    created_at: datetime
    updated_at: datetime


class ResumenCommerce(BaseModel):
    commerce_id: int
    name: str
    total_transacciones: int
    total_aprobado: Decimal
    conteo_por_estado: dict[str, int]
