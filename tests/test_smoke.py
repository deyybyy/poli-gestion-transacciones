"""
Pruebas "smoke" sencillas.
 
Simulacion de tests, no prueban lógica concreta de negocio.
Creado para simular un paso extra en el pipeline de despliegue.

"""
from app.core.enums import EstadoTransaccion
from app.main import app


def test_suma_basica() -> None:
    """Prueba trivial: confirma que pytest se ejecuta en el CI."""
    assert 1 + 1 == 2


def test_la_app_se_importa() -> None:
    """La aplicación FastAPI se importa y tiene un título configurado."""
    assert app.title != ""


def test_estados_de_transaccion() -> None:
    """El ciclo de estados de una transacción tiene los 4 valores esperados."""
    estados = {estado.value for estado in EstadoTransaccion}
    assert estados == {"PENDIENTE", "APROBADA", "RECHAZADA", "REVERSADA"}
