from datos import buscar_conductores_cercanos

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
            "conductor_id": conductor["conductor_id"],
            "tipo_vehiculo": conductor["tipo_vehiculo"],
            "distancia_km": distancia,
            "eta_minutos": eta,
            "timestamp_ubicacion": conductor["timestamp_ubicacion"]
        })

    return {
        "total": len(conductores_resultado),
        "conductores": conductores_resultado
    }
