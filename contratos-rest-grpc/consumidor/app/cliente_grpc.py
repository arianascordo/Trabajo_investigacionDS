import os
import sys
from pathlib import Path

import grpc

# Los archivos generados están en app/. Esta ruta también permite que el
# módulo generado encuentre disponibilidad_pb2 al importarlo desde el simulador.
RUTA_APP = str(Path(__file__).resolve().parent)
if RUTA_APP not in sys.path:
    sys.path.insert(0, RUTA_APP)

import disponibilidad_pb2 as pb2
import disponibilidad_pb2_grpc as pb2_grpc


GRPC_TARGET = os.getenv("GRPC_TARGET", "localhost:50051")
TOKEN_FIJO = os.getenv("TOKEN_FIJO", "token-de-prueba")

TIPOS_VEHICULO = {
    "AUTO": pb2.AUTO,
    "MOTO": pb2.MOTO,
}


def consultar_disponibilidad(
    lat_origen: float,
    lon_origen: float,
    radio_km: float,
    tipo_vehiculo: str,
) -> dict:
    """Consulta conductores cercanos mediante gRPC."""

    tipo_normalizado = tipo_vehiculo.upper()

    if tipo_normalizado not in TIPOS_VEHICULO:
        raise ValueError("tipo_vehiculo debe ser 'AUTO' o 'MOTO'")

    solicitud = pb2.ConsultaDisponibilidadRequest(
        lat_origen=lat_origen,
        lon_origen=lon_origen,
        radio_km=radio_km,
        tipo_vehiculo=TIPOS_VEHICULO[tipo_normalizado],
    )

    metadata = (
        ("authorization", f"Bearer {TOKEN_FIJO}"),
    )

    with grpc.insecure_channel(GRPC_TARGET) as canal:
        stub = pb2_grpc.DisponibilidadServiceStub(canal)
        respuesta = stub.ConsultarDisponibilidad(
            solicitud,
            timeout=5,
            metadata=metadata,
        )

    return {
        "datos": respuesta,
        "bytes_respuesta": respuesta.ByteSize(),
    }