# Pact: lado proveedor (Actividad 8)

Esta parte corresponde al proveedor **Ubicación y disponibilidad (M4)**. Toma el
contrato que generó el consumidor **Solicitudes y despacho (M5)** en la
Actividad 7 y comprueba que la API REST real lo cumple.

## Qué hace la verificación

El test `tests/test_pact_verificacion.py`:

1. Lee el contrato `solicitudes-despacho-ubicacion-disponibilidad.json`.
2. Prepara el estado del proveedor ("hay al menos un conductor disponible
   dentro del radio"). Con los datos en memoria de `datos.py` el conductor `001`
   ya cumple la condición, así que no hay que preparar nada más.
3. Reproduce la petición del contrato (`GET /api/v1/conductores/cercanos` con
   sus parámetros y headers) contra el servidor REST real.
4. Compara la respuesta con lo que espera el consumidor: status `200`,
   `Content-Type: application/json`, y en el body `total` (entero) y
   `conductores` (al menos uno), cada uno con `conductor_id` (texto),
   `tipo_vehiculo` (`AUTO` o `MOTO`), `distancia_km` (decimal),
   `eta_minutos` (entero) y `timestamp_ubicacion` (`yyyy-MM-ddTHH:mm:ss`).

Si algo no coincide, Pact indica exactamente qué campo falló y el test queda en rojo.

## Variables de entorno

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `PACT_DIR` | Carpeta donde está el JSON del contrato | `../consumidor/tests/pacts` |
| `PROVEEDOR_URL` | URL de un proveedor ya levantado | Sin definir: el test levanta el servidor REST solo, en un puerto libre |
| `PROVEEDOR_INCOMPATIBLE` | `true` activa el cambio intencional en `logica.py` | `false` |
| `PACT_DO_NOT_TRACK` | `true` evita el aviso de estadísticas de Pact | Sin definir |

## Correrlo en local

Desde `contratos-rest-grpc/proveedor`:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Caso de éxito.** El proveedor cumple el contrato:

```bash
pytest -v -s tests/test_pact_verificacion.py
```

**Caso de falla.** Se levanta el proveedor con el cambio intencional:

```bash
PROVEEDOR_INCOMPATIBLE=true pytest -v -s tests/test_pact_verificacion.py
```

En PowerShell:

```powershell
$env:PROVEEDOR_INCOMPATIBLE="true"; pytest -v -s tests/test_pact_verificacion.py
Remove-Item Env:PROVEEDOR_INCOMPATIBLE
```

Salida esperada en el caso de falla:

```
has a matching body (FAILED)

Failures:
1) Verifying a pact between solicitudes-despacho and ubicacion-disponibilidad
   Given hay al menos un conductor disponible dentro del radio - una consulta de conductores cercanos con resultado disponible
    1.1) has a matching body
           $.conductores[0] -> Actual map is missing the following keys: conductor_id
```

También se puede verificar contra un servidor levantado a mano:

```bash
cd app && uvicorn servidor_rest:app --port 8000      # en otra terminal
PROVEEDOR_URL=http://localhost:8000 pytest -v -s tests/test_pact_verificacion.py
```

## El cambio intencional

En `app/logica.py`, con `PROVEEDOR_INCOMPATIBLE=true` el campo `conductor_id`
se devuelve como `id_conductor`. Es un renombre que parece inofensivo del lado
de M4, pero M5 lee `conductor_id` para asignar el viaje, así que en producción
la integración se rompería. Se activa con una variable de entorno para que la
demo muestre los dos casos sin editar código en vivo. El servidor gRPC usa el
mismo nombre de campo interno, así que sigue funcionando en los dos modos.

## Con Docker

Ver la Parte 3 de `demo/guion.md`. El servicio `pact-verificador` monta
`consumidor/tests/pacts` como `/pacts` y verifica contra `proveedor` (correcto)
o contra `proveedor-incompatible` (con el cambio).
