# Actividad 10: Orquestación del entorno y demostración práctica

Todo el escenario corre con `docker-compose.yml` (en la raíz de `contratos-rest-grpc/`).
Este guion dice **qué se muestra, en qué orden y con qué comandos**.

## Qué levanta el docker-compose

| Servicio | Qué es | Actividad | Cuándo se levanta |
|---|---|---|---|
| `proveedor` | M4 Ubicación y disponibilidad. REST en `:8000` y gRPC en `:50051` | 5 | Siempre |
| `consumidor` | Simula M5. Manda la misma carga a REST y a gRPC y guarda el CSV | 6 | Siempre |
| `pact-consumidor` | Corre los tests de Pact del consumidor y genera el JSON en `pacts/` | 7 | Con `--profile pact` |
| `pact-verificador` | Verifica el JSON de `pacts/` contra un proveedor real | 8 | Con `--profile pact` |
| `proveedor-incompatible` | El mismo proveedor con un campo de la respuesta cambiado a propósito | 8 | Con `--profile pact` |

El consumidor encuentra al proveedor por su nombre en la red de Docker (`proveedor:8000` y `proveedor:50051`).
Además, el `healthcheck` hace que el consumidor espere a que los dos puertos del proveedor estén listos antes de arrancar.

---

## Antes de la presentación (preparación, ~5 min)

1. Tener **Docker Desktop abierto** (en Windows, con WSL2).
2. Abrir una terminal en `contratos-rest-grpc/`.
3. Construir las imágenes con anticipación, porque la primera vez tarda en descargar:
   ```bash
   docker compose --profile pact build
   ```
4. Dejar abierta la carpeta `resultados/` en el explorador y el navegador listo.

---

## Parte 1: El servicio expone REST y gRPC a la vez (~2 min)

```bash
docker compose up -d proveedor
docker compose ps          # proveedor debe figurar como "healthy"
```

**Qué mostrar:**
- Abrir **http://localhost:8000/docs**: el Swagger que FastAPI genera a partir del endpoint REST. Ejecutar una consulta desde ahí con `lat_origen=-27.4511`, `lon_origen=-58.9867`, `radio_km=5` y `tipo_vehiculo=AUTO` para mostrar el JSON de respuesta.
- Mostrar lado a lado `contratos/openapi/disponibilidad.yaml` y `contratos/proto/disponibilidad.proto`: son **el mismo conjunto de datos** definido con los dos tipos de contrato.

**Qué decir:** "Es un único servicio con una única lógica (`logica.py`) y dos puertas de entrada: una REST/JSON y una gRPC/Protobuf."

---

## Parte 2: Comparativa de rendimiento en vivo (~3 min)

```bash
docker compose run --rm consumidor
```

Se mandan 100 consultas idénticas con 10 en paralelo, primero por REST y después por gRPC. Al final se imprime un resumen como este (valores de una corrida de prueba; en vivo van a cambiar):

```
REST
  Exitosas:    100
  Latencia promedio: 15.668 ms
  Latencia p95:      50.711 ms
  Bytes respuesta promedio: 153.0

gRPC
  Exitosas:    100
  Latencia promedio: 7.456 ms
  Latencia p95:      19.455 ms
  Bytes respuesta promedio: 37.0
```

**Qué mostrar:**
- El **tamaño del mensaje**: la misma respuesta ocupa unas 4 veces menos en Protobuf (binario, sin nombres de campos) que en JSON.
- La **latencia** promedio y la p95 de cada protocolo.
- Que el CSV crudo quedó en `resultados/crudos/resultados_carga.csv` (una fila por consulta). Con esto trabaja la Actividad 9.
- Si da el tiempo, correrlo una segunda vez para mostrar que los números varían un poco, pero la tendencia se mantiene.

---

## Parte 3: Contract Testing con Pact (~4 min)

> Esta parte depende de las Actividades 7 y 8 (ver "Acuerdos" más abajo).

**3.1 El consumidor define el contrato:**
```bash
docker compose --profile pact run --rm pact-consumidor
```
Los tests pasan y aparece el JSON del contrato en `pacts/`. **Abrirlo y mostrarlo**: es lo que M5 espera recibir de M4.

**3.2 El proveedor correcto cumple el contrato:**
```bash
docker compose --profile pact run --rm pact-verificador
```
La verificación **pasa** (en verde).

**3.3 El proveedor cambia la respuesta y Pact lo detecta:**
```bash
docker compose --profile pact up -d proveedor-incompatible
docker compose --profile pact run --rm -e PROVEEDOR_URL=http://proveedor-incompatible:8000 pact-verificador
```
La verificación **falla**, y Pact indica exactamente qué campo no coincide con lo que espera el consumidor.

**Qué decir:** "Si M4 hubiera desplegado este cambio, M5 se rompía en producción. Pact lo detectó antes de integrar, sin levantar M5 de verdad."

---

## Cierre

```bash
docker compose --profile pact down
```

---

## Acuerdos con las Actividades 7 y 8 (para que la Parte 3 funcione)

El `docker-compose.yml` ya tiene los servicios de Pact. Para que funcionen, esas actividades tienen que respetar lo siguiente:

**Actividad 7 (consumidor):**
- El test va en `consumidor/tests/test_pact_consumidor.py` (se monta en el contenedor, no hace falta tocar el Dockerfile).
- Agregar `pact-python` y `pytest` a `consumidor/requirements.txt`.
- Escribir el JSON del contrato en la carpeta indicada por la variable de entorno `PACT_DIR` (en Docker vale `/pacts`, que es la carpeta `pacts/` del repo). Por ejemplo: `os.getenv("PACT_DIR", "pacts")`.

**Actividad 8 (proveedor):**
- El test va en `proveedor/tests/test_pact_verificacion.py`.
- Agregar `pact-python` y `pytest` a `proveedor/requirements.txt`.
- Leer el contrato desde `PACT_DIR` y verificar contra la URL de la variable `PROVEEDOR_URL` (por ejemplo `os.getenv("PROVEEDOR_URL", "http://localhost:8000")`).
- La modificación intencional se activa con la variable de entorno `PROVEEDOR_INCOMPATIBLE=true`. Así el proveedor normal sigue intacto y la demo puede mostrar los dos casos sin editar código en vivo. Por ejemplo, en `logica.py`:
  ```python
  import os
  INCOMPATIBLE = os.getenv("PROVEEDOR_INCOMPATIBLE", "false").lower() == "true"
  CAMPO_ID = "id_conductor" if INCOMPATIBLE else "conductor_id"   # nombre de campo cambiado

  # ...y en el append de consultar_disponibilidad:
  #     CAMPO_ID: conductor["conductor_id"],
  ```

---

## Si algo falla durante la demo

| Problema | Solución |
|---|---|
| `port is already allocated` | Hay algo usando el 8000 o el 50051. Correr `docker compose down` o cerrar el uvicorn local. |
| El consumidor da errores de conexión | Revisar con `docker compose ps` que `proveedor` esté `healthy`, y los logs con `docker compose logs proveedor`. |
| `pact-verificador` no encuentra el contrato | Primero hay que correr `pact-consumidor` (paso 3.1) para que exista el JSON en `pacts/`. |
| Se cambió código y no se ve el cambio | Reconstruir con `docker compose build` (o `up --build`). |
