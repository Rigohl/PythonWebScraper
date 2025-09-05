````markdown
# Web Scraper PRO

Un crawler y archivador web inteligente, diseñado para ser adaptable, resiliente y fácil de usar.

## Prerrequisitos

- Python 3.10 o superior.

## ¿Cómo Empezar?

1. **Instalar Dependencias:**
    Ejecuta el script de instalación correspondiente a tu sistema operativo. Esto creará un entorno virtual, instalará las librerías de Python y los navegadores necesarios para Playwright.

    **En Windows:**

    ```powershell
    .\1-Install-Dependencies.bat
    ```

    **En Linux o macOS:**

    ```bash
    chmod +x 1-Install-Dependencies.sh
    ./1-Install-Dependencies.sh
    ```

2. **Lanzar la Aplicación:**
    Una vez instaladas las dependencias, puedes ejecutar el scraper.

    **En Windows (usando el script de lanzamiento):**

    ```powershell
    .\2-Launch-Scraper.bat
    ```

    **En Linux o macOS (manualmente):**

    ```bash
    # 1. Activa el entorno virtual
    source .venv/bin/activate
    # 2. Lanza la TUI
    python3 -m src.main --tui
    ```

3. **(Opcional) Ejecución por Línea de Comandos (CLI):**
    Para automatización, también puedes ejecutarlo directamente (asegúrate de tener el entorno virtual activado).

    ```bash
    # Ejemplo: Iniciar un crawling desde la CLI (desde la raíz del proyecto)
    python3 -m src.main --crawl http://toscrape.com/
    ```

    Para ver todas las opciones, usa `python3 -m src.main --help`.

---

## Configuración

El proyecto utiliza `pydantic-settings` para gestionar la configuración, lo que permite una gran flexibilidad. La configuración se carga desde las siguientes fuentes, en orden de prioridad:

1. **Variables de entorno del sistema.**
2. **Un archivo `.env`** en la raíz del proyecto.
3. **Valores por defecto** definidos en `src/settings.py`.

Para personalizar tu configuración, simplemente copia el archivo `.env.example` a `.env` y modifica los valores.

```bash
# Ejemplo de contenido para tu archivo .env
CONCURRENCY=10
LLM_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
DB_PATH="data/mi_base_de_datos.db"
```

---

## Cómo Funciona (Flujo Detallado)

El proceso de scraping es gestionado por un orquestador concurrente:

1. **Inicio:** El proceso comienza con una o más URLs iniciales.
2. **Cola de Trabajo:** Estas URLs se añaden a una cola de prioridad (`asyncio.PriorityQueue`), dando preferencia a las URLs que probablemente sean más importantes (ej. con menor profundidad de ruta y según el tipo de contenido de la página padre).
3. **Pre-calificación y `robots.txt`:** Antes de encolar una URL, el sistema realiza una petición `HEAD` ultrarrápida para verificar que el tipo y tamaño del contenido son adecuados, descartando archivos grandes o no deseados sin necesidad de abrir un navegador. A continuación, respeta las directivas de `robots.txt` por defecto para un comportamiento ético (opción configurable).
4. **Trabajadores (Workers):** Se lanza un número configurable de "trabajadores" asíncronos. Cada trabajador es una tarea que se ejecuta en un bucle infinito, esperando URLs en la cola.

---

## Estructura del Proyecto (Detallado)

- `src/`: **Carpeta Principal del Código Fuente.** Organizada por funcionalidad.

... (contenido reducido)
