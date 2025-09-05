# Conversational AI Features - PythonWebScraper

## 🎯 Introducción

El PythonWebScraper ahora incluye capacidades avanzadas de inteligencia artificial conversacional que permiten interactuar con el sistema utilizando lenguaje natural en español e inglés.

## 🚀 Nuevas Funcionalidades

### 1. **Interfaz de Chat Inteligente**
- Chat integrado en la interfaz TUI
- Procesamiento de lenguaje natural
- Detección automática de intenciones
- Historial de conversación
- Notificaciones en tiempo real

### 2. **Sistema de Gestión de Bots**
- Creación automática de bots especializados
- 5 tipos de bots: Scraper, Monitor, Crawler, Analyzer, Search
- Configuración inteligente desde descripciones en lenguaje natural
- Gestión completa del ciclo de vida de bots

### 3. **Motor de IA Conversacional**
- Reconocimiento de intenciones por patrones
- Soporte para comandos complejos
- Contexto de conversación persistente
- Integración opcional con LLMs

### 4. **Procesador de Comandos Avanzado**
- Ejecución asíncrona de comandos
- Búsqueda web inteligente
- Análisis de datos automático
- Exportación y gestión de resultados

## 💬 Comandos Soportados

### Búsqueda
```
busca información sobre Python
encuentra datos de APIs REST
search for web scraping tools
```

### Scraping
```
extrae datos de https://ejemplo.com
hacer scraping de esta página
crawl these URLs
```

### Creación de Bots
```
crea un bot para monitorear precios
genera un scraper para noticias
create a monitoring bot for changes
```

### Análisis
```
analiza los datos recopilados
examina las tendencias del mercado
analyze the scraped content
```

### Sistema
```
estado del sistema
cómo va el progreso
ayuda
```

## 🛠️ Uso

### 1. Interfaz TUI con Chat
```bash
python -m src.main --tui
```
- Navega a la pestaña "Chat AI"
- Escribe comandos en lenguaje natural
- Usa Ctrl+C para enfocar el chat

### 2. Demo Conversacional
```bash
python demo_conversation.py
```

### 3. Modo Demo Tradicional
```bash
python -m src.main --demo
```

## 🏗️ Arquitectura

### Módulos Principales

1. **`src/intelligence/conversation_ai.py`**
   - Motor principal de IA conversacional
   - Detección de intenciones
   - Gestión de contexto

2. **`src/intelligence/bot_manager.py`**
   - Sistema de gestión de bots
   - Configuración automática
   - Persistencia de estado

3. **`src/intelligence/command_processor.py`**
   - Procesamiento y ejecución de comandos
   - Integración con componentes existentes
   - Manejo de operaciones asíncronas

4. **`src/tui/chat_widget.py`**
   - Widget de chat para Textual
   - Interfaz de usuario rica
   - Integración con el TUI existente

### Flujo de Datos
```
Usuario → Chat Widget → Conversational AI → Command Processor → Bot Manager / Orchestrator
```

## 🧪 Testing

### Ejecutar Tests
```bash
python -m pytest tests/test_conversation_ai.py -v
```

### Tests Incluidos
- Detección de intenciones
- Procesamiento de comandos
- Gestión de bots
- Análisis de sistema

## 🎨 Ejemplos de Uso

### Ejemplo 1: Búsqueda Automatizada
```
Usuario: "busca información sobre machine learning APIs"
Sistema: Crea bot de búsqueda → Genera URLs → Inicia scraping automático
```

### Ejemplo 2: Monitoreo Continuo
```
Usuario: "crea un bot para monitorear cambios en precios de productos"
Sistema: Configura bot tipo Monitor → Programa ejecución → Notifica cambios
```

### Ejemplo 3: Análisis Inteligente
```
Usuario: "analiza los datos de las últimas búsquedas"
Sistema: Procesa resultados → Genera estadísticas → Crear resumen
```

## ⚙️ Configuración

### Variables de Entorno
```bash
# Opcional: Habilitar LLM para análisis avanzado
LLM_API_KEY=tu_api_key_aqui
LLM_MODEL=gpt-3.5-turbo

# Base de datos
DB_PATH=data/scraper_database.db

# Configuración de bots
CONCURRENCY=3
ROBOTS_ENABLED=false
```

### Archivos de Configuración
- `bots/bot_configs.json` - Configuraciones de bots persistentes
- `data/scraper_database.db` - Base de datos principal
- `logs/scraper_run.md` - Logs del sistema

## 🚨 Consideraciones

### Rendimiento
- Los bots ejecutan operaciones asíncronas
- Uso responsable de concurrencia
- Respeto a robots.txt configurable

### Seguridad
- Validación de URLs
- Sanitización de entradas
- Manejo seguro de errores

### Escalabilidad
- Gestión de memoria eficiente
- Persistencia de estado
- Arquitectura modular

## 🔧 Solución de Problemas

### Error: Base de datos no encontrada
```bash
# Asegúrate de que existe el directorio data/
mkdir -p data/
```

### Error: LLM no configurado
```bash
# Es opcional, el sistema funciona sin LLM
export LLM_API_KEY=""
```

### Error: Dependencias faltantes
```bash
pip install -r requirements.txt
```

## 📚 Recursos Adicionales

- [Documentación de Textual](https://textual.textualize.io/)
- [Guía de Pydantic](https://docs.pydantic.dev/)
- [Documentación de AsyncIO](https://docs.python.org/3/library/asyncio.html)

## 🤝 Contribuciones

Para contribuir al desarrollo de estas funcionalidades:

1. Revisa los tests existentes
2. Mantén la compatibilidad con la arquitectura actual
3. Documenta nuevas funcionalidades
4. Sigue las convenciones de código existentes

---

*Desarrollado como extensión modular del PythonWebScraper original, manteniendo total compatibilidad con funcionalidades existentes.*