\# Análisis Crítico y Conclusiones de Rendimiento



\## 1. Tamaño del Mensaje Transmitido (Payload)



Para evaluar la eficiencia en la transmisión, se midió el tamaño del mensaje de respuesta para la consulta de disponibilidad transportando exactamente el mismo conjunto de datos.



| Protocolo | Formato de Serialización | Tamaño del Payload | Reducción de Tamaño | 

| ----- | ----- | ----- | ----- | 

| \*\*REST\*\* | JSON (Texto plano) | 153 Bytes | Base de referencia | 

| \*\*gRPC\*\* | Protocol Buffers (Binario) | 37 Bytes | 75.8% menor | 



\*\*Justificación Técnica:\*\* La diferencia obtenida de 116 bytes a favor de gRPC radica en el mecanismo de serialización. JSON transmite objetos en texto plano, repitiendo las claves (keys) por cada registro. Por el contrario, Protobuf serializa la información en formato binario y omite las claves, reemplazándolas por identificadores numéricos predefinidos en el archivo `.proto`. En escenarios de alta concurrencia dentro de la plataforma de movilidad, esta reducción de payload disminuye drásticamente el consumo de ancho de banda y la saturación de la red interna.



\## 2. Latencia bajo Carga (Rendimiento)



Se sometió a los servicios a una simulación de carga concurrente enviando el mismo conjunto de datos a ambos endpoints (REST y gRPC) para recolectar las métricas de latencia reales.



| Métrica de Latencia | REST (JSON) | gRPC (Protobuf) | Diferencia | 

| ----- | ----- | ----- | ----- | 

| \*\*Promedio\*\* | 78.39 ms | 33.07 ms | 2.37x más rápido | 

| \*\*Percentil 99 (p99)\*\* | 206.97 ms | 76.96 ms | 2.69x más rápido | 



\*\*Justificación Técnica:\*\* Los resultados reflejan una clara ventaja de rendimiento de gRPC. Por los siguientes motivos:



\* \*\*Eficiencia de CPU:\*\* La deserialización binaria de Protobuf consume significativamente menos ciclos de procesador que el parseo de cadenas de texto JSON.



\* \*\*Multiplexación nativa (HTTP/2):\*\* Mientras las implementaciones tradicionales de REST suelen sufrir de bloqueos (\*Head-of-Line Blocking\*) al requerir múltiples conexiones TCP, gRPC opera sobre HTTP/2, permitiendo enviar múltiples flujos concurrentes sobre una única conexión de larga duración.



\* \*\*Compresión de Cabeceras:\*\* El protocolo HTTP/2 utiliza HPACK para comprimir los metadatos de las peticiones, sumando velocidad a la transmisión.



\## 3. Análisis Crítico y Criterios de Utilización



\* \*\*Aplicación de REST:\*\* Resulta la opción más adecuada para exponer los servicios de la plataforma hacia el exterior (por ejemplo, el API Gateway público o aplicaciones móviles de los usuarios). Su legibilidad, adopción universal y facilidad de integración superan la necesidad de latencia ultra-baja en la frontera del sistema.



\* \*\*Aplicación de gRPC:\*\* Se recomienda su uso exclusivo para la comunicación síncrona interna (\*backend-to-backend\*). En módulos de alta exigencia, como la comunicación entre el motor de asignación de viajes y el servicio de disponibilidad de conductores.

