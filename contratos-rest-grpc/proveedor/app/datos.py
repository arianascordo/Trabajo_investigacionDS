from math import sqrt

conductores = [
    {
        "conductor_id": "001",
        "latitud": -27.451,
        "longitud": -58.986,
        "tipo_vehiculo": "AUTO",
        "activo": True,
        "disponible": True,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:30:00"
    },
    {
        "conductor_id": "002",
        "latitud": -27.455,
        "longitud": -58.989,
        "tipo_vehiculo": "MOTO",
        "activo": True,
        "disponible": True,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:32:00"
    },
    {
        "conductor_id": "003",
        "latitud": -27.470,
        "longitud": -58.986,
        "tipo_vehiculo": "AUTO",
        "activo": True,
        "disponible": False,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:35:00"
    },
    {
        "conductor_id": "004",
        "latitud": -27.432,
        "longitud": -58.986,
        "tipo_vehiculo": "AUTO",
        "activo": True,
        "disponible": True,
        "reservado": True,
        "timestamp_ubicacion": "2026-11-11T10:40:00"
    },
    {
        "conductor_id": "005",
        "latitud": -27.451,
        "longitud": -59.040,
        "tipo_vehiculo": "MOTO",
        "activo": True,
        "disponible": True,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:42:00"
    },
    {
        "conductor_id": "006",
        "latitud": -27.451,
        "longitud": -58.930,
        "tipo_vehiculo": "AUTO",
        "activo": True,
        "disponible": True,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:45:00"
    },
    {
        "conductor_id": "007",
        "latitud": -27.540,
        "longitud": -58.986,
        "tipo_vehiculo": "AUTO",
        "activo": False,
        "disponible": True,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:48:00"
    },
    {
        "conductor_id": "008",
        "latitud": -27.451,
        "longitud": -58.870,
        "tipo_vehiculo": "MOTO",
        "activo": True,
        "disponible": True,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:50:00"
    },
    {
        "conductor_id": "009",
        "latitud": -27.650,
        "longitud": -58.986,
        "tipo_vehiculo": "AUTO",
        "activo": True,
        "disponible": True,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:52:00"
    },
    {
        "conductor_id": "010",
        "latitud": -27.451,
        "longitud": -58.700,
        "tipo_vehiculo": "MOTO",
        "activo": True,
        "disponible": False,
        "reservado": False,
        "timestamp_ubicacion": "2026-11-11T10:55:00"
    }
]

def calcular_distancia(lat1, lon1, lat2, lon2):
    diferencia_lat = (lat2 - lat1) * 111.32
    diferencia_lon = (lon2 - lon1) * 111.32

    return sqrt(diferencia_lat**2 + diferencia_lon**2)

def buscar_conductores_cercanos(lat_origen, lon_origen, tipo_vehiculo, radio_km):
    resultados = []
    for conductor in conductores:

        if not conductor["activo"]:
            continue

        if not conductor["disponible"]:
            continue

        if conductor["reservado"]:
            continue

        if tipo_vehiculo is not None and conductor["tipo_vehiculo"] != tipo_vehiculo:
            continue

        distancia = calcular_distancia(
            lat_origen,
            lon_origen,
            conductor["latitud"],
            conductor["longitud"]
        )

        if distancia <= radio_km:
            conductor_resultado = conductor.copy()
            conductor_resultado["distancia_origen_km"] = round(distancia, 2)

            resultados.append(conductor_resultado)

    resultados.sort(key=lambda c: c["distancia_origen_km"])

    return resultados[:5]
