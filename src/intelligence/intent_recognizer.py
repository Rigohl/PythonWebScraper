# src/intelligence/intent_recognizer.py

import re
import shlex
from enum import Enum
from typing import Any, Dict


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

        # Patrones para edición de archivos (mejorados para evitar colisiones)
        IntentType.EDIT: [
            # Patrones específicos para edición con verbos explícitos (no-capturing verbs)
            r"\b(?:editar?|modificar?|cambiar?|actualizar?|corregir?) (?:el |este |la |esta |los |estas |)(?:archivo|fichero|documento|código|file|script|contenido|content)(?:\s|$|\.)",
            r"\b(?:edit|modify|change|update|fix) (?:the |this |these |)(?:file|document|code|script|content|configuration)(?:\s|$|\.)",
            r"\b(?:puedes|podrías) (?:editar|modificar|cambiar|actualizar|corregir)(?:\s|$|\.)",
            r"\b(?:can you|could you) (?:edit|modify|change|update|fix)(?:\s|$|\.)",
            r"\b(?:necesito|quiero) (?:cambiar|modificar|editar|actualizar)(?:\s|$|\.)",
            r"\b(?:need|want) to (?:change|modify|edit|update|fix)(?:\s|$|\.)",
            # Reemplazo específico con comillas (alta precisión)
            r"\b(?:cambia|reemplaza|sustituye|cambiar|reemplazar|sustituir) ['\"](.*?)['\"] (?:por|a|to|with) ['\"](.*?)['\"](?:\s|en |in |inside |dentro de |)([a-zA-Z0-9_\-\.\/\\]+(?:\/[a-zA-Z0-9_\-\.]+)*\.[a-zA-Z0-9]+)?",
            r"\b(?:change|replace) ['\"](.*?)['\"] (?:to|with|by) ['\"](.*?)['\"](?:\s|en |in |inside |dentro de |)([a-zA-Z0-9_\-\.\/\\]+(?:\/[a-zA-Z0-9_\-\.]+)*\.[a-zA-Z0-9]+)?",
            # Mostrar / abrir archivo (con rutas mejoradas)
            r"\b(?:muestra|enséñame|ensename|abre|abre el|visualiza|ver|mostrar) (?:el |la |el archivo |el fichero |el script |)([a-zA-Z0-9_\-\.\/\\]+(?:\/[a-zA-Z0-9_\-\.]+)*\.[a-zA-Z0-9]+)",
            r"\b(?:show|open|display|view) (?:the |this |file |)([a-zA-Z0-9_\-\.\/\\]+(?:\/[a-zA-Z0-9_\-\.]+)*\.[a-zA-Z0-9]+)",
            # Añadir / insertar contenido (con rutas mejoradas)
            r"\b(agrega|añade|anade|append|inserta|inserte|inserte la|insert) (?:línea |line |texto |content |)(['\"]([^'\"]+)['\"]) (?:a |al |al final de |to |into |en |)([a-zA-Z0-9_\-\.\/\\]+(?:\/[a-zA-Z0-9_\-\.]+)*\.[a-zA-Z0-9]+)",
            # Reemplazar línea específica (con rutas mejoradas)
            r"\b(reemplaza|sustituye|replace) (?:la |la línea |line |linea |línea |line )?(?:linea |línea |line |ln)?\s*(\d+) (?:por|with) ['\"]([^'\"]+)['\"] (?:en |in |de |)([a-zA-Z0-9_\-\.\/\\]+(?:\/[a-zA-Z0-9_\-\.]+)*\.[a-zA-Z0-9]+)",
        ],

        # Patrones para comandos de terminal
        IntentType.TERMINAL: [
            r"\b(ejecuta|corre|lanza|correr?|lanzar?|usar?) (?:en |el |un |este |)(terminal|cmd|powershell|comando|command)(?:\s|$|\.)",
            r"\b(run|execute|launch|use) (?:in |the |this |)(?:terminal|cmd|powershell|command|shell)(?:\s|$|\.)",
            r"\b(ejecuta|corre|usa) (?:el comando |)(\"[^\"]+\"|\'[^\']+\'|`[^`]+`)(?:\s|$|\.)",
            r"\b(run|execute|use) (?:the command |)(\"[^\"]+\"|\'[^\']+\'|`[^`]+`)(?:\s|$|\.)",
            r"\b(ejecuta|corre|usa|run|execute) (?:el comando |the command |)([a-zA-Z0-9_\-\.]+(?:\s+[^\n]*)?)(?:\s|$|\.)",
            # Peticiones naturales comunes (sin archivos para evitar colisión con EDIT)
            r"\b(lista|listar) (?:archivos|files)(?:\s|$|\.)",
            r"\b(quien soy|quién soy)(?:\s|$|\.)",
            r"\b(where am i|donde estoy|dónde estoy)(?:\s|$|\.)",
            # Patrones específicos para PowerShell (cmdlets sin verbo explícito)
            r"\b(get|set|new|remove|start|stop|restart|enable|disable|test|invoke|clear|select|sort|measure|convert|format|write|out|import|export|where|foreach|join|compare)-[a-zA-Z][a-zA-Z0-9\-]*(?:\s+[^\n]*)?(?:\s|$|\.)",
            r"\b(get|set|new|remove|start|stop|restart|enable|disable|test|invoke|clear|select|sort|measure|convert|format|write|out|import|export|where|foreach|join|compare)[a-zA-Z][a-zA-Z0-9\-]*(?:\s+[^\n]*)?(?:\s|$|\.)",
            # Patrones para comandos PowerShell comunes
            r"\b(get-process|get-service|get-childitem|set-location|new-item|remove-item|copy-item|move-item)(?:\s+[^\n]*)?(?:\s|$|\.)",
            r"\b(dir|ls|pwd|whoami|ipconfig|netstat|tasklist|taskkill)(?:\s+[^\n]*)?(?:\s|$|\.)"
        ]
    }

    @classmethod
    def _is_valid_file_path(cls, path: str) -> bool:
        """Valida si una cadena parece ser una ruta de archivo válida con mejor soporte para subdirectorios."""
        if not path or len(path) > 260:  # MAX_PATH en Windows
            return False

        # Limpiar la ruta de caracteres problemáticos
        path = path.strip('"\'')

        # Rechazar intentos explícitos de traversal fuera del repo
        if '..' in path.replace('\\', '/').split('/'):
            return False

        # Patrones de archivos válidos mejorados
        valid_patterns = [
            r'^[a-zA-Z]:[\\\/]',  # Ruta absoluta Windows
            r'^[\/~]',  # Ruta absoluta Unix/Linux
            r'^[\.\/]',  # Ruta relativa
            # Archivos con extensión (soporte para subdirectorios)
            r'^[a-zA-Z0-9_][a-zA-Z0-9_\-\.\/\\]*[\/\\][a-zA-Z0-9_][a-zA-Z0-9_\-\.]*\.[a-zA-Z0-9]+$',  # con subdir
            r'^[a-zA-Z0-9_][a-zA-Z0-9_\-\.]*\.[a-zA-Z0-9]+$',  # sin subdir
            # Archivos sin extensión (soporte para subdirectorios)
            r'^[a-zA-Z0-9_][a-zA-Z0-9_\-\.\/\\]*[\/\\][a-zA-Z0-9_][a-zA-Z0-9_\-\.]*$',  # con subdir
            r'^[a-zA-Z0-9_][a-zA-Z0-9_\-\.]*$',  # sin subdir
            # Extensiones múltiples (ej: .tar.gz)
            r'^[a-zA-Z0-9_][a-zA-Z0-9_\-\.\/\\]*\.[a-zA-Z0-9]+\.[a-zA-Z0-9]+$',  # doble extensión
        ]

        for pattern in valid_patterns:
            if re.match(pattern, path):
                return True

        return False

    @classmethod
    def _normalize_command(cls, command: str, shell_type: str) -> str:
        """Normaliza comandos según el tipo de shell y sistema operativo."""
        if not command:
            return ""
        # Tokenize the command safely and only replace the first token (the executable/verb).
        # This avoids replacing substrings inside args, paths or quoted sections.
        try:
            # Use posix=True so shlex handles quotes consistently across platforms for our purposes.
            tokens = shlex.split(command, posix=True)
        except Exception:
            tokens = command.strip().split()

        if not tokens:
            return command

        cmd_token = tokens[0]

        def replace_first_token(mapping: Dict[str, str]) -> str:
            key = cmd_token.lower()
            if key in mapping:
                new_cmd = mapping[key]
                rest = tokens[1:]
                # If replacement contains spaces (expanded form), keep as-is then append rest
                return ' '.join([new_cmd] + rest) if rest else new_cmd
            return None

        if shell_type == "powershell":
            replacements = {
                'dir': 'Get-ChildItem',
                'ls': 'Get-ChildItem',
                'pwd': 'Get-Location',
                'cd': 'Set-Location',
                'cat': 'Get-Content',
                'type': 'Get-Content',
                'copy': 'Copy-Item',
                'cp': 'Copy-Item',
                'move': 'Move-Item',
                'mv': 'Move-Item',
                'del': 'Remove-Item',
                'rm': 'Remove-Item',
                'mkdir': 'New-Item -ItemType Directory',
                'md': 'New-Item -ItemType Directory'
            }
            replaced = replace_first_token(replacements)
            if replaced is not None:
                return replaced

        if shell_type in ("bash", "sh"):
            replacements = {
                'dir': 'ls',
                'type': 'cat',
                'copy': 'cp',
                'move': 'mv',
                'del': 'rm',
                'md': 'mkdir',
                'rd': 'rmdir'
            }
            replaced = replace_first_token(replacements)
            if replaced is not None:
                return replaced

        # If nothing matched or unknown shell, return the original command unmodified.
        return command

    @classmethod
    def _extract_command_flags(cls, command: str) -> Dict[str, Any]:
        """Extrae flags y opciones de un comando."""
        flags = {}

        # Patrones comunes de flags
        flag_patterns = [
            (r'-([a-zA-Z])\s+([^\s]+)', 'short_flag'),  # -a value
            (r'--([a-zA-Z-]+)\s+([^\s]+)', 'long_flag'),  # --verbose value
            (r'-([a-zA-Z])([^\s]*)', 'short_flag_compact'),  # -la
            (r'/([a-zA-Z])\s+([^\s]+)', 'windows_flag'),  # /a value
        ]

        for pattern, flag_type in flag_patterns:
            matches = re.findall(pattern, command)
            for match in matches:
                if flag_type == 'short_flag':
                    flags[f'-{match[0]}'] = match[1]
                elif flag_type == 'long_flag':
                    flags[f'--{match[0]}'] = match[1]
                elif flag_type == 'short_flag_compact':
                    flags[f'-{match[0]}'] = match[1] if match[1] else True
                elif flag_type == 'windows_flag':
                    flags[f'/{match[0]}'] = match[1]

        return flags

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
        matches_found = []
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
                            # Extraer el nombre del archivo con múltiples patrones mejorados
                            content_patterns = [
                                # Patrón estándar: cambiar X por Y en archivo
                                r'(?:cambiar|modificar|sustituir|reemplazar|change|modify|replace)\s*["\']([^"\']+)["\']\s*(?:por|a|con|to|with|by)\s*["\']([^"\']+)["\']\s*en\s*([^\s]+)',
                                # Edita el archivo <filename>
                                r'(?:edita|modifica|actualiza|cambia|change|edit|update|modify)\s+(?:el\s+archivo\s+|the\s+file\s+)?([\w\-.]+\.[A-Za-z0-9]+)',
                                # Patrón estándar: cambiar X por Y
                                r'(?:cambiar|modificar|sustituir|reemplazar|change|modify|replace)\s*["\"][^"\"]+["\"]\s*(?:por|a|con|to|with|by)\s*["\"][^"\"]+["\"]',
                                # Patrón alternativo: X -> Y en archivo
                                r'["\"][^"\"]+["\"]\s*(?:->|→|=>)\s*["\"][^"\"]+["\"]\s*(?:en|in|inside|dentro de|de)?\s*([a-zA-Z0-9_\-\./\\]+(?:[\/\\][a-zA-Z0-9_\-\.]+)*[\/\\]?[a-zA-Z0-9_\-\.]*\.[a-zA-Z0-9]+)?',
                                # Patrón alternativo: X -> Y
                                r'["\"][^"\"]+["\"]\s*(?:->|→|=>)\s*["\"][^"\"]+["\"]',
                                # Patrón para añadir: añade "contenido"
                                r'(?:agrega|añade|anade|append|inserta|insert|add)\s*["\"][^"\"]+["\"]'
                            ]

                            for pattern in content_patterns:
                                content_match = re.search(pattern, text, re.IGNORECASE)
                                if content_match:
                                    # Si el patrón incluye archivo, extraerlo
                                    # Assign file if present in any group
                                    if len(content_match.groups()) == 1 and content_match.group(1):
                                        params["file"] = content_match.group(1)
                                    elif len(content_match.groups()) == 3:
                                        params["old_content"] = content_match.group(1)
                                        params["new_content"] = content_match.group(2)
                                        params["file"] = content_match.group(3)
                                    elif len(content_match.groups()) == 2:
                                        params["old_content"] = content_match.group(1)
                                        params["new_content"] = content_match.group(2)
                                    else:
                                        # Try to extract filename from text if not matched
                                        filename_match = re.search(r'(\w+\.\w+)', text)
                                        if filename_match:
                                            params["file"] = filename_match.group(1)
                                        params["new_content"] = content_match.group(1)
                                    break

                            # If we detected a replace action and file still not found,
                            # try to capture 'en <filename>' patterns explicitly (Spanish/English)
                            if params.get("action") == "replace" and not params.get("file"):
                                en_file_match = re.search(r'\b(?:en|in|inside|dentro de|de)\s+([a-zA-Z0-9_\-\.\/\\]+\.[a-zA-Z0-9]+)\b', text, re.IGNORECASE)
                                if en_file_match:
                                    params["file"] = en_file_match.group(1)

                            # Determinar la acción con mayor precisión
                            action_keywords = {
                                "show": ['muestra', 'enséñame', 'ensename', 'abre', 'visualiza', 'ver', 'mostrar', 'show', 'open', 'display', 'view', 'read', 'cat'],
                                "append": ['agrega', 'añade', 'anade', 'append', 'inserta', 'inserte', 'insert', 'add', 'agregar'],
                                "remove": ['elimina', 'borra', 'borrar', 'remove', 'delete', 'quitar', 'sacar'],
                                "replace": ['cambia', 'reemplaza', 'sustituye', 'modifica', 'change', 'modify', 'replace', 'update']
                            }

                            detected_action = None
                            max_matches = 0
                            for action, keywords in action_keywords.items():
                                matches = sum(1 for keyword in keywords if keyword in text.lower())
                                if matches > max_matches:
                                    max_matches = matches
                                    detected_action = action

                            params["action"] = detected_action or "show"  # Default a mostrar si no se detecta acción clara

                            # Extraer contenido con mejor manejo de comillas
                            content_patterns = [
                                # Patrón estándar: cambiar X por Y
                                r'(?:cambiar|modificar|sustituir|reemplazar|change|modify|replace)\s*["\'`"]([^"\'`]+)["\'`"]\s*(?:por|a|con|to|with|by)\s*["\'`"]([^"\'`]+)["\'`"]',
                                # Patrón alternativo: X -> Y
                                r'["\'`"]([^"\'`]+)["\'`"]\s*(?:->|→|=>)\s*["\'`"]([^"\'`]+)["\'`"]',
                                # Patrón para añadir: añade "contenido"
                                r'(?:agrega|añade|anade|append|inserta|insert|add)\s*["\'`"]([^"\'`]+)["\'`"]'
                            ]

                            for pattern in content_patterns:
                                content_match = re.search(pattern, text, re.IGNORECASE)
                                if content_match:
                                    if len(content_match.groups()) >= 2:
                                        params["old_content"] = content_match.group(1)
                                        params["new_content"] = content_match.group(2)
                                    else:
                                        params["new_content"] = content_match.group(1)
                                    break

                            # Extraer línea específica con más flexibilidad
                            line_patterns = [
                                r'(?:línea|linea|line|ln|numero|número|num)\s*(\d+)',
                                r'#(\d+)',
                                r':(\d+)',
                                r'\b(\d+)\b\s*(?:line|línea)',
                                r'(\d+)-(\d+)',  # Rango de líneas
                            ]

                            for pattern in line_patterns:
                                line_match = re.search(pattern, text, re.IGNORECASE)
                                if line_match:
                                    try:
                                        if len(line_match.groups()) >= 2 and line_match.group(2):
                                            # Es un rango
                                            start_line = int(line_match.group(1))
                                            end_line = int(line_match.group(2))
                                            if 1 <= start_line <= 10000 and 1 <= end_line <= 10000 and start_line <= end_line:
                                                params["line_range"] = {"start": start_line, "end": end_line}
                                                break
                                        else:
                                            # Es una línea simple
                                            line_num = int(line_match.group(1))
                                            if 1 <= line_num <= 10000:  # Rango razonable
                                                params["line_number"] = line_num
                                                break
                                    except (ValueError, IndexError):
                                        continue

                            # Extraer contexto adicional (antes/después de línea)
                            context_patterns = [
                                r'(\d+)\s*(?:líneas?|lines?)\s*(?:antes|before|previas|arriba|above)',
                                r'(\d+)\s*(?:líneas?|lines?)\s*(?:después|after|siguientes|abajo|below)',
                                r'(\d+)\s*(?:líneas?|lines?)\s*(?:alrededor|around|around)',
                                r'contexto\s*(\d+)',
                                r'context\s*(\d+)'
                            ]

                            for i, pattern in enumerate(context_patterns):
                                context_match = re.search(pattern, text, re.IGNORECASE)
                                if context_match:
                                    context_lines = int(context_match.group(1))
                                    if i == 0:
                                        params["context_before"] = context_lines
                                    elif i == 1:
                                        params["context_after"] = context_lines
                                    else:  # around o context general
                                        params["context_before"] = context_lines
                                        params["context_after"] = context_lines

                            # Detectar si es una operación de búsqueda/reemplazo global
                            if re.search(r'\b(todo|all|global|todas|completo)\b', text, re.IGNORECASE):
                                params["global_replace"] = True

                            # Detectar si debe crear backup antes de modificar
                            if re.search(r'\b(backup|respaldo|copia|seguro)\b', text, re.IGNORECASE):
                                params["create_backup"] = True

                            # Mostrar archivo (action=view)
                            view_pattern = r"\b(muestra|enséñame|ensename|abre|open|display|view|ver|muestrame) (?:el |la |las |los |)(?:líneas?|lines?)?\s*(\d+(?:-\d+)?)?\s*(?:del |de |del archivo |la archivo |el fichero |)([a-zA-Z0-9_\-/\\\.]+\.[a-zA-Z0-9]+)"
                            view_match = re.search(view_pattern, text, re.IGNORECASE)
                            if view_match:
                                params["file"] = view_match.group(4) if len(view_match.groups()) >= 4 else view_match.group(3)
                                params["action"] = "view"
                                # Extraer rango de líneas si está presente
                                if view_match.group(2):
                                    if '-' in view_match.group(2):
                                        start, end = view_match.group(2).split('-')
                                        params["line_range"] = {"start": int(start), "end": int(end)}
                                    else:
                                        params["line_number"] = int(view_match.group(2))

                            # Añadir contenido (action=append)
                            append_pattern = r"\b(agrega|añade|anade|append|inserta|insert) (?:línea |line |texto |content |)?['\"]([^'\"]+)['\"] (?:a |al |al final de |to |into |en |)([a-zA-Z0-9_\-/\\\.]+\.[a-zA-Z0-9]+)"
                            append_match = re.search(append_pattern, text, re.IGNORECASE)
                            if append_match:
                                params["file"] = append_match.group(3)
                                params["new_content"] = append_match.group(2)
                                params["action"] = "append"

                            # Reemplazar línea específica
                            line_replace_pattern = r"\b(reemplaza|sustituye|replace) (?:la |la línea |line |linea |línea |ln )?(?:linea |línea |line |ln)?\s*(\d+) (?:por|with) ['\"]([^'\"]+)['\"] (?:en |in |de |)([a-zA-Z0-9_\-/\\\.]+\.[a-zA-Z0-9]+)"
                            line_replace_match = re.search(line_replace_pattern, text, re.IGNORECASE)
                            if line_replace_match:
                                params["file"] = line_replace_match.group(4)
                                params["line_number"] = int(line_replace_match.group(2))
                                params["new_content"] = line_replace_match.group(3)
                                params["action"] = "replace_line"

                        elif intent_type == IntentType.TERMINAL:
                            # Extraer el comando a ejecutar con mejor precisión
                            command_pattern = r'["\'`]([^"\'`]+)["\'`]'
                            command_match = re.search(command_pattern, text)
                            if command_match:
                                params["command"] = command_match.group(1)
                            else:
                                # Buscar cmdlets de PowerShell con mejor patrón
                                powershell_cmdlet_pattern = r'\b(get|set|new|remove|start|stop|restart|enable|disable|test|invoke|clear|select|sort|measure|convert|format|write|out|import|export|where|foreach|join|compare)-[a-zA-Z][a-zA-Z0-9\-]*(?:\s+[^\n]*)?'
                                cmdlet_match = re.search(powershell_cmdlet_pattern, text, re.IGNORECASE)
                                if cmdlet_match:
                                    params["command"] = cmdlet_match.group(0).strip()
                                    params["shell_type"] = "powershell"
                                else:
                                    # Buscar comandos PowerShell comunes con aliases
                                    common_ps_commands = [
                                        'get-process', 'get-service', 'get-childitem', 'set-location',
                                        'new-item', 'remove-item', 'copy-item', 'move-item',
                                        'get-content', 'set-content', 'clear-content'
                                    ]
                                    for cmd in common_ps_commands:
                                        if re.search(r'\b' + re.escape(cmd) + r'\b', text, re.IGNORECASE):
                                            # Extraer el comando completo con parámetros
                                            cmd_match = re.search(r'\b(' + re.escape(cmd) + r'(?:\s+[^\n]*))', text, re.IGNORECASE)
                                            if cmd_match:
                                                params["command"] = cmd_match.group(1).strip()
                                                params["shell_type"] = "powershell"
                                                break

                                    if "command" not in params:
                                        # Buscar comandos del sistema con mejor detección
                                        system_commands = {
                                            'cmd': ['dir', 'ipconfig', 'netstat', 'tasklist', 'taskkill', 'whoami', 'hostname', 'systeminfo'],
                                            'bash': ['ls', 'pwd', 'cd', 'cat', 'grep', 'find', 'chmod', 'chown', 'ps', 'top', 'df', 'du']
                                        }

                                        for shell, commands in system_commands.items():
                                            for cmd in commands:
                                                if re.search(r'\b' + re.escape(cmd) + r'\b', text, re.IGNORECASE):
                                                    # Extraer comando con parámetros
                                                    cmd_match = re.search(r'\b(' + re.escape(cmd) + r'(?:\s+[^\n]*))', text, re.IGNORECASE)
                                                    if cmd_match:
                                                        params["command"] = cmd_match.group(1).strip()
                                                        params["shell_type"] = shell
                                                        break
                                            if "command" in params:
                                                break

                                        if "command" not in params:
                                            # Último intento: buscar cualquier cosa después de las palabras clave
                                            cmd_pattern1 = r'(?:ejecuta|corre|usa|run|execute|launch)\s+(?:en |el |un |este |in |the |this |)(?:terminal|cmd|powershell|comando|command|shell)\s+(.+?)(?:$|\.)'
                                            cmd_match1 = re.search(cmd_pattern1, text, re.IGNORECASE)

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

                            # Peticiones naturales avanzadas
                            if "command" not in params:
                                natural_commands = {
                                    r"\b(lista|listar) (?:archivos|files|directorio|directory)\b": ("dir", "cmd"),
                                    r"\b(quien soy|quién soy|who am i)\b": ("whoami", "cmd"),
                                    r"\b(where am i|donde estoy|dónde estoy|ubicación|location)\b": ("pwd", "bash"),
                                    r"\b(contenido de|content of|muestra (?:el |la |)(?:contenido|content) (?:de |del |of ))([a-zA-Z0-9_\-/\\\.]+\.[a-zA-Z0-9]+)": (lambda m: f"type {m.group(2)}", "cmd"),
                                    r"\b(mostrar|show) (?:procesos|processes)\b": ("tasklist", "cmd"),
                                    r"\b(mostrar|show) (?:servicios|services)\b": ("net start", "cmd"),
                                    r"\b(reiniciar|restart) (?:sistema|system|equipo|computer)\b": ("shutdown /r /t 0", "cmd"),
                                    r"\b(apagar|shutdown) (?:sistema|system|equipo|computer)\b": ("shutdown /s /t 0", "cmd"),
                                    r"\b(net user|usuario de red|network user)\b": ("net user", "cmd"),
                                    r"\b(net localgroup|grupo local|local group)\b": ("net localgroup", "cmd"),
                                }

                                for pattern, (cmd, shell) in natural_commands.items():
                                    match = re.search(pattern, text, re.IGNORECASE)
                                    if match:
                                        if callable(cmd):
                                            params["command"] = cmd(match)
                                        else:
                                            params["command"] = cmd
                                        params["shell_type"] = shell
                                        break

                            # Normalizar el comando si se detectó
                            if "command" in params and "shell_type" in params:
                                params["command"] = cls._normalize_command(params["command"], params["shell_type"])

                            # Extraer flags y opciones del comando
                            if "command" in params:
                                flags = cls._extract_command_flags(params["command"])
                                if flags:
                                    params["flags"] = flags

                            # Detectar si el comando requiere elevación/admin
                            if "command" in params:
                                admin_keywords = ['runas', 'sudo', 'administrator', 'admin', 'elevated', 'as admin']
                                if any(keyword in params["command"].lower() for keyword in admin_keywords):
                                    params["requires_admin"] = True

                                # Detectar comandos potencialmente peligrosos
                                dangerous_patterns = [
                                    r'\b(rm|del|remove-item)\s+.*[-*?]',  # Wildcards peligrosos
                                    r'\b(shutdown|restart|halt)\s+.*[/\\]',  # Shutdown con flags
                                    r'\b(format|fdisk|diskpart)',  # Comandos de disco
                                    r'\b(net\s+user|net\s+localgroup)',  # Gestión de usuarios
                                    r'\b(reg\s+(delete|add))',  # Modificación de registro
                                ]

                                for pattern in dangerous_patterns:
                                    if re.search(pattern, params["command"], re.IGNORECASE):
                                        params["danger_level"] = "high"
                                        break
                                else:
                                    params["danger_level"] = "low"

                        matches_found.append((intent_type, confidence, params))

        # Resolver colisiones: si hubo match para EDIT y TERMINAL, y EDIT detectó un archivo, preferir EDIT
        if matches_found:
            # Buscar EDIT con file param
            edit_candidate = None
            terminal_candidate = None
            for itype, conf, parms in matches_found:
                if itype == IntentType.EDIT and parms.get('file'):
                    edit_candidate = (itype, conf, parms)
                if itype == IntentType.TERMINAL:
                    terminal_candidate = (itype, conf, parms)

            if edit_candidate:
                best_intent = Intent(edit_candidate[0], edit_candidate[1], edit_candidate[2])
            else:
                # Fallback: highest confidence
                best = max(matches_found, key=lambda x: x[1])
                best_intent = Intent(best[0], best[1], best[2])

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
