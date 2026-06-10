"""Esquemas Pydantic para Commerce."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommerceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, examples=["Tienda La 14"])
    nit: str = Field(..., min_length=5, max_length=30, examples=["900123456-7"])


class CreateCommerce(CommerceBase):
    pass


class CommerceActualizar(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    active: bool | None = None


class CommerceResponse(CommerceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
