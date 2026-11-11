from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from logica import consultar_disponibilidad

app = FastAPI(title="API de Disponibilidad de Conductores")

@app.get(
    "/api/v1/conductores/cercanos",
    operation_id="consultarConductoresCercanos"
)
def consultar_conductores(
    lat_origen: str = Query(...),
    lon_origen: str = Query(...),
    radio_km: Optional[str] = Query(None),
    tipo_vehiculo: Optional[str] = Query(None)
):
    try:
        lat_origen = float(lat_origen)
        lon_origen = float(lon_origen)
        radio_km = float(radio_km) if radio_km is not None else 5

        if not -90 <= lat_origen <= 90:
            raise ValueError("Latitud fuera de rango")

        if not -180 <= lon_origen <= 180:
            raise ValueError("Longitud fuera de rango")

        if not 0 < radio_km <= 5:
            raise ValueError("El radio debe ser mayor a 0 y máximo 5 km")

        if tipo_vehiculo is not None and tipo_vehiculo not in ("AUTO", "MOTO"):
            raise ValueError("El tipo de vehículo debe ser AUTO o MOTO")

        return consultar_disponibilidad(
            lat_origen,
            lon_origen,
            tipo_vehiculo,
            radio_km
        )

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "codigo": "PARAMETROS_INVALIDOS",
                "mensaje": str(e)
            }
        )