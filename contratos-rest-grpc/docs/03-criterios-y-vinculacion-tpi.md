# Criterios de utilización de REST, gRPC y Contract Testing

## Resumen

Este trabajo establece criterios para decidir cuándo aplicar **REST/JSON**, **gRPC/Protobuf** y **Contract Testing con Pact**, aplicándolos a la plataforma de movilidad distribuida del TPI. Los criterios se organizan según la **complejidad de implementación** y el **rendimiento esperado**.

---

## Marco Conceptual

* **REST/JSON:** Estilo arquitectónico basado en recursos identificados por URI y manipulados mediante métodos HTTP. Sus representaciones suelen ser JSON y su contrato se documenta con **OpenAPI** (rutas, parámetros, esquemas y códigos de respuesta).
* **gRPC/Protobuf:** Framework de llamadas a procedimientos remotos (RPC) sobre HTTP/2 que utiliza **Protocol Buffers**, un formato binario compacto. El contrato se declara en archivos `.proto` a partir de los cuales se genera código tipado para cliente y servidor. Admite streaming de forma nativa.
* **Contract Testing con Pact:** Prueba que verifica que consumidor y proveedor cumplen su acuerdo sin necesidad de desplegarlos juntos. El consumidor declara en un test lo que necesita, Pact genera el contrato y el proveedor lo verifica contra su servicio real, detectando cambios incompatibles antes de la integración.

---

## Criterios de Utilización

La elección entre REST y gRPC se decide **por interacción**, fundamentándose en la complejidad técnica que agrega cada tecnología y el rendimiento esperado.

### 1. Complejidad

| Criterio | REST/JSON | gRPC/Protobuf |
| :--- | :--- | :--- |
| **Aprendizaje y herramientas** | **Baja.** Con HTTP y JSON, herramientas como `curl` o Postman alcanzan. | **Alta.** Requiere definir archivos `.proto`, usar `protoc` y gestionar código generado. |
| **Depuración** | Mensajes de texto legibles directamente por humanos. | Mensajes binarios que requieren herramientas específicas para inspeccionarse. |
| **Coordinación del contrato** | OpenAPI (puede desviarse de la implementación si no se verifica). | Archivo `.proto` como fuente de verdad única con coherencia garantizada al compilar. |
| **Clientes heterogéneos** | Cualquier cliente HTTP, incluidos los navegadores web de forma nativa. | Requiere bibliotecas gRPC. Los navegadores necesitan **gRPC-Web** o una pasarela (gateway). |

> **Nota:** REST es la opción de menor costo de adopción. El uso de gRPC se justifica únicamente cuando ese costo inicial se compensa con una ganancia concreta de rendimiento o tipado estricto.

### 2. Rendimiento

| Criterio | REST/JSON | gRPC/Protobuf |
| :--- | :--- | :--- |
| **Tamaño del mensaje** | Texto plano (JSON). Repite los nombres de cada campo en cada envío. | Binario compacto. Los campos se identifican por número de etiqueta. |
| **Conexiones** | HTTP/1.1 o HTTP/2. | HTTP/2 con multiplexación nativa de peticiones sobre una misma conexión. |
| **Volumen y frecuencia** | Adecuado para tráfico y volumen moderado. | Pensado para alto tráfico de mensajes pequeños y alta frecuencia. |
| **Streaming** | Limitado. | Nativo con cuatro modos (unario, streaming de servidor, de cliente y bidireccional). |

> **Importante:** La diferencia real de rendimiento depende del tamaño de los mensajes, la red y la implementación; por ello, **debe medirse** antes de usarse como argumento definitivo de decisión.

---

## Situaciones de Uso

### REST/JSON
* **Conviene cuando:** La interfaz es consumida por otros equipos con tecnologías distintas, el patrón es petición-respuesta con frecuencia moderada y se valora depurar con herramientas comunes.
* **No conviene cuando:** Existen flujos continuos de mensajes pequeños con latencia crítica o se requiere streaming bidireccional.

### gRPC/Protobuf
* **Conviene cuando:** Se trata de comunicación interna entre microservicios de alto volumen, con latencia crítica, necesidad de streaming o cuando se busca un contrato estricto con código autogenerado.
* **No conviene cuando:** Son interfaces públicas o consumidas directamente desde navegadores web, tienen bajo volumen de tráfico o el equipo no puede sostener la complejidad de su cadena de herramientas.

### Contract Testing (Pact)
* **Conviene cuando:** Consumidor y proveedor son equipos distintos con ciclos de despliegue independientes y existe el riesgo de que el contrato diverja de la implementación real.
* **No conviene cuando:** Se aplica dentro de un mismo módulo o en el acceso a bases de datos propias. Tampoco reemplaza a las pruebas funcionales, ya que valida la **forma/estructura** de la respuesta y no la lógica de negocio.
