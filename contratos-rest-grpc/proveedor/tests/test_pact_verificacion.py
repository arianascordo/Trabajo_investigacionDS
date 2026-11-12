import os
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from pact import Verifier

NOMBRE_PROVEEDOR = "ubicacion-disponibilidad"
NOMBRE_CONTRATO = "solicitudes-despacho-ubicacion-disponibilidad.json"

DIRECTORIO_TESTS = Path(__file__).resolve().parent
DIRECTORIO_PACTS_LOCAL = (
    DIRECTORIO_TESTS.parent.parent / "consumidor" / "tests" / "pacts"
)


def _ruta_contrato() -> Path:
    directorio = Path(os.getenv("PACT_DIR", DIRECTORIO_PACTS_LOCAL))
    contrato = directorio / NOMBRE_CONTRATO
    if not contrato.exists():
        pytest.fail(
            f"No se encontró el contrato en {contrato}. "
            "Primero hay que correr el test del consumidor (Actividad 7)."
        )
    return contrato

def _agregar_app_al_path() -> None:
    for candidata in (DIRECTORIO_TESTS.parent / "app", DIRECTORIO_TESTS.parent):
        if (candidata / "servidor_rest.py").exists():
            sys.path.insert(0, str(candidata))
            return
    pytest.fail("No se encontró servidor_rest.py para levantar el proveedor.")


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def url_proveedor():
    """Devuelve la URL del proveedor a verificar (externo o levantado acá)."""
    url_externa = os.getenv("PROVEEDOR_URL")
    if url_externa:
        yield url_externa
        return

    import uvicorn

    _agregar_app_al_path()
    from servidor_rest import app

    puerto = _puerto_libre()
    servidor = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=puerto, log_level="warning")
    )
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()

    limite = time.time() + 10
    while not servidor.started:
        if time.time() > limite:
            pytest.fail("El servidor REST no arrancó a tiempo.")
        time.sleep(0.05)

    yield f"http://127.0.0.1:{puerto}"

    servidor.should_exit = True
    hilo.join(timeout=5)


def estado_conductor_disponible(action: str = "setup", parameters=None) -> None:
    """Estado 'hay al menos un conductor disponible dentro del radio'.
    El proveedor usa datos en memoria (datos.py) y el conductor 001 ya cumple
    la condición, así que no hay que preparar nada. En un servicio con base de
    datos, acá se insertaría el conductor de prueba.
    """


def test_proveedor_cumple_contrato_con_consumidor(url_proveedor):
    """M4 responde lo que M5 espera según el contrato de Pact."""
    verificador = (
        Verifier(NOMBRE_PROVEEDOR, host=urlsplit(url_proveedor).hostname)
        .add_source(_ruta_contrato())
        .add_transport(url=url_proveedor)
        .state_handler(
            {
                "hay al menos un conductor disponible dentro del radio":
                    estado_conductor_disponible,
            }
        )
    )

    verificador.verify()
