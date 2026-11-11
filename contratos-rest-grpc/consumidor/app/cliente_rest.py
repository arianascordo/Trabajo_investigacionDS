import os

import requests


URL_REST = os.getenv(
    "REST_URL",
    "http://localhost:8000/api/v1/conductores/cercanos",
)

TOKEN_FIJO = os.getenv("TOKEN_FIJO", "token-de-prueba")


def consultar_disponibilidad(
    lat_origen: float,
    lon_origen: float,
    radio_km: float,
    tipo_vehiculo: str,
) -> dict:
    """Consulta conductores cercanos mediante la API REST."""

    parametros = {
        "lat_origen": lat_origen,
        "lon_origen": lon_origen,
        "radio_km": radio_km,
        "tipo_vehiculo": tipo_vehiculo.upper(),
    }

    encabezados = {
        "Authorization": f"Bearer {TOKEN_FIJO}",
    }

    respuesta = requests.get(
        URL_REST,
        params=parametros,
        headers=encabezados,
        timeout=5,
    )

    # Si el proveedor devuelve un error HTTP, lo informa como excepción.
    respuesta.raise_for_status()

    return {
        "datos": respuesta.json(),
        "bytes_respuesta": len(respuesta.content),
    }