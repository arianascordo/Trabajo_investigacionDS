# Pact: lado consumidor

Esta implementación corresponde al consumidor **Solicitudes y despacho (M5)**,
que consulta al proveedor **Ubicación y disponibilidad (M4)** mediante REST.

## Interacción definida

- Método: `GET`
- Ruta: `/api/v1/conductores/cercanos`
- Query: `lat_origen`, `lon_origen`, `radio_km` y `tipo_vehiculo`.
- Header esperado: `Accept: application/json` y `Authorization: Bearer ...`.
- Estado esperado: `200`.
- Respuesta: objeto JSON con `total` y `conductores`.
- Cada conductor contiene `conductor_id`, `tipo_vehiculo`, `distancia_km`,
  `eta_minutos` y `timestamp_ubicacion`.

Los matchers de Pact validan tipos y formatos, sin fijar todos los valores
dinámicos de la respuesta. El estado `given` documenta que hay al menos un
conductor disponible dentro del radio.

## Instalación y ejecución

Desde la carpeta `contratos-rest-grpc/consumidor`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

En Windows, la activación del entorno virtual es:

```powershell
.venv\Scripts\Activate.ps1
```

La prueba levanta un proveedor simulado de Pact. **No hace falta iniciar el
servidor real** para ejecutar el test del consumidor.

Al finalizar correctamente, Pact genera el contrato JSON en:

`tests/pacts/solicitudes-despacho-ubicacion-disponibilidad.json`

Ese archivo debe compartirse con el equipo que implementa la verificación del
proveedor. No se debe editar manualmente: se regenera ejecutando la prueba.

## Observaciones para coordinar con el proveedor

1. OpenAPI declara autenticación Bearer, pero el `servidor_rest.py` actual no
   valida el header. El consumidor lo envía porque forma parte del contrato
   publicado en OpenAPI.
2. El esquema OpenAPI muestra un timestamp con zona horaria (`Z`), mientras
   que los datos actuales del proveedor usan `YYYY-MM-DDTHH:MM:SS` sin zona.
   El matcher de este contrato refleja el formato que devuelve hoy el código
   del proveedor. Conviene acordar un formato RFC 3339 y alinear ambos lados.
3. El contrato de esta actividad cubre la interacción REST. El cliente gRPC
   existente queda fuera de este test.

## Qué demuestra la prueba

- El consumidor usa el método, ruta, parámetros y headers declarados.
- La respuesta contiene los campos que necesita el consumidor.
- Los tipos y formatos importantes se verifican mediante matchers.
- Pact genera un JSON reutilizable por el equipo proveedor.
