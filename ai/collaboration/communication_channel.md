# Canal de Comunicación entre Agentes

## Estructura del Canal

El canal de comunicación entre los tres agentes (Arquitecto, Especialista en Reparación y Experto en UI/UX) está diseñado para facilitar una colaboración eficiente y transparente. Se implementa a través de un sistema de mensajería estructurado que permite varios tipos de interacciones.

## Formato de Mensajes

Cada mensaje en el canal sigue este formato estandarizado:

```
[AGENT-ID] [TIMESTAMP] [MESSAGE-TYPE] [PRIORITY] [CONTENT]
```

### Componentes:

1. **AGENT-ID**:
   - `[A]`: Arquitecto
   - `[R]`: Especialista en Reparación
   - `[U]`: Experto en UI/UX
   - `[SYS]`: Mensaje del sistema

2. **TIMESTAMP**:
   - Formato ISO 8601: `YYYY-MM-DDThh:mm:ss`

3. **MESSAGE-TYPE**:
   - `[QUERY]`: Solicitud de información o ayuda
   - `[RESPONSE]`: Respuesta a una solicitud
   - `[UPDATE]`: Actualización de progreso
   - `[ALERT]`: Notificación urgente
   - `[INFO]`: Información general
   - `[ACTION]`: Acción tomada o a tomar

4. **PRIORITY**:
   - `[HIGH]`: Requiere atención inmediata
   - `[MEDIUM]`: Atención normal
   - `[LOW]`: Información no urgente

5. **CONTENT**:
   - El contenido del mensaje puede incluir:
     - Texto descriptivo
     - Referencias a archivos (con ruta completa)
     - Fragmentos de código (con lenguaje especificado)
     - Enlaces a recursos
     - Resultados de análisis

## Protocolos de Comunicación

### 1. Solicitud de Ayuda

```
[A] [2025-09-06T11:15:30] [QUERY] [MEDIUM]
Necesito ayuda para entender la estructura de la base de datos en `src/database/manager.py`.
¿Puedes explicar cómo se manejan las transacciones concurrentes?

```

### 2. Respuesta a Solicitud

```
[R] [2025-09-06T11:18:45] [RESPONSE] [MEDIUM]
En referencia a tu consulta sobre `src/database/manager.py`:

Las transacciones concurrentes se manejan utilizando el patrón de bloqueo con contexto:

```python
with db_lock:
    conn = sqlite3.connect(DB_PATH)
    # Operaciones de base de datos
    conn.close()
```

El objeto `db_lock` es un `threading.Lock` que garantiza acceso exclusivo.
```

### 3. Actualización de Progreso

```
[U] [2025-09-06T14:30:12] [UPDATE] [LOW]
He completado el 70% de las mejoras en la interfaz TUI.
Elementos terminados:
- Menú principal con navegación por teclado
- Visualización de resultados con paginación
- Exportación de datos con barra de progreso

Pendientes:
- Mejora de los mensajes de error
- Personalización de colores
```

### 4. Alerta

```
[R] [2025-09-06T16:45:23] [ALERT] [HIGH]
Detectado un problema crítico en `src/scraper/engine.py` línea 156:
Hay una condición de carrera cuando se procesan múltiples URLs simultáneamente.
Esto podría causar corrupción de datos. Requiere atención inmediata.
```

## Reglas de Etiqueta

1. **Acuse de recibo**: Todo mensaje dirigido específicamente a un agente debe ser reconocido, incluso con un simple "Recibido".

2. **Especificidad**: Los mensajes deben ser lo más específicos posible, incluyendo nombres de archivos, números de línea, o fragmentos de código relevantes.

3. **Formato de código**: El código debe estar siempre en bloques con el lenguaje especificado:

```python
def ejemplo():
    pass
```

4. **Claridad**: Evitar ambigüedades. Si una solicitud o respuesta puede interpretarse de múltiples formas, pedir clarificación.

5. **Conclusión**: Los hilos de conversación deben cerrarse con un mensaje final que indique que el tema se ha resuelto.

## Almacenamiento de Comunicaciones

Todas las comunicaciones entre agentes se registran automáticamente en:
`c:\Users\DELL\Desktop\PythonWebScraper\ai\collaboration\reports\communication_log.md`

Este registro sirve como documentación del proceso de colaboración y como referencia para futuras mejoras del sistema.
