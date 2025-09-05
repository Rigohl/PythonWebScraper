# Chat Commands y Procesamiento de Lenguaje Natural

El chat del WebScraperPRO incluye dos modos de interacción:

1. **Comandos explícitos con prefijo `/`**
2. **Procesamiento de lenguaje natural**

## Comandos Explícitos

Los comandos del chat utilizan el prefijo `/` y permiten acceso directo a funcionalidades específicas:

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/help`, `/ayuda` | Muestra ayuda sobre comandos disponibles | `/help` |
| `/crawl URL` | Inicia un scraping en la URL especificada | `/crawl https://books.toscrape.com` |
| `/kb CONSULTA` | Consulta la base de conocimiento | `/kb python scraping` |
| `/snapshot` | Genera un snapshot del cerebro | `/snapshot` |
| `/status` | Muestra el estado actual del scraping | `/status` |
| `/stop` | Detiene cualquier proceso de scraping en ejecución | `/stop` |
| `/edit ARCHIVO [CONTENIDO]` | Edita o muestra un archivo | `/edit config.json` |
| `/terminal COMANDO` | Ejecuta un comando en terminal | `/terminal dir` |

## Procesamiento de Lenguaje Natural

El chat ahora puede entender y responder a peticiones en lenguaje natural tanto en español como en inglés. En vez de usar comandos con formato específico, puedes simplemente escribir lo que necesitas.

### Tipos de Intenciones Reconocidas

1. **Búsqueda de información**
   - "Busca información sobre Python"
   - "Encuentra datos de web scraping"
   - "Search for machine learning"
   - "Find information about artificial intelligence"

2. **Iniciar scraping**
   - "Inicia un scraping en amazon.com"
   - "Haz un scraping de la página books.toscrape.com"
   - "Crawl the website github.com"
   - "Visit and extract from stackoverflow.com"

3. **Consulta de conocimiento**
   - "Qué sabes sobre JavaScript?"
   - "Háblame de bases de datos"
   - "Tell me what you know about APIs"
   - "Explain web development"

4. **Generar snapshot**
   - "Genera un snapshot del cerebro"
   - "Crea una imagen del estado actual"
   - "Generate a brain snapshot"
   - "Create a snapshot of the knowledge base"

5. **Consulta de estado**
   - "Cuál es el estado actual?"
   - "Cómo va el scraping?"
   - "What's the current status?"
   - "How's the process going?"

6. **Edición de archivos**
   - "Edita el archivo config.json"
   - "Modifica el código de main.py"
   - "Edit the documentation file"
   - "Update this configuration file"
   - "Can you change the script?"

7. **Comandos de terminal**
   - "Ejecuta dir en el terminal"
   - "Corre el comando 'whoami' en PowerShell"
   - "Run 'ls' in the terminal"
   - "Execute 'ipconfig' command"

### Ejemplos de Uso

```text
> Busca información sobre inteligencia artificial
[Detectada intención: búsqueda de "inteligencia artificial"]
Iniciando búsqueda sobre inteligencia artificial...
[Resultados de la base de conocimiento]
```

```text
> Inicia un scraping en https://books.toscrape.com
[Detectada intención: iniciar scraping]
Configurando scraping para: https://books.toscrape.com
Proceso de scraping iniciado. Puedes ver el progreso en la pestaña de monitoreo.
```

```text
> Edita el archivo config.json
[Detectada intención: editar archivo 'config.json']
📄 Contenido de config.json:
{
    "version": "1.0",
    "settings": {
        "timeout": 30,
        "user_agent": "WebScraperPRO Bot"
    }
}
```

```text
> Ejecuta dir en el terminal
[Detectada intención: ejecutar comando en terminal 'dir']
🖥️ Ejecutando: dir
📤 Salida:
 Volume in drive C has no label.
 Directory of C:\Users\DELL\Desktop\PythonWebScraper

 [Listado de archivos...]
```

### Funcionamiento Interno

1. El mensaje del usuario es procesado por `IntentRecognizer` que utiliza patrones y palabras clave para identificar intenciones
2. Se extraen parámetros importantes como URLs o consultas
3. Si la intención se detecta con suficiente confianza (>60%), se ejecuta la acción correspondiente
4. El sistema proporciona retroalimentación sobre la intención detectada
5. Las respuestas mantienen el formato bilingüe (español/inglés)
