# Plantillas de Reportes para Agentes

Este documento define las plantillas estándar para los diferentes tipos de reportes que los agentes deben producir durante su colaboración. Estas plantillas aseguran consistencia y exhaustividad en la documentación.

## 1. Reporte de Análisis Inicial

```markdown
# Reporte de Análisis Inicial - [AGENT-ID]

## Información General
- **Fecha**: YYYY-MM-DD
- **Agente**: [Nombre del Agente]
- **Área de Enfoque**: [Área específica analizada]

## Resumen Ejecutivo
[Breve resumen de los hallazgos principales, no más de 3 párrafos]

## Componentes Analizados
| Componente | Ruta | Estado | Prioridad |
|------------|------|--------|-----------|
| [Nombre] | [Ruta del archivo] | [OK/Problemas/Crítico] | [Alta/Media/Baja] |

## Hallazgos Detallados
### 1. [Título del Hallazgo]
- **Ubicación**: [Archivo(s) y líneas relevantes]
- **Descripción**: [Descripción detallada del problema o hallazgo]
- **Impacto**: [Cómo afecta al sistema]
- **Recomendación**: [Sugerencia para abordar el problema]

[Repetir para cada hallazgo]

## Métricas
- **Calidad del Código**: [Evaluación numérica/5]
- **Cobertura de Pruebas**: [Porcentaje]
- **Deuda Técnica**: [Evaluación]
- **Rendimiento**: [Evaluación]

## Conclusiones
[Conclusiones generales del análisis]

## Próximos Pasos Recomendados
1. [Paso recomendado 1]
2. [Paso recomendado 2]
3. [...]
```

## 2. Plan de Implementación

```markdown
# Plan de Implementación - [AGENT-ID]

## Información General
- **Fecha**: YYYY-MM-DD
- **Agente**: [Nombre del Agente]
- **Área de Enfoque**: [Área específica de implementación]

## Objetivos
- [Objetivo 1]
- [Objetivo 2]
- [...]

## Tareas Planificadas
| ID | Tarea | Dependencias | Estimación | Prioridad | Asignado a |
|----|-------|--------------|------------|-----------|------------|
| T1 | [Descripción] | [IDs de tareas] | [tiempo] | [Alta/Media/Baja] | [Agente] |

## Desglose de Tareas

### T1: [Título de la Tarea]
- **Descripción detallada**: [Explicación completa]
- **Archivos afectados**:
  - [Ruta 1]
  - [Ruta 2]
- **Cambios propuestos**:
  ```python
  # Ejemplo de código o pseudocódigo
  ```
- **Criterios de aceptación**:
  1. [Criterio 1]
  2. [Criterio 2]

[Repetir para cada tarea]

## Riesgos y Mitigaciones
| Riesgo | Impacto | Probabilidad | Estrategia de Mitigación |
|--------|---------|--------------|--------------------------|
| [Descripción] | [Alto/Medio/Bajo] | [Alta/Media/Baja] | [Estrategia] |

## Cronograma
- **Inicio estimado**: [Fecha]
- **Finalización estimada**: [Fecha]
- **Hitos**:
  - [Fecha 1]: [Hito 1]
  - [Fecha 2]: [Hito 2]

## Recursos Necesarios
- [Recurso 1]
- [Recurso 2]
- [...]
```

## 3. Reporte de Progreso

```markdown
# Reporte de Progreso - [AGENT-ID]

## Información General
- **Fecha**: YYYY-MM-DD
- **Agente**: [Nombre del Agente]
- **Período**: [Fecha inicio - Fecha fin]

## Resumen de Progreso
[Breve resumen del progreso general, 1-2 párrafos]

## Tareas Completadas
| ID | Tarea | Fecha de Finalización | Resultados |
|----|-------|------------------------|------------|
| T1 | [Descripción] | [Fecha] | [Breve descripción de resultados] |

## Tareas en Progreso
| ID | Tarea | Progreso | Bloqueantes | Fecha estimada |
|----|-------|----------|-------------|----------------|
| T2 | [Descripción] | [%] | [Bloqueantes si hay] | [Fecha] |

## Cambios Realizados
| Archivo | Cambios | Razón |
|---------|---------|-------|
| [Ruta] | [Descripción del cambio] | [Justificación] |

## Problemas Encontrados
- **Problema 1**: [Descripción]
  - **Impacto**: [Impacto]
  - **Solución propuesta**: [Solución]

[Repetir para cada problema]

## Colaboraciones
- **Con [Agente]**: [Descripción de la colaboración]
- **Resultados**: [Resultados de la colaboración]

## Próximos Pasos
1. [Próximo paso 1]
2. [Próximo paso 2]
3. [...]

## Notas Adicionales
[Cualquier información adicional relevante]
```

## 4. Reporte de Verificación

```markdown
# Reporte de Verificación - [AGENT-ID]

## Información General
- **Fecha**: YYYY-MM-DD
- **Agente**: [Nombre del Agente]
- **Componentes Verificados**: [Lista de componentes]

## Resumen de Verificación
[Resumen general de los resultados de la verificación]

## Pruebas Realizadas
| ID | Prueba | Resultado | Notas |
|----|--------|-----------|-------|
| P1 | [Descripción] | [Éxito/Fallo] | [Observaciones] |

## Resultados Detallados

### P1: [Título de la Prueba]
- **Objetivo**: [Lo que se pretende verificar]
- **Procedimiento**: [Pasos seguidos]
- **Resultado esperado**: [Lo que debería ocurrir]
- **Resultado actual**: [Lo que ocurrió]
- **Evidencia**:
  ```
  [Salida de consola, capturas, etc.]
  ```
- **Análisis**: [Análisis del resultado]

[Repetir para cada prueba]

## Cobertura de Verificación
- **Componentes verificados**: [número]/[total]
- **Funcionalidades verificadas**: [número]/[total]
- **Casos de prueba ejecutados**: [número]/[total]

## Problemas Identificados
| ID | Problema | Severidad | Ubicación | Solución Propuesta |
|----|----------|-----------|-----------|-------------------|
| I1 | [Descripción] | [Alta/Media/Baja] | [Archivo:línea] | [Propuesta] |

## Conclusiones de Verificación
[Conclusiones sobre la calidad y estabilidad basadas en la verificación]

## Recomendaciones
1. [Recomendación 1]
2. [Recomendación 2]
3. [...]
```

## 5. Reporte Final

```markdown
# Reporte Final - [AGENT-ID]

## Información General
- **Fecha**: YYYY-MM-DD
- **Agente**: [Nombre del Agente]
- **Período de trabajo**: [Fecha inicio - Fecha fin]

## Resumen Ejecutivo
[Resumen conciso de todo el trabajo realizado y resultados obtenidos]

## Objetivos Cumplidos
- [Objetivo 1]: [Estado] - [Descripción del cumplimiento]
- [Objetivo 2]: [Estado] - [Descripción del cumplimiento]
- [...]

## Resultados Clave
1. **[Resultado 1]**:
   - [Detalle]
   - [Impacto]
   - [Métricas relacionadas]

[Repetir para cada resultado clave]

## Métricas Finales
| Métrica | Valor Inicial | Valor Final | Cambio | Objetivo |
|---------|---------------|-------------|--------|----------|
| [Métrica] | [Valor] | [Valor] | [+/-] | [Objetivo] |

## Innovaciones y Mejoras
- **[Innovación 1]**: [Descripción y beneficios]
- **[Innovación 2]**: [Descripción y beneficios]

## Lecciones Aprendidas
- **[Lección 1]**: [Descripción y aplicación futura]
- **[Lección 2]**: [Descripción y aplicación futura]

## Trabajo Pendiente
| Tarea | Razón | Recomendación |
|-------|-------|---------------|
| [Tarea] | [Por qué quedó pendiente] | [Sugerencia para completarla] |

## Recomendaciones para el Futuro
1. [Recomendación 1]
2. [Recomendación 2]
3. [...]

## Conclusiones
[Conclusiones generales sobre el trabajo realizado y el estado final del proyecto]

## Agradecimientos
[Reconocimiento a colaboraciones específicas y ayudas recibidas]
```

## 6. Solicitud de Colaboración

```markdown
# Solicitud de Colaboración - [AGENT-ID]

## Información General
- **Fecha**: YYYY-MM-DD
- **Agente Solicitante**: [Nombre del Agente]
- **Agente(s) Solicitado(s)**: [Nombre(s)]
- **Prioridad**: [Alta/Media/Baja]

## Descripción de la Solicitud
[Descripción detallada de la ayuda necesaria]

## Contexto
[Información de contexto necesaria para entender la solicitud]

## Archivos Relevantes
- [Ruta 1]
- [Ruta 2]
- [...]

## Código Relevante
```python
# Código relacionado con la solicitud
```

## Tipo de Asistencia Requerida
- [ ] Revisión de código
- [ ] Solución de problema
- [ ] Optimización
- [ ] Diseño
- [ ] Otro: [Especificar]

## Intentos Previos
[Descripción de soluciones ya intentadas]

## Resultados Esperados
[Descripción clara de lo que se espera lograr con esta colaboración]

## Plazo Deseado
- **Fecha límite**: [Fecha]
- **Urgencia**: [Justificación de la urgencia si aplica]
```

## 7. Respuesta de Colaboración

```markdown
# Respuesta de Colaboración - [AGENT-ID]

## Información General
- **Fecha**: YYYY-MM-DD
- **Agente Respondiente**: [Nombre del Agente]
- **En respuesta a**: [ID de solicitud]
- **Estado**: [Completado/Parcial/No resuelto]

## Resumen de la Respuesta
[Breve resumen de la solución o ayuda proporcionada]

## Solución Propuesta
[Descripción detallada de la solución]

## Código Propuesto
```python
# Código de la solución
```

## Cambios Realizados
| Archivo | Líneas | Descripción del Cambio |
|---------|--------|------------------------|
| [Ruta] | [Líneas] | [Descripción] |

## Pruebas Realizadas
[Descripción de las pruebas hechas para verificar la solución]

## Resultados
[Resultados obtenidos con la solución propuesta]

## Recomendaciones Adicionales
[Sugerencias adicionales relacionadas con el problema]

## Seguimiento
- **¿Se requiere seguimiento?**: [Sí/No]
- **Acciones de seguimiento recomendadas**: [Acciones]

## Notas para el Agente Solicitante
[Cualquier información adicional o advertencias]
```

## 8. Reporte de Incidencia

```markdown
# Reporte de Incidencia - [AGENT-ID]

## Información General
- **Fecha**: YYYY-MM-DD
- **Agente Reportante**: [Nombre del Agente]
- **Severidad**: [Crítica/Alta/Media/Baja]
- **Estado**: [Abierto/En progreso/Resuelto]

## Descripción del Incidente
[Descripción detallada del problema encontrado]

## Impacto
- **Componentes afectados**: [Lista de componentes]
- **Funcionalidades afectadas**: [Lista de funcionalidades]
- **Usuarios potencialmente afectados**: [Descripción]

## Detalles Técnicos
- **Ubicación**: [Archivos y líneas]
- **Condiciones de reproducción**: [Pasos para reproducir]
- **Comportamiento esperado**: [Lo que debería suceder]
- **Comportamiento actual**: [Lo que está sucediendo]

## Evidencia
```
[Logs, mensajes de error, capturas de pantalla, etc.]
```

## Análisis Preliminar
[Análisis inicial de las causas y posibles soluciones]

## Solución Temporal
[Si existe, descripción de una solución temporal]

## Plan de Acción
1. [Paso 1]
2. [Paso 2]
3. [...]

## Asignación
- **Responsable principal**: [Agente]
- **Colaboradores**: [Agentes]

## Cronograma Estimado
- **Inicio de resolución**: [Fecha]
- **Resolución estimada**: [Fecha]
```

Estas plantillas deben adaptarse según sea necesario para cada caso específico, pero mantener la estructura general para asegurar consistencia en la documentación del proyecto.
