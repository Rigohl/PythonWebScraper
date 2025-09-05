# src/intelligence/intent_recognizer.py

import re
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

class IntentType(Enum):
    """Tipos de intenciones que se pueden detectar en el chat."""
    UNKNOWN = "unknown"
    SEARCH = "search"        # Buscar información
    CRAWL = "crawl"          # Iniciar scraping
    KNOWLEDGE = "knowledge"  # Consultar conocimiento
    SNAPSHOT = "snapshot"    # Generar snapshot
    STATUS = "status"        # Verificar estado
    EDIT = "edit"            # Editar archivos
    TERMINAL = "terminal"    # Ejecutar comandos en terminal

class Intent:
    """Representa una intención detectada en un mensaje."""

    def __init__(self,
                 intent_type: IntentType = IntentType.UNKNOWN,
                 confidence: float = 0.0,
                 parameters: Dict[str, Any] = None):
        self.type = intent_type
        self.confidence = confidence  # 0.0 - 1.0
        self.parameters = parameters or {}

    def __repr__(self):
        return f"Intent(type={self.type}, confidence={self.confidence:.2f}, parameters={self.parameters})"

class IntentRecognizer:
    """Reconocedor de intenciones para el chat."""

    # Patrones para detectar intenciones (español e inglés)
    INTENT_PATTERNS = {
        # Patrones para búsqueda
        IntentType.SEARCH: [
            r"\b(busc|busca|encontr|hall|localiz)[a-z]* (?:info|información|datos|sobre|acerca)?\s*(.+)",
            r"\b(search|find|look)\s+(?:for|about)?\s+(.+)",
            r"\b(qué|dime|cómo|explica)[a-z]* (?:es|son|está|sobre)?\s*(.+)"
        ],

        # Patrones para iniciar scraping
        IntentType.CRAWL: [
            r"\b(scrap[a-z]*|extraer?|recorrer?|navega[a-z]*|visita[a-z]*|explora[a-z]*) (?:en |la página |la web |el sitio |la url |)(?:de |)(.+?)(?:\s|$|\.)",
            r"\b(crawl|scrape|extract|visit|explore)\s+(?:from |the |website |page |url |)(?:of |)(.+?)(?:\s|$|\.)"
        ],

        # Patrones para consultar base de conocimiento
        IntentType.KNOWLEDGE: [
            r"\b(qué sabes|conoces|dime|háblame) (?:sobre|acerca de|de)\s+(.+)",
            r"\b(what do you know|tell me|explain) (?:about)\s+(.+)"
        ],

        # Patrones para generar snapshot
        IntentType.SNAPSHOT: [
            r"\b(genera|crea|haz|produce)[a-z]* (?:un |el |)(?:snapshot|instantánea|captura|imagen)(?:\s|$|\.)",
            r"\b(generate|create|make|produce)\s+(?:a |the |)(?:snapshot|image|capture)(?:\s|$|\.)"
        ],

        # Patrones para verificar estado
        IntentType.STATUS: [
            r"\b(estado|situación|progreso|cómo va|status)(?:\s|$|\.)",
            r"\b(status|progress|how is it going|state)(?:\s|$|\.)"
        ],

        # Patrones para edición de archivos
        IntentType.EDIT: [
            r"\b(editar?|modificar?|cambiar?|actualizar?) (?:el |este |la |esta |los |estas |)(?:archivo|fichero|documento|código|file|script|contenido|content)(?:\s|$|\.)",
            r"\b(edit|modify|change|update|fix) (?:the |this |these |)(?:file|document|code|script|content|configuration)(?:\s|$|\.)",
            r"\b(puedes|podrías) (?:editar|modificar|cambiar|actualizar|corregir)(?:\s|$|\.)",
            r"\b(can you|could you) (?:edit|modify|change|update|fix)(?:\s|$|\.)",
            r"\b(necesito|quiero) (?:cambiar|modificar|editar|actualizar)(?:\s|$|\.)",
            r"\b(need|want) to (?:change|modify|edit|update|fix)(?:\s|$|\.)",
            r"\b(cambia|reemplaza|sustituye|cambiar|reemplazar|sustituir) ['\"](.*?)['\"] (?:por|a|to|with) ['\"](.*?)['\"](?:\s|en |in |inside |dentro de |)([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)?",
            r"\b(change|replace) ['\"](.*?)['\"] (?:to|with|by) ['\"](.*?)['\"](?:\s|en |in |inside |dentro de |)([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)?"
        ],

        # Patrones para comandos de terminal
        IntentType.TERMINAL: [
            r"\b(ejecuta|corre|lanza|correr?|lanzar?|usar?) (?:en |el |un |este |)(terminal|cmd|powershell|comando|command)(?:\s|$|\.)",
            r"\b(run|execute|launch|use) (?:in |the |this |)(?:terminal|cmd|powershell|command|shell)(?:\s|$|\.)",
            r"\b(ejecuta|corre|usa) (?:el comando |)(\"[^\"]+\"|\'[^\']+\'|`[^`]+`)(?:\s|$|\.)",
            r"\b(run|execute|use) (?:the command |)(\"[^\"]+\"|\'[^\']+\'|`[^`]+`)(?:\s|$|\.)",
            r"\b(ejecuta|corre|usa|run|execute) (?:el comando |the command |)([a-zA-Z0-9_\-\.]+(?:\s+[^\n]*)?)(?:\s|$|\.)"
        ]
    }

    @classmethod
    def extract_url(cls, text: str) -> Optional[str]:
        """Extrae una URL del texto si está presente."""
        url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+\.[^\s<>"\']+'
        match = re.search(url_pattern, text)
        if match:
            return match.group(0)
        return None

    @classmethod
    def recognize(cls, text: str) -> Intent:
        """
        Reconoce la intención en un mensaje de texto.

        Args:
            text: El texto del mensaje a analizar

        Returns:
            Intent: La intención detectada con su tipo, confianza y parámetros
        """
        text = text.lower().strip()
        best_intent = Intent()

        # Buscar coincidencias para cada tipo de intención
        for intent_type, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = 0.7  # Base confidence

                    # Aumentar confianza si hay palabras clave específicas
                    if intent_type == IntentType.CRAWL and ("scraping" in text or "scrapear" in text):
                        confidence = 0.9
                    elif intent_type == IntentType.SEARCH and ("busca" in text or "search" in text):
                        confidence = 0.85
                    elif intent_type == IntentType.KNOWLEDGE and ("sabes" in text or "know" in text):
                        confidence = 0.8

                    # Si es mejor que la intención actual
                    if confidence > best_intent.confidence:
                        params = {}

                        # Extraer parámetros según el tipo de intención
                        if intent_type == IntentType.SEARCH:
                            if len(match.groups()) > 1 and match.group(2):
                                query = match.group(2).strip()
                            else:
                                # Buscar patrón más general para buscar
                                search_pattern = r'\b(?:busca|buscar|find|search|encontrar)\s+(?:información|info|datos|about|for)?\s*(.+)'
                                search_match = re.search(search_pattern, text, re.IGNORECASE)
                                query = search_match.group(1).strip() if search_match else ""
                            params["query"] = query

                        elif intent_type == IntentType.CRAWL:
                            url = match.group(2) if len(match.groups()) > 1 else ""
                            # Si no es una URL explícita, intentar extraer una
                            if not (url.startswith("http") or url.startswith("www")):
                                extracted_url = cls.extract_url(text)
                                if extracted_url:
                                    url = extracted_url
                            params["url"] = url

                        elif intent_type == IntentType.KNOWLEDGE:
                            topic = match.group(2) if len(match.groups()) > 1 else ""
                            params["topic"] = topic

                        elif intent_type == IntentType.EDIT:
                            # Extraer el nombre del archivo si está presente
                            # Buscar posibles menciones a nombres de archivo
                            file_pattern = r'(?:el archivo|el fichero|file|document|archivo|fichero|script|código)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)'
                            file_match = re.search(file_pattern, text, re.IGNORECASE)
                            if file_match:
                                params["file"] = file_match.group(1)
                            else:
                                # Buscar cualquier patrón que parezca un nombre de archivo
                                file_pattern2 = r'[\s"]([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)[\s"]'
                                file_match2 = re.search(file_pattern2, text)
                                if file_match2:
                                    params["file"] = file_match2.group(1)

                            # Buscar archivo al final de una sustitución (cambia X por Y en archivo.ext)
                            file_pattern3 = r'(?:en|in)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)'
                            file_match3 = re.search(file_pattern3, text, re.IGNORECASE)
                            if file_match3:
                                params["file"] = file_match3.group(1)

                            # Extraer el contenido a modificar si está presente
                            content_pattern = r'(?:cambiar|modificar|sustituir|reemplazar|change|modify|replace)\s+["\'`]([^"\'`]+)["\'`]\s+(?:por|a|with|to)\s+["\'`]([^"\'`]+)["\'`]'
                            content_match = re.search(content_pattern, text, re.IGNORECASE)
                            if content_match:
                                params["old_content"] = content_match.group(1)
                                params["new_content"] = content_match.group(2)

                        elif intent_type == IntentType.TERMINAL:
                            # Extraer el comando a ejecutar
                            command_pattern = r'["\'`]([^"\'`]+)["\'`]'
                            command_match = re.search(command_pattern, text)
                            if command_match:
                                params["command"] = command_match.group(1)
                            else:
                                # Buscar cualquier cosa después de las palabras clave
                                # Primer patrón: buscar verbo + terminal + resto
                                cmd_pattern1 = r'(?:ejecuta|corre|usa|run|execute|launch)\s+(?:en |el |un |este |in |the |this |)(?:terminal|cmd|powershell|comando|command|shell)\s+(.+?)(?:$|\.)'
                                cmd_match1 = re.search(cmd_pattern1, text, re.IGNORECASE)

                                # Segundo patrón: buscar solo verbo + resto
                                cmd_pattern2 = r'(?:ejecuta|corre|usa|run|execute|launch)\s+(.+?)(?:$|\.)'
                                cmd_match2 = re.search(cmd_pattern2, text, re.IGNORECASE)

                                if cmd_match1:
                                    cmd_text = cmd_match1.group(1).strip()
                                    params["command"] = cmd_text
                                elif cmd_match2:
                                    cmd_text = cmd_match2.group(1).strip()
                                    # Limpiar palabras intermedias comunes
                                    cmd_text = re.sub(r'\b(en|in|el|the|un|a|este|this|terminal|cmd|powershell|command)\b', '', cmd_text, flags=re.IGNORECASE).strip()
                                    if cmd_text:
                                        params["command"] = cmd_text

                        best_intent = Intent(intent_type, confidence, params)

        return best_intent

# Ejemplo de uso
if __name__ == "__main__":
    test_messages = [
        # Mensajes básicos
        "Busca información sobre Python",
        "Inicia un scraping en https://books.toscrape.com",
        "Qué sabes sobre inteligencia artificial",
        "Genera un snapshot del cerebro",
        "Cuál es el estado actual del scraping",

        # Nuevos mensajes para edición de archivos
        "Edita el archivo config.json",
        "Modifica el código en main.py",
        "Can you update this script?",
        "Cambia 'timeout: 30' por 'timeout: 60'",

        # Nuevos mensajes para comandos de terminal
        "Ejecuta 'dir' en el terminal",
        "Corre el comando whoami",
        "Run 'ls -la' in terminal",
        "Execute ipconfig",

        # Mensajes sin intención específica
        "Hola, como estas?",
        "Gracias por tu ayuda",
        "What time is it?"
    ]

    for msg in test_messages:
        intent = IntentRecognizer.recognize(msg)
        print(f"Mensaje: '{msg}'")
        print(f"Intención: {intent}\n")
