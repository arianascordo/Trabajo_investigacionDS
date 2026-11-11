import csv
import math
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import perf_counter


# Permite importar los clientes desde app/ al ejecutar este archivo desde carga/.
RUTA_CONSUMIDOR = str(Path(__file__).resolve().parents[1])
if RUTA_CONSUMIDOR not in sys.path:
    sys.path.insert(0, RUTA_CONSUMIDOR)

from app.cliente_grpc import (
    consultar_disponibilidad as consultar_grpc,
)
from app.cliente_rest import (
    consultar_disponibilidad as consultar_rest,
)


# Datos idénticos para ambos protocolos.
DATOS_PRUEBA = {
    "lat_origen": -27.4511,
    "lon_origen": -58.9867,
    "radio_km": 5.0,
    "tipo_vehiculo": "AUTO",
}

TOTAL_SOLICITUDES = 100
CONCURRENCIA = 10

ARCHIVO_CSV = Path(__file__).resolve().with_name("resultados_carga.csv")


def medir_una_solicitud(protocolo: str, cliente) -> dict:
    """Ejecuta una consulta y registra su latencia, tamaño o error."""

    inicio = perf_counter()

    try:
        respuesta = cliente(**DATOS_PRUEBA)
        latencia_ms = (perf_counter() - inicio) * 1000

        return {
            "protocolo": protocolo,
            "latencia_ms": round(latencia_ms, 3),
            "bytes_respuesta": respuesta["bytes_respuesta"],
            "error": "",
        }
    except Exception as error:
        latencia_ms = (perf_counter() - inicio) * 1000

        return {
            "protocolo": protocolo,
            "latencia_ms": round(latencia_ms, 3),
            "bytes_respuesta": "",
            "error": f"{type(error).__name__}: {error}",
        }


def ejecutar_carga(protocolo: str, cliente) -> list[dict]:
    """Envía el mismo número de consultas usando un máximo de trabajadores."""

    resultados = []

    with ThreadPoolExecutor(max_workers=CONCURRENCIA) as executor:
        tareas = [
            executor.submit(medir_una_solicitud, protocolo, cliente)
            for _ in range(TOTAL_SOLICITUDES)
        ]

        for tarea in as_completed(tareas):
            resultados.append(tarea.result())

    return resultados


def percentil(valores: list[float], proporcion: float) -> float:
    """Calcula un percentil usando el método de rango más cercano."""

    ordenados = sorted(valores)
    posicion = max(0, math.ceil(proporcion * len(ordenados)) - 1)
    return ordenados[posicion]


def mostrar_resumen(protocolo: str, resultados: list[dict]) -> None:
    exitosas = [
        resultado
        for resultado in resultados
        if not resultado["error"]
    ]
    fallidas = len(resultados) - len(exitosas)

    print(f"\n{protocolo}")
    print(f"  Solicitudes: {len(resultados)}")
    print(f"  Exitosas:    {len(exitosas)}")
    print(f"  Fallidas:    {fallidas}")

    if not exitosas:
        print("  No hay solicitudes exitosas para calcular métricas.")
        return

    latencias = [r["latencia_ms"] for r in exitosas]
    tamanios = [r["bytes_respuesta"] for r in exitosas]

    print(f"  Latencia promedio: {sum(latencias) / len(latencias):.3f} ms")
    print(f"  Latencia p50:      {percentil(latencias, 0.50):.3f} ms")
    print(f"  Latencia p95:      {percentil(latencias, 0.95):.3f} ms")
    print(f"  Bytes respuesta promedio: {sum(tamanios) / len(tamanios):.1f}")


def guardar_csv(resultados: list[dict]) -> None:
    columnas = [
        "protocolo",
        "latencia_ms",
        "bytes_respuesta",
        "error",
    ]

    with ARCHIVO_CSV.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(resultados)

    print(f"\nResultados individuales guardados en: {ARCHIVO_CSV}")


def main() -> None:
    print("Ejecutando carga REST...")
    resultados_rest = ejecutar_carga("REST", consultar_rest)

    print("Ejecutando carga gRPC...")
    resultados_grpc = ejecutar_carga("gRPC", consultar_grpc)

    todos_los_resultados = resultados_rest + resultados_grpc

    mostrar_resumen("REST", resultados_rest)
    mostrar_resumen("gRPC", resultados_grpc)
    guardar_csv(todos_los_resultados)


if __name__ == "__main__":
    main()