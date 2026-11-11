# Investigación conceptual de REST/JSON y gRPC/Protobuf

**Integrantes:** \[completar nombres\]

**Fecha:** 11 de noviembre de 2026

## 1. Resumen

Este documento presenta los fundamentos técnicos de REST con JSON y de gRPC con Protocol Buffers (Protobuf), dos enfoques ampliamente utilizados para comunicar servicios en arquitecturas distribuidas. Se describe qué problemas resuelve cada uno, cuáles son sus características principales y cómo se comparan en tres dimensiones: definición de contratos, interoperabilidad y rendimiento. La conclusión es que ninguno es superior en términos absolutos: la elección depende del contexto de uso, del tipo de consumidores y de los requisitos de latencia y volumen de datos.

## 2. Introducción y problema que se aborda

En una arquitectura compuesta por módulos independientes, cada módulo debe exponer sus capacidades a otros mediante una interfaz de red bien definida. Esta interfaz plantea problemas recurrentes:

- **Acuerdo sobre el contrato:** qué operaciones existen, qué datos reciben y devuelven, y cómo se informan los errores.
- **Independencia tecnológica:** los equipos pueden usar lenguajes y frameworks distintos y aun así deben comunicarse.
- **Evolución:** el contrato cambia con el tiempo sin romper a los consumidores existentes.
- **Eficiencia:** el costo de serializar, transmitir y procesar los mensajes puede ser relevante cuando el volumen o la frecuencia son altos.

REST y gRPC son dos respuestas distintas a estos problemas. REST propone un estilo arquitectónico orientado a recursos, apoyado en la semántica nativa de HTTP. gRPC propone un modelo de llamada a procedimiento remoto (RPC) con contratos fuertemente tipados y un formato binario compacto.

## 3. REST y JSON

### 3.1. Origen y definición

REST (*Representational State Transfer*) fue definido por Roy Fielding en su tesis doctoral (2000) como un estilo arquitectónico, no como un protocolo ni un estándar. Describe un conjunto de restricciones que, aplicadas en conjunto, favorecen la escalabilidad, la simplicidad y la evolución independiente de cliente y servidor. Una API que respeta estas restricciones se denomina RESTful.

### 3.2. Restricciones del estilo REST

| Restricción | Descripción |
| --- | --- |
| Cliente-servidor | Separación de responsabilidades entre interfaz de usuario y almacenamiento/lógica de datos. |
| Sin estado (*stateless*) | Cada petición contiene toda la información necesaria; el servidor no guarda el contexto de sesión entre peticiones. |
| Cacheable | Las respuestas deben indicar si pueden almacenarse en caché, reduciendo latencia y carga. |
| Interfaz uniforme | Recursos identificados por URI, manipulados mediante representaciones y un conjunto reducido de operaciones estándar. |
| Sistema en capas | Pueden existir intermediarios (balanceadores, proxies, gateways) transparentes para el cliente. |
| Código bajo demanda (opcional) | El servidor puede enviar código ejecutable al cliente. |

### 3.3. Modelo de recursos y semántica HTTP

En REST, la unidad central es el **recurso** (por ejemplo, un conductor o una ubicación), identificado por una URI. Las operaciones se expresan con los métodos HTTP, cuya semántica está definida en RFC 9110:

- **GET:** lectura, segura e idempotente.
- **POST:** creación o acciones que no son idempotentes por definición.
- **PUT:** reemplazo completo, idempotente.
- **PATCH:** modificación parcial.
- **DELETE:** eliminación, idempotente.

El resultado de cada operación se comunica con códigos de estado estándar (200, 201, 400, 404, 409, 500, entre otros), lo que permite que clientes e intermediarios interpreten la respuesta sin conocer la lógica de negocio.

Un marco usado habitualmente para evaluar qué tan "REST" es una API es el **modelo de madurez de Richardson**: nivel 0 (un único endpoint), nivel 1 (recursos), nivel 2 (uso correcto de verbos y códigos HTTP) y nivel 3 (hipermedia, HATEOAS). En la práctica, la mayoría de las APIs de la industria se ubican en el nivel 2.

### 3.4. JSON como formato de representación

JSON (*JavaScript Object Notation*, RFC 8259) es un formato de texto liviano, legible por humanos y soportado nativamente por prácticamente todos los lenguajes. Sus tipos primitivos son cadena, número, booleano, nulo, objeto y arreglo. Sus ventajas son la legibilidad y la facilidad de depuración. Sus desventajas son la verbosidad (los nombres de los campos se repiten en cada mensaje), la ausencia de un tipo para fechas o datos binarios (deben codificarse como cadenas, por ejemplo ISO 8601 o Base64) y que por sí mismo no impone un esquema.

### 3.5. Definición de contratos en REST: OpenAPI

Como REST no prescribe un lenguaje de descripción, la industria adoptó la **OpenAPI Specification (OAS)**, un documento en YAML o JSON, independiente del lenguaje de programación, que describe rutas, métodos, parámetros, esquemas de petición y respuesta (basados en JSON Schema), códigos de estado y mecanismos de autenticación. A partir de este documento pueden generarse documentación, servidores *mock*, código cliente y pruebas de contrato. Esto es especialmente relevante en proyectos con varios equipos, porque el documento OpenAPI actúa como acuerdo formal entre las partes.

### 3.6. Manejo de errores estandarizado

Para homogeneizar la forma de informar errores, existe el formato *Problem Details for HTTP APIs*, definido originalmente en RFC 7807 y actualizado por RFC 9457. Define campos como `type`, `title`, `status`, `detail` e `instance`, y el tipo de contenido `application/problem+json`.

### 3.7. Ventajas y limitaciones

**Ventajas:** simplicidad y curva de aprendizaje baja; compatibilidad total con navegadores, herramientas de depuración y proxies HTTP; gran ecosistema; facilidad de cacheo; legibilidad de los mensajes.

**Limitaciones:** mayor tamaño de mensaje y costo de análisis sintáctico por ser texto; contrato no obligatorio por el propio estilo (depende de la disciplina de documentación); *over-fetching* y *under-fetching* (se reciben más o menos datos de los necesarios); el modelo petición-respuesta no cubre de forma natural la comunicación bidireccional o en flujo continuo.

## 4. gRPC y Protocol Buffers

### 4.1. Origen y definición

gRPC es un framework RPC de código abierto, impulsado por Google y publicado en 2015, y actualmente alojado en la Cloud Native Computing Foundation (CNCF). Permite que una aplicación cliente invoque métodos de un servidor remoto como si fueran llamadas locales. Utiliza HTTP/2 como protocolo de transporte (RFC 9113) y Protocol Buffers como lenguaje de definición de interfaces y formato de serialización.

### 4.2. Protocol Buffers

Protobuf es un mecanismo de serialización binario, neutral respecto del lenguaje y de la plataforma. Los mensajes y servicios se declaran en archivos `.proto`. Un ejemplo ilustrativo:

```proto
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);
  rpc UploadEvents (stream Event) returns (UploadSummary);
}

message GetUserRequest {
  string user_id = 1;
}

message User {
  string user_id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4; // epoch en segundos
}
```

Cada campo se identifica con un **número de campo** y no con su nombre en la transmisión, lo que reduce el tamaño del mensaje. Un compilador (`protoc`) genera código tipado para el lenguaje elegido (clientes y esqueletos de servidor).

### 4.3. Características principales de gRPC

- **Contrato obligatorio y fuertemente tipado:** el archivo `.proto` es la fuente de verdad y el código se genera a partir de él.
- **Cuatro modos de comunicación:** unario (una petición, una respuesta), *server streaming*, *client streaming* y *streaming bidireccional*.
- **Multiplexación sobre HTTP/2:** varias llamadas concurrentes comparten una conexión, con compresión de cabeceras.
- **Funcionalidades integradas:** plazos (*deadlines*), cancelación, metadatos, interceptores, autenticación mediante TLS y tokens.
- **Códigos de estado propios:** gRPC define su propio conjunto de códigos (por ejemplo `OK`, `INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `UNAVAILABLE`), que no son códigos HTTP.
- **Evolución compatible:** se pueden agregar campos nuevos sin romper a clientes antiguos, siempre que no se reutilicen ni cambien los números de campo existentes.

### 4.4. Ventajas y limitaciones

**Ventajas:** mensajes compactos y rápidos de serializar; contratos estrictos con generación de código; soporte nativo de *streaming*; buen desempeño en comunicación interna entre servicios.

**Limitaciones:** los mensajes no son legibles directamente, lo que complica la depuración sin herramientas específicas; los navegadores no pueden usar gRPC de forma nativa y requieren gRPC-Web o una pasarela; menor soporte en proxies y herramientas HTTP tradicionales; mayor curva de aprendizaje y dependencia de la cadena de compilación de `.proto`.

## 5. Comparación

### 5.1. Definición de contratos

En REST el contrato se describe habitualmente con OpenAPI, pero este es un documento complementario: el servidor puede desviarse de él si no se verifica con pruebas de contrato. En gRPC, el archivo `.proto` es parte del propio mecanismo de comunicación y el código generado garantiza la coherencia entre cliente y servidor en tiempo de compilación. A cambio, REST permite contratos más flexibles y descriptivos en cuanto a validaciones (rangos, formatos, enumeraciones) mediante JSON Schema, mientras que Protobuf ofrece tipado estricto pero con menor expresividad de validación.

### 5.2. Interoperabilidad

REST sobre HTTP/1.1 y JSON es el denominador común: cualquier cliente que sepa hacer una petición HTTP puede consumirlo, incluidos navegadores, herramientas como `curl` o Postman y servicios de terceros. gRPC requiere bibliotecas cliente específicas y soporte HTTP/2 de extremo a extremo, aunque cuenta con implementaciones oficiales en los lenguajes más comunes (Java, Go, Python, C++, C#, Node.js, entre otros). Para exponer gRPC a clientes web suele necesitarse una capa adicional.

### 5.3. Rendimiento

Los mensajes Protobuf suelen ser notablemente más pequeños y más rápidos de procesar que sus equivalentes JSON, y HTTP/2 reduce el costo de establecer conexiones y permite multiplexar. Por ello gRPC tiende a ofrecer menor latencia y mayor *throughput* en comunicación interna con volumen alto de mensajes pequeños. La magnitud exacta de la diferencia depende del tamaño y la estructura de los mensajes, la red, la implementación y la configuración, por lo que debe medirse en cada caso antes de tomarla como argumento de decisión. En APIs con poco tráfico o mensajes grandes, la diferencia puede ser irrelevante frente a otros factores como el acceso a base de datos o a servicios externos.

### 5.4. Cuadro comparativo

| Aspecto | REST / JSON | gRPC / Protobuf |
| --- | --- | --- |
| Naturaleza | Estilo arquitectónico orientado a recursos | Framework RPC orientado a operaciones |
| Transporte | HTTP/1.1 o HTTP/2 | HTTP/2 |
| Formato | Texto (JSON) | Binario (Protobuf) |
| Contrato | OpenAPI (YAML/JSON), opcional por el estilo | Archivo `.proto`, obligatorio |
| Generación de código | Opcional, a partir de OpenAPI | Nativa y central |
| Legibilidad | Alta | Baja sin herramientas |
| Tamaño de mensaje | Mayor | Menor |
| Streaming | Limitado (SSE, WebSocket como complemento) | Nativo, cuatro modos |
| Errores | Códigos HTTP y Problem Details (RFC 9457) | Códigos gRPC y metadatos |
| Soporte en navegadores | Nativo | Requiere gRPC-Web o pasarela |
| Caché HTTP | Soportado de forma natural | Limitado |
| Uso típico | APIs públicas, integración entre equipos y terceros | Comunicación interna de alto rendimiento entre microservicios |

## 6. Criterios para elegir entre REST y gRPC

La elección depende del contexto de uso y no de una superioridad absoluta de una tecnología. Los criterios siguientes resumen las situaciones en que cada enfoque suele ser más adecuado.

**Se favorece REST/JSON cuando:**

- La API es pública o la consumen equipos y terceros con tecnologías diversas.
- Hay clientes web que acceden directamente desde el navegador.
- Se valoran la facilidad de depuración, el cacheo HTTP y una curva de aprendizaje baja.
- El volumen y la frecuencia de mensajes son moderados.

**Se favorece gRPC/Protobuf cuando:**

- La comunicación es interna entre microservicios bajo el control de una misma organización.
- Hay un alto tráfico de mensajes pequeños y la latencia es crítica.
- Se necesita *streaming* unidireccional o bidireccional.
- Se desea un contrato estricto con generación automática de código en varios lenguajes.

**Enfoque híbrido.** Es habitual usar gRPC en la comunicación interna y exponer REST hacia el exterior mediante una pasarela de API que traduzca entre ambos protocolos, con herramientas como gRPC-Gateway o Envoy.

**Medir antes de decidir.** Si el rendimiento es el argumento principal, conviene realizar pruebas de carga con mensajes y condiciones representativas del caso real, porque la diferencia depende de muchos factores.

## 7. Conclusiones

1. REST y gRPC resuelven el mismo problema general, la comunicación entre servicios, con filosofías distintas: recursos y semántica HTTP en un caso, procedimientos remotos y contratos tipados en el otro.
2. REST/JSON destaca por su simplicidad, universalidad e interoperabilidad; gRPC/Protobuf destaca por su eficiencia, contrato estricto y capacidad de *streaming*.
3. En términos de contrato, OpenAPI y `.proto` cumplen el mismo rol de fuente de verdad, pero con distinto grado de obligatoriedad y de integración con el código.
4. Las diferencias de rendimiento existen pero deben verificarse con mediciones propias antes de justificar una decisión.
5. Como regla general, REST con OpenAPI es adecuado para interfaces públicas o compartidas entre equipos diversos, gRPC para comunicación interna de alto rendimiento, y es frecuente combinarlos en un enfoque híbrido.

## 8. Referencias

- Fielding, R. T. (2000). *Architectural Styles and the Design of Network-based Software Architectures* (tesis doctoral). University of California, Irvine. Capítulo 5: Representational State Transfer (REST).
- Fowler, M. (2010). *Richardson Maturity Model*. https://martinfowler.com/articles/richardsonMaturityModel.html
- IETF. RFC 9110: *HTTP Semantics* (2022).
- IETF. RFC 9113: *HTTP/2* (2022).
- IETF. RFC 8259: *The JavaScript Object Notation (JSON) Data Interchange Format* (2017).
- IETF. RFC 7807: *Problem Details for HTTP APIs* (2016) y RFC 9457: *Problem Details for HTTP APIs* (2023).
- OpenAPI Initiative. *OpenAPI Specification*. https://spec.openapis.org/oas/latest.html
- gRPC Authors. *gRPC Documentation: Introduction, Core Concepts*. https://grpc.io/docs/
- Google. *Protocol Buffers Documentation*. https://protobuf.dev/
