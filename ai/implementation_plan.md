# Plan de Implementación de Correcciones para WebScraperPRO

Este documento contiene el plan detallado de implementación para corregir y mejorar el proyecto WebScraperPRO, basado en el análisis colaborativo de los tres agentes de IA.

## 1. Correcciones de Errores de Sintaxis

### 1.1 Corrección en embedding_adapter.py:256

**Problema:** Error de sintaxis debido a dos puntos sin valor predeterminado.
**Solución:** Corregir la definición de la función.

```python
# Original (incorrecto)
def calculate_similarity_matrix(vectors, batch_size=100:
    # código...

# Corregido
def calculate_similarity_matrix(vectors, batch_size=100):
    # código...
```

### 1.2 Corrección en novelty_detector.py:391

**Problema:** Paréntesis sin cerrar en función.
**Solución:** Balancear los paréntesis correctamente.

```python
# Original (incorrecto)
novelty_score = self._calculate_novelty_score(embedding, reference_embeddings

# Corregido
novelty_score = self._calculate_novelty_score(embedding, reference_embeddings)
```

### 1.3 Corrección en proactivity_manager.py:466

**Problema:** Sintaxis inválida en estructura de control.
**Solución:** Corregir la estructura de control.

```python
# Original (incorrecto)
if self.current_mode == "aggressive:
    # código...

# Corregido
if self.current_mode == "aggressive":
    # código...
```

### 1.4 Corrección en vector_store.py:429

**Problema:** Indentación incorrecta o sintaxis de bloque inválida.
**Solución:** Corregir la indentación y estructura del bloque.

```python
# Original (incorrecto)
if similarity > threshold
    matches.append((doc_id, similarity))

# Corregido
if similarity > threshold:
    matches.append((doc_id, similarity))
```

## 2. Corrección de Referencias Indefinidas

### 2.1 Corrección en autonomous_controller.py

**Problema:** Referencias indefinidas a 'os'.
**Solución:** Añadir la importación necesaria.

```python
# Añadir al inicio del archivo, después de las importaciones existentes
import os
```

### 2.2 Corrección en professional_app_update.py

**Problema:** Referencias indefinidas a 'TextLog'.
**Solución:** Añadir la importación necesaria.

```python
# Añadir al inicio del archivo, después de las importaciones existentes
from textual.widgets import TextLog
```

## 3. Corrección de F-strings sin Placeholders

### 3.1 Correcciones en professional_app.py

**Problema:** Múltiples f-strings sin marcadores de posición.
**Soluciones:**

```python
# Línea 777 - Original:
f"Rendimiento: "
# Corregido:
f"Rendimiento: {self.performance_metric:.2f}%"

# Línea 780 - Original:
f"Estado: "
# Corregido:
f"Estado: {self.current_state}"

# Línea 802 - Original:
f"Conexión: "
# Corregido:
f"Conexión: {self.connection_status}"

# Línea 805 - Original:
f"Latencia: "
# Corregido:
f"Latencia: {self.latency_ms:.1f}ms"

# Línea 814 - Original:
f"CPU: "
# Corregido:
f"CPU: {self.cpu_usage:.1f}%"

# Línea 817 - Original:
f"Memoria: "
# Corregido:
f"Memoria: {self.memory_usage:.1f}MB"

# Línea 830 - Original:
f"Progreso: "
# Corregido:
f"Progreso: {self.progress_percent:.1f}%"

# Línea 832 - Original:
f"Tiempo restante: "
# Corregido:
f"Tiempo restante: {self.remaining_time_str}"

# Línea 847 - Original:
f"Elementos procesados: "
# Corregido:
f"Elementos procesados: {self.processed_items}"

# Línea 849 - Original:
f"Velocidad: "
# Corregido:
f"Velocidad: {self.processing_speed:.2f} elementos/s"
```

### 3.2 Correcciones en autonomous_coordinator.py

```python
# Línea 453 - Original:
f"Estado del coordinador: "
# Corregido:
f"Estado del coordinador: {self.state}"

# Línea 572 - Original:
f"Tarea actual: "
# Corregido:
f"Tarea actual: {self.current_task}"
```

### 3.3 Correcciones en otras ubicaciones

Aplicar el mismo patrón para corregir los f-strings en:
- database_brain_adapter.py:408
- self_improvement.py:332
- self_healing.py:581
- voice_assistant.py:658

## 4. Corrección de Variables No Utilizadas

Eliminar o utilizar adecuadamente las variables identificadas como no utilizadas, siguiendo un patrón similar a este:

```python
# Opción 1: Eliminar la asignación si no se necesita
# Original:
synthesis = self._synthesize_results(data)
# Corregido:
self._synthesize_results(data)  # Procesamiento sin capturar el resultado

# Opción 2: Comentar el propósito si se mantiene para uso futuro
# Original:
synthesis = self._synthesize_results(data)
# Corregido:
synthesis = self._synthesize_results(data)  # TODO: Usar en próxima fase de implementación

# Opción 3: Usar el prefijo de descarte para indicar intencionalmente no usado
# Original:
synthesis = self._synthesize_results(data)
# Corregido:
_synthesis = self._synthesize_results(data)  # Resultado capturado pero no usado
```

## 5. Mejoras de Interfaz de Usuario

Una vez corregidos los errores, implementar las siguientes mejoras en la interfaz:

### 5.1 Mejora de retroalimentación visual

```python
# Añadir indicadores visuales para métricas
def _format_metric(self, name, value, threshold_warning, threshold_critical):
    if value > threshold_critical:
        return f"[bold red]{name}: {value}[/bold red]"
    elif value > threshold_warning:
        return f"[bold yellow]{name}: {value}[/bold yellow]"
    else:
        return f"[bold green]{name}: {value}[/bold green]"

# Ejemplo de uso:
cpu_display = self._format_metric("CPU", self.cpu_usage, 70, 90)
```

### 5.2 Mejora de layout

Reorganizar los elementos de la interfaz para optimizar el espacio y mejorar la legibilidad, agrupando métricas relacionadas y estableciendo jerarquía visual clara.

## 6. Plan de Pruebas

1. Ejecutar flake8 para verificar que se han corregido todos los errores de sintaxis
2. Ejecutar las pruebas unitarias existentes para garantizar que no se ha roto funcionalidad
3. Probar específicamente las áreas modificadas para verificar su funcionamiento
4. Validar el archivo WebScraperPRO.bat ejecutando cada una de sus opciones

## 7. Documentación de Cambios

Actualizar los siguientes archivos para reflejar los cambios realizados:
- CHANGELOG-IA.md
- IA_SELF_REPAIR.md
- README.md

## Implementación Secuencial

Para minimizar el riesgo, implementar las correcciones en el siguiente orden:

1. Correcciones de errores de sintaxis críticos (Sección 1)
2. Corrección de referencias indefinidas (Sección 2)
3. Corrección de f-strings (Sección 3)
4. Eliminación de variables no utilizadas (Sección 4)
5. Mejoras de interfaz de usuario (Sección 5)
6. Pruebas exhaustivas (Sección 6)
7. Actualización de documentación (Sección 7)

Este plan será implementado por el equipo de agentes de IA siguiendo el protocolo de colaboración establecido en `multi_agent_collaboration.md`.
