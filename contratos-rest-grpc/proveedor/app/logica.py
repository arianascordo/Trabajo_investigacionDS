import os

from datos import buscar_conductores_cercanos

# Actividad 8: cambio intencional para demostrar que Pact detecta la ruptura.
# Con PROVEEDOR_INCOMPATIBLE=true el campo "conductor_id" se renombra a
# "id_conductor", que es justo el tipo de cambio que rompería a M5.
INCOMPATIBLE = os.getenv("PROVEEDOR_INCOMPATIBLE", "false").lower() == "true"
CAMPO_ID = "id_conductor" if INCOMPATIBLE else "conductor_id"

def consultar_disponibilidad(latitud, longitud, tipo_vehiculo, radio_km):

    conductores_cercanos = buscar_conductores_cercanos(
        latitud,
        longitud,
        tipo_vehiculo,
        radio_km
    )

    conductores_resultado = []

    for conductor in conductores_cercanos:
        distancia = conductor["distancia_origen_km"]
        eta = max(1, round(distancia * 3))

        conductores_resultado.append({
            CAMPO_ID: conductor["conductor_id"],
            "tipo_vehiculo": conductor["tipo_vehiculo"],
            "distancia_km": distancia,
            "eta_minutos": eta,
            "timestamp_ubicacion": conductor["timestamp_ubicacion"]
        })

    return {
        "total": len(conductores_resultado),
        "conductores": conductores_resultado
    }
