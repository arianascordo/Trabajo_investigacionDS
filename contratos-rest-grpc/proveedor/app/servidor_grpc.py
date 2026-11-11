from concurrent import futures
from datetime import datetime, timezone
import grpc

from google.protobuf.timestamp_pb2 import Timestamp

import disponibilidad_pb2
import disponibilidad_pb2_grpc

from logica import consultar_disponibilidad


class DisponibilidadServicer(
    disponibilidad_pb2_grpc.DisponibilidadServiceServicer
):

    def ConsultarDisponibilidad(self, request, context):
        try:
            lat_origen = request.lat_origen
            lon_origen = request.lon_origen

            radio_km = (
                request.radio_km
                if request.HasField("radio_km")
                else 5
            )

            tipo_vehiculo = None

            if request.tipo_vehiculo == disponibilidad_pb2.AUTO:
                tipo_vehiculo = "AUTO"

            elif request.tipo_vehiculo == disponibilidad_pb2.MOTO:
                tipo_vehiculo = "MOTO"

            elif request.tipo_vehiculo != disponibilidad_pb2.TIPO_VEHICULO_DESCONOCIDO:
                raise ValueError("Tipo de vehículo inválido")

            if not -90 <= lat_origen <= 90:
                raise ValueError("Latitud fuera de rango")

            if not -180 <= lon_origen <= 180:
                raise ValueError("Longitud fuera de rango")

            if not 0 < radio_km <= 5:
                raise ValueError("El radio debe ser mayor a 0 y máximo 5 km")

            resultado = consultar_disponibilidad(
                lat_origen,
                lon_origen,
                tipo_vehiculo,
                radio_km
            )

            respuesta = disponibilidad_pb2.DisponibilidadResponse(
                total=resultado["total"]
            )

            for conductor in resultado["conductores"]:
                timestamp = datetime.fromisoformat(
                    conductor["timestamp_ubicacion"]
                )

                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)

                timestamp_proto = Timestamp()
                timestamp_proto.FromDatetime(timestamp)

                nuevo_conductor = respuesta.conductores.add()

                nuevo_conductor.conductor_id = conductor["conductor_id"]

                nuevo_conductor.tipo_vehiculo = (
                    disponibilidad_pb2.AUTO
                    if conductor["tipo_vehiculo"] == "AUTO"
                    else disponibilidad_pb2.MOTO
                )

                nuevo_conductor.distancia_km = conductor["distancia_km"]
                nuevo_conductor.eta_minutos = conductor["eta_minutos"]
                nuevo_conductor.timestamp_ubicacion.CopyFrom(timestamp_proto)

            return respuesta

        except ValueError as e:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                str(e)
            )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    disponibilidad_pb2_grpc.add_DisponibilidadServiceServicer_to_server(
        DisponibilidadServicer(),
        server
    )

    server.add_insecure_port("[::]:50051")
    server.start()

    print("Servidor gRPC ejecutándose en el puerto 50051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
