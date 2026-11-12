\# Criterios de utilización de REST, gRPC y Contract Testing



\## Resumen

Este trabajo establece criterios para decidir cuándo aplicar \*\*REST/JSON\*\*, \*\*gRPC/Protobuf\*\* y \*\*Contract Testing con Pact\*\*, aplicándolos a la plataforma de movilidad distribuida del TPI. Los criterios se organizan según la \*\*complejidad de implementación\*\* y el \*\*rendimiento esperado\*\*.



\---



\## Marco Conceptual



\* \*\*REST/JSON:\*\* Estilo arquitectónico basado en recursos identificados por URI y manipulados mediante métodos HTTP. Sus representaciones suelen ser JSON y su contrato se documenta con \*\*OpenAPI\*\* (rutas, parámetros, esquemas y códigos de respuesta).

\* \*\*gRPC/Protobuf:\*\* Framework de llamadas a procedimientos remotos (RPC) sobre HTTP/2 que utiliza \*\*Protocol Buffers\*\*, un formato binario compacto. El contrato se declara en archivos `.proto` a partir de los cuales se genera código tipado para cliente y servidor. Admite streaming de forma nativa.

\* \*\*Contract Testing con Pact:\*\* Prueba que verifica que consumidor y proveedor cumplen su acuerdo sin necesidad de desplegarlos juntos. El consumidor declara en un test lo que necesita, Pact genera el contrato y el proveedor lo verifica contra su servicio real, detectando cambios incompatibles antes de la integración.



\---



\## Criterios de Utilización

La elección entre REST y gRPC se decide por cada interacción, fundamentándose en la complejidad técnica que agrega cada tecnología y el rendimiento esperado.



\### 1. Complejidad



| Criterio | REST/JSON | gRPC/Protobuf |

| :--- | :--- | :--- |

| \*\*Aprendizaje y herramientas\*\* | \*\*Baja.\*\* Con HTTP y JSON, herramientas como `curl` o Postman alcanzan. | \*\*Alta.\*\* Requiere conocer `.proto`, `protoc` y manejar código generado. |

| \*\*Depuración\*\* | Mensajes legibles en texto plano. | Mensajes binarios que requieren herramientas específicas. |

| \*\*Coordinación del contrato\*\* | OpenAPI, el cual puede desviarse de la implementación si no se verifica. | Archivo `.proto` como fuente única de verdad, garantizando coherencia al compilar. |

| \*\*Clientes heterogéneos\*\* | Cualquier cliente HTTP (incluidos los navegadores web de forma nativa). | Requiere bibliotecas gRPC. Los navegadores necesitan `gRPC-Web` o una pasarela. |



> \*\*Conclusión de complejidad:\*\* REST es la opción de menor costo de adopción. gRPC se justifica únicamente cuando ese costo inicial se compensa con una ganancia técnica concreta.



\### 2. Rendimiento



| Criterio | REST/JSON | gRPC/Protobuf |

| :--- | :--- | :--- |

| \*\*Tamaño del mensaje\*\* | Texto. Repite los nombres de los campos en cada mensaje. | Binario compacto. Campos identificados por número. |

| \*\*Conexiones\*\* | HTTP/1.1 o HTTP/2. | HTTP/2 con multiplexación nativa. |

| \*\*Volumen y frecuencia\*\* | Adecuado para un volumen de tráfico moderado. | Pensado para alto tráfico de mensajes pequeños. |

| \*\*Streaming\*\* | Limitado. | Nativo con cuatro modos distintos. |



> \*\*Conclusión de rendimiento:\*\* La diferencia real depende del tamaño de los mensajes, la red y la implementación, por lo que debe medirse antes de usarse como argumento definitivo de decisión.



\---



\## Situaciones de Uso (¿Cuándo elegir cada uno?)



\### REST/JSON

\* \*\*Conviene cuando:\*\* La interfaz la consumen otros equipos con tecnologías distintas, el patrón es petición-respuesta con frecuencia moderada y se valora la facilidad para depurar con herramientas comunes.

\* \*\*No conviene cuando:\*\* Existen flujos continuos de mensajes pequeños con latencia crítica o se requiere streaming bidireccional/continuo.



\### gRPC/Protobuf

\* \*\*Conviene cuando:\*\* Se trata de comunicación interna de alto volumen, con latencia crítica, necesidad de streaming y cuando se busca un contrato estricto con generación automática de código.

\* \*\*No conviene cuando:\*\* Son interfaces públicas o consumidas directamente desde navegadores, el volumen de tráfico es bajo o el equipo no puede sostener la curva de aprendizaje y herramientas.



\### Contract Testing (Pact)

\* \*\*Conviene cuando:\*\* Consumidor y proveedor son equipos distintos con despliegues independientes y existe el riesgo de que el contrato diverja de la implementación real.

\* \*\*No conviene cuando:\*\* Se aplica dentro de un mismo módulo o en el acceso a bases de datos propias. 

\* \*\*Nota importante:\*\* No reemplaza a las pruebas funcionales; valida la \*\*forma y estructura\*\* de la respuesta, no la lógica de negocio.

