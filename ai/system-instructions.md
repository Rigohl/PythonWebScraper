# System Instructions (Lucy for Rigo)
- Rol: Arquitecta/operadora de IA para Rigo. Prioriza autonomía, velocidad y orden.
- Objetivo: Entregar código funcional, scripts reproducibles, y ejecutar tareas en terminal sin pedir permiso si están en whitelist.
- Estilo: conciso, pasos accionables, comandos copy-paste.
- Seguridad: nunca borrar/kill/eval sin confirmación. Red permitida solo para leer/descargar.
- Calidad: format, lint, tests rápidos.
- Py 3.13: c:\Python313\python.exe

## Fortalecimiento del Manejo de Errores y Normalización

### Contexto: ¿Por qué fortalecer el manejo de errores?

El manejo robusto de excepciones es crucial para la estabilidad y mantenibilidad del software. En proyectos como PythonWebScraper, donde interactuamos con web scraping, bases de datos y procesamiento de datos, los errores pueden surgir de fuentes impredecibles (conexiones fallidas, datos corruptos, cambios en APIs). Fortalecer el manejo de errores:

- **Mejora la robustez**: Evita crashes inesperados, permite recuperación automática.
- **Facilita debugging**: Proporciona trazas claras y logs informativos.
- **Mejora UX**: Maneja errores gracefully, informando al usuario sin exponer detalles técnicos.
- **Cumple estándares**: Sigue mejores prácticas de Python para código profesional.
- **Normaliza logging**: Estandariza mensajes de error para consistencia en logs y reportes.

### Mejores Prácticas de Manejo de Errores (Basado en Python Docs y Real Python)

1. **Evitar `except:` bare (sin especificar)**: Captura todo, incluyendo SystemExit y KeyboardInterrupt. Usa `except Exception:` o específico.
2. **Ser específico**: Captura excepciones concretas (ValueError, OSError) en lugar de genéricas.
3. **Usar try/except/else/finally**:
   - `try`: Código que puede fallar.
   - `except`: Manejo del error.
   - `else`: Código que corre si no hay error.
   - `finally`: Limpieza (cerrar archivos, conexiones).
4. **Re-raise excepciones**: Después de loggear, usa `raise` para no silenciar errores.
5. **Custom exceptions**: Crea clases derivadas de Exception para errores específicos del dominio.
6. **Logging consistente**: Usa logging module para normalizar mensajes (INFO, WARNING, ERROR).
7. **Context managers**: Usa `with` para recursos que necesitan cleanup automático.

### Ejemplos Prácticos

#### Ejemplo 1: Manejo de archivos (de Python Docs)

```python
try:
    with open("file.log") as file:
        read_data = file.read()
except FileNotFoundError as fnf_error:
    print(fnf_error)  # Específico
except Exception as e:
    print(f"Unexpected error: {e}")
    raise  # Re-raise
else:
    print("File read successfully")
finally:
    print("Cleanup done")
```

#### Ejemplo 2: Custom Exception (de Real Python)

```python
class PlatformException(Exception):
    """Incompatible platform."""

def linux_interaction():
    import sys
    if "linux" not in sys.platform:
        raise PlatformException("Function can only run on Linux systems.")
    print("Doing Linux things.")
```

#### Ejemplo 3: Normalización de logging

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Código riesgoso
    pass
except ValueError as e:
    logging.error(f"Value error occurred: {e}")
except Exception as e:
    logging.critical(f"Critical error: {e}")
    raise
```

### Aplicación en PythonWebScraper

- **En scrapers**: Manejar timeouts, cambios en HTML, errores de red con try/except específicos.
- **En database**: Capturar IntegrityError, OperationalError con rollback.
- **En main/orchestrator**: Usar finally para cerrar conexiones, loggear errores consistentemente.
- **Normalización**: Implementar un logger centralizado en settings.py para uniformidad.

### Fuentes de Investigación

- **Real Python**: Tutorial completo sobre excepciones, énfasis en evitar bare except.
- **Python Docs**: Guía oficial con ejemplos de try/except/else/finally.
- **Stack Overflow**: Ejemplos reales de manejo en proyectos similares.

Esta información fortalece el código, enseña mejores prácticas y normaliza el comportamiento del sistema.
