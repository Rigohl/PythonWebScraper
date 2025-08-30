# Prompts para el Agente de IA (Gemini Code Assist)

Este documento contiene una colección de prompts listos para usar. Están diseñados para instruir a un asistente de IA para que realice tareas específicas sobre este proyecto, como análisis de código, corrección de errores, generación de pruebas y más.

---

## 1. Corrección de Errores

### Prompt 1.1: Corregir el error de sintaxis inicial

**Objetivo:** Solucionar el `SyntaxError` que impide ejecutar la aplicación.

```
Actúa como un experto ingeniero de software. He intentado ejecutar mi aplicación y he recibido un `SyntaxError: expected 'else' after 'if' expression` en varios archivos Python dentro del directorio `src/`.

Tu tarea es analizar todos los archivos con extensión `.py` en la carpeta `src/` y sus subdirectorios. Busca y reemplaza todas las instancias de comillas dobles escapadas incorrectamente (`''`) por comillas simples (`'`).

Proporciona los cambios en formato diff para cada archivo que necesite ser modificado.
```

---

## 2. Análisis y Refactorización de Código

### Prompt 2.1: Analizar el script de PowerShell que causa los errores

**Objetivo:** Encontrar la causa raíz del error de sintaxis y corregir el script que lo genera.

```
Actúa como un desarrollador senior con experiencia en PowerShell y Python. Revisa el script `Nueva carpeta/apply_refactor.ps1`. Este script fue usado para actualizar los archivos del proyecto, pero introdujo errores de sintaxis en el código Python al reemplazar las comillas simples (`'`) por comillas dobles (`''`).

1.  Explica por qué el script de PowerShell está causando este problema.
2.  Proporciona una versión corregida del script `apply_refactor.ps1` que inserte el código Python en los archivos sin corromper la sintaxis de las comillas.
```

---

## 3. Generación de Pruebas

### Prompt 3.1: Crear pruebas unitarias para el `FingerprintManager`

**Objetivo:** Aumentar la cobertura de pruebas para una función clave.

```
Actúa como un ingeniero de QA especializado en Python. Quiero mejorar la cobertura de pruebas de mi proyecto.

Tu tarea es escribir pruebas unitarias para el método `_platform_from_ua` en el archivo `src/fingerprint_manager.py`.

Asegúrate de que las pruebas cubran los siguientes casos basados en el User-Agent:
- Windows
- macOS
- Linux
- iPhone/iPad
- Android
- Un caso por defecto donde no se reconoce la plataforma.

Presenta el código de las nuevas pruebas y sugiere en qué archivo de test deberían ubicarse.
```

---

## 4. Documentación y Análisis de Alto Nivel

### Prompt 4.1: Proponer la siguiente gran mejora para el proyecto

**Objetivo:** Obtener una recomendación estratégica sobre cómo evolucionar el proyecto.

```
Actúa como un arquitecto de software. Analiza los archivos `MEJORAS.md` y `README.md` para entender el estado actual y la visión a futuro del proyecto.

1.  Identifica cuál de las tareas marcadas como "PLANIFICADO" en `MEJORAS.md` consideras que aportaría más valor al proyecto en este momento.
2.  Justifica tu elección.
3.  Elabora un plan de implementación detallado para esa funcionalidad. Describe qué archivos necesitarían ser modificados, qué nuevas clases o funciones se deberían crear y un borrador de la lógica principal.
```
