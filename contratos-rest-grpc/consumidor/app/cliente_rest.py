"""Cliente REST del consumidor Solicitudes y despacho (M5)."""
from typing import Any

import requests


class ClienteDisponibilidad:
    """Consume la API REST de Ubicación y disponibilidad (M4)."""

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
