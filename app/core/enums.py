"""Enumeraciones del dominio."""

from enum import StrEnum


class EstadoTransaccion(StrEnum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    REVERSADA = "REVERSADA"
