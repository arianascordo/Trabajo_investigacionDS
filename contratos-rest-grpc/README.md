# Desarrollo de Software: Trabajo de investigación
## Comunicación: REST frente a gRPC
### Escenario de ejemplo
Para llevar a cabo la investigación acerca de REST/gRPC, proponemos un escenario de ejemplo relacionado con el TPI: **Consulta de disponibilidad de conductores cercanos**.
Solicitudes y despacho (otro servicio, M5 en el TPI) solicita a nuestro servicio (ubicación y disponibilidad): ¿Qué conductores disponibles hay cerca de ese punto?
_Proveedor:_ nuestro módulo de Ubicación y disponibilidad (en el TPI M4)
_Consumidor:_ un programa chico que simule ser el servicio de Solicitudes y despacho. Debe llamar una vez por REST y otra por gRPC. 
_Disparador:_ un pasajero pidió un viaje y el módulo de solicitudes y despacho necesita candidatos
_Datos de entrada:_ latitud y longitud del punto de origen de la solicitud, radio_km, tipo de vehículo (auto, moto).
_Salida:_ lista de conductores (conductor_id, tipo_vehiculo, distancia_km, eta_minutos, timestamp_ubicacion)
## Integración: Contract Testing con Pact

## Cómo correr la demo (Actividad 10)

Requisito: Docker Desktop. Desde esta carpeta (contratos-rest-grpc/):

​```
docker compose up --build              # levanta el proveedor (REST :8000 y gRPC :50051) y corre la comparativa
docker compose run --rm consumidor     # repite la comparativa con el proveedor ya levantado
docker compose down                    # apaga todo
​```

- El resumen de latencia y tamaño de mensaje se imprime en la terminal; el CSV crudo queda en resultados/crudos/resultados_carga.csv.
- Con el proveedor levantado, el Swagger de la API REST está en http://localhost:8000/docs.
- La parte de Contract Testing usa --profile pact. Los pasos completos de la demo están en demo/guion.md.