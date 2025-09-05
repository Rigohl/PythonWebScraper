# WebScraperPRO - Chat Avanzado con Procesamiento de Lenguaje Natural

## Características del Chat Inteligente

El chat del WebScraperPRO ahora incluye procesamiento avanzado de lenguaje natural que permite interactuar con el sistema usando comandos en lenguaje natural tanto en español como en inglés. Las nuevas capacidades incluyen:

1. **Reconocimiento de intenciones**: El sistema identifica automáticamente qué quieres hacer basado en tu mensaje.

2. **Edición de archivos**: Modifica archivos del sistema directamente desde el chat.

3. **Ejecución de comandos**: Ejecuta comandos seguros en terminal desde la interfaz de chat.

4. **Procesamiento bilingüe**: Todas las funciones disponibles en español e inglés.

5. **Respuestas contextuales**: El sistema responde basado en el contexto y la base de conocimiento.

## Modos de Interacción

### 1. Comandos Explícitos (prefijo `/`)

Acceso directo a funcionalidades usando comandos con formato específico:

```bash
/edit config.json
/terminal dir
/crawl https://example.com
/kb inteligencia artificial
```

### 2. Lenguaje Natural

Interacción usando lenguaje conversacional normal:

```text
"Edita el archivo config.json"
"Ejecuta dir en el terminal"
"Inicia un scraping en example.com"
"Qué sabes sobre inteligencia artificial"
```

## Ejemplos de Uso

### Edición de Archivos

**Con comando explícito:**

```bash
/edit config.json
```

**Con lenguaje natural:**

```text
"Edita el archivo config.json"
"Modifica el contenido de app.py"
"Cambia 'timeout: 30' por 'timeout: 60' en config.json"
```

### Ejecución de Comandos

**Con comando explícito:**

```bash
/terminal dir
```

**Con lenguaje natural:**

```text
"Ejecuta dir en el terminal"
"Corre el comando 'whoami'"
"Run 'pip list' in the terminal"
```

## Seguridad

El sistema incluye medidas de seguridad para proteger tu sistema:

- Solo se permiten editar archivos con extensiones seguras (.py, .md, .txt, .html, .css, .json, .csv, .log)
- Comandos de terminal restringidos a operaciones informativas y seguras (dir, ls, echo, etc.)
- Bloqueo automático de comandos potencialmente peligrosos

## Compatibilidad

Esta funcionalidad está disponible en todas las plataformas soportadas:

- Windows (PowerShell)
- macOS (Bash/Zsh)
- Linux (Bash)

## Modo TUI-Pro

En modo TUI-Pro (interfaz de terminal profesional), activa el chat con F9 y disfruta de todas estas capacidades.
