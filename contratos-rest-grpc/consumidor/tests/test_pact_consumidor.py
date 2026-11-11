"""Contrato Pact del consumidor Solicitudes y despacho frente a M4."""
from pathlib import Path

import pytest
from pact import Pact, match

from app.cliente_rest import ClienteDisponibilidad


DIRECTORIO_PACTS = Path(__file__).parent / "pacts"


@pytest.fixture
def pact():
    """Crea el contrato y guarda el JSON al finalizar la prueba."""
    contrato = Pact(
        "solicitudes-despacho",
        "ubicacion-disponibilidad",
    ).with_specification("V4")

    yield contrato

    contrato.write_file(DIRECTORIO_PACTS, overwrite=True)


def test_consultar_conductores_cercanos(pact):
    """El cliente envía los parámetros esperados y procesa la respuesta."""
    token_prueba = "token-de-prueba"

    respuesta_esperada = {
        "total": match.int(1),
        "conductores": match.each_like(
            {
                "conductor_id": match.str("001"),
                "tipo_vehiculo": match.regex(
                    "AUTO",
                    regex=r"^(AUTO|MOTO)$",
                ),
                "distancia_km": match.float(0.12),
                "eta_minutos": match.int(1),
                # El proveedor actual devuelve fecha y hora sin zona horaria.
                "timestamp_ubicacion": match.datetime(
                    "2026-11-11T10:30:00",
                    format="%Y-%m-%dT%H:%M:%S",
                ),
            },
            min=1,
        ),
    }

    (
        pact.upon_receiving(
            "una consulta de conductores cercanos con resultado disponible"
        )
        .given("hay al menos un conductor disponible dentro del radio")
        .with_request("GET", "/api/v1/conductores/cercanos")
        .with_query_parameter("lat_origen", -27.4511)
        .with_query_parameter("lon_origen", -58.9867)
        .with_query_parameter("radio_km", 5)
        .with_query_parameter("tipo_vehiculo", "AUTO")
        .with_header("Accept", "application/json")
        .with_header("Authorization", f"Bearer {token_prueba}")
        .will_respond_with(200)
        .with_body(respuesta_esperada, content_type="application/json")
    )

    with pact.serve() as servidor_simulado:
        cliente = ClienteDisponibilidad(
            base_url=str(servidor_simulado.url),
            token=token_prueba,
        )

        resultado = cliente.consultar_conductores_cercanos(
            lat_origen=-27.4511,
            lon_origen=-58.9867,
            radio_km=5,
            tipo_vehiculo="AUTO",
        )

    assert resultado["total"] == len(resultado["conductores"])
    assert resultado["total"] >= 1
    assert isinstance(resultado["conductores"][0]["conductor_id"], str)
    assert resultado["conductores"][0]["tipo_vehiculo"] == "AUTO"
