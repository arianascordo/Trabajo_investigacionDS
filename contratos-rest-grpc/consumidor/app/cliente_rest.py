"""Cliente REST del consumidor Solicitudes y despacho (M5)."""
import os
from typing import Any

import requests


URL_REST = os.getenv(
    "REST_URL",
    "http://localhost:8000/api/v1/conductores/cercanos",
)

TOKEN_FIJO = os.getenv("TOKEN_FIJO", "token-de-prueba")


class ClienteDisponibilidad:
    """Consume la API REST de Ubicación y disponibilidad (M4).

    La usan las pruebas de contrato con Pact (Actividad 7).
    """

    RUTA_CONDUCTORES_CERCANOS = "/api/v1/conductores/cercanos"

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        timeout: float = 5.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def consultar_conductores_cercanos(
        self,
        lat_origen: float,
        lon_origen: float,
        radio_km: float = 5,
        tipo_vehiculo: str | None = None,
    ) -> dict[str, Any]:
        """Consulta los conductores cercanos y devuelve el JSON recibido."""
        parametros: dict[str, Any] = {
            "lat_origen": lat_origen,
            "lon_origen": lon_origen,
            "radio_km": radio_km,
        }
        if tipo_vehiculo is not None:
            parametros["tipo_vehiculo"] = tipo_vehiculo

        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        respuesta = requests.get(
            f"{self.base_url}{self.RUTA_CONDUCTORES_CERCANOS}",
            params=parametros,
            headers=headers,
            timeout=self.timeout,
        )
        respuesta.raise_for_status()
        return respuesta.json()


def consultar_disponibilidad(
    lat_origen: float,
    lon_origen: float,
    radio_km: float,
    tipo_vehiculo: str,
) -> dict:
    """Consulta conductores cercanos mediante la API REST.

    La usa el simulador de carga (Actividad 6): además del JSON,
    devuelve el tamaño en bytes de la respuesta.
    """

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