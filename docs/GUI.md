# WebScraper PRO – GUI de Escritorio (PyQt6)

Interfaz de control profesional con estetica "hacker moderno" que aprovecha el 100% del cerebro hibrido del scraper. Permite iniciar, monitorear y detener sesiones de scraping inteligente en tiempo real.

## Caracteristicas Clave
- Panel de control unificado (URLs, concurrencia, RL, hot reload, robots.txt)
- Logs en tiempo real (stream directo del logger raiz)
- Visualizacion de actividad del cerebro hibrido (barra animada y ojos reactivos)
- Ejecucion en hilo dedicado seguro (no bloquea GUI)
- Estilo oscuro con acentos cian (custom QSS)

## Lanzamiento
1. Instala dependencias (si aun no):
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el launcher y selecciona la Opcion 1:
   ```bash
   WebScraperPRO.bat
   ```
3. Si PyQt6 no esta disponible, el sistema hara fallback automatico a TUI Pro y luego a TUI clasico.

## Uso Basico
1. Ingresa una o varias URLs iniciales separadas por coma.
2. Ajusta el nivel de concurrencia y activa/desactiva: RL / Hot Reload / Respeto robots.txt.
3. Pulsa "Start" para iniciar. Observa:
   - Logs: Flujo detallado de eventos.
   - Stats: Datos de callbacks (pendiente de ampliacion con mas metricas del cerebro).
   - Robot: Ojos y barra se intensifican segun actividad reciente.
4. Pulsa "Stop" para solicitar parada. El hilo se desmonta limpiamente.

## Arquitectura Interna
- `controller.py`: Gestiona hilo + event loop asyncio. Expone señales Qt.
- `log_handler.py`: Handler logging -> señales Qt.
- `robot_widget.py`: Widget animado minimalista con futura extensibilidad (emociones, alertas).
- `app.py`: Composicion de interfaz y wiring.
- `styles.qss`: Hoja de estilo unificada.

## Extensiones Sugeridas Futuras
- Panel avanzado de conocimiento (consultas directas al cerebro hibrido).
- Dashboard de dominios con prioridad, backoff y calidad.
- Sistema de alertas proactivas (anomalies / ethical flags / drift).
- Editor visual de reglas RL / Frontier Classifier.

## Notas Tecnicas
- El runner ya soporta `stats_callback`; ampliar para enviar mas contexto (tiempos, queue_size, dominios activos).
- Para instrumentar mayor actividad cerebral, exponer metodo ligero en HybridBrain y llamarlo periodicamente.
- Evitar bloqueos: Nunca ejecutar tareas intensivas en el hilo GUI.

## Mantenimiento
Si la GUI no abre:
- Verificar `pip show PyQt6`.
- Revisar logs en `logs/scraper_run.log` para excepciones previas.

## Licencia
Se hereda la licencia del proyecto principal.
