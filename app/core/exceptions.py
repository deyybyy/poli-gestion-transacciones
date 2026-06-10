"""Excepciones de dominio.

Mantienen la lógica de negocio desacoplada del transporte HTTP. Los
manejadores registrados en main.py las traducen a respuestas HTTP.
"""


class DominioError(Exception):
    """Excepción base del dominio."""


class EntidadNoEncontrada(DominioError):
    def __init__(self, entidad: str, identificador: object) -> None:
        self.entidad = entidad
        self.identificador = identificador
        super().__init__(f"{entidad} con identificador '{identificador}' no encontrado.")


class ReglaDeNegocioInvalida(DominioError):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
