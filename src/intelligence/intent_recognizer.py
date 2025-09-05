# src/intelligence/intent_recognizer.py

import re
import shlex
from enum import Enum

# src/intelligence/intent_recognizer.py
from typing import Any, Dict, Optional


class IntentType(Enum):
    UNKNOWN = "unknown"
    SEARCH = "search"
    CRAWL = "crawl"
    KNOWLEDGE = "knowledge"
    SNAPSHOT = "snapshot"
    STATUS = "status"
    EDIT = "edit"
    TERMINAL = "terminal"


class Intent:
    def __init__(
        self,
        intent_type: IntentType = IntentType.UNKNOWN,
        confidence: float = 0.0,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.type = intent_type
        self.confidence = confidence
        self.parameters = parameters or {}

    def __repr__(self) -> str:
        return f"Intent(type={self.type}, confidence={self.confidence:.2f}, parameters={self.parameters})"


class IntentRecognizer:
    """Lightweight, robust recognizer focused on EDIT and TERMINAL patterns for tests."""

    INTENT_PATTERNS = {
        IntentType.EDIT: [
            r"\b(?:edita|editar|edite|modifica|modificar|modificá|cambia|cambiar|cambiá|actualiza|actualizar|corrige|corregir|corregí|reemplaza|reemplazar|sustituye|sustituir)\b",
            r"\b(?:edit|edits|modify|changes|change|update|fix|update)\b",
            r"\b(?:cambia|reemplaza|sustituye|replace|reemplazar)\b",
            r"\b(?:configuration|configuración|configuration file|config file)\b",
        ],
        IntentType.TERMINAL: [
            r"\b(?:ejecuta|corre|lanza|run|execute|use|usa|utiliza)\b",
            r"\b(?:terminal|cmd|powershell|shell|comando|command)\b",
            r"\b(get-|set-|new-|remove-|start-|stop-|restart-)",
        ],
    }

    @classmethod
    def _is_valid_file_path(cls, path: str) -> bool:
        if not path:
            return False
        path = path.strip("\"'` ")
        if len(path) > 260:
            return False
        # prevent traversal
        if ".." in path.replace("\\", "/").split("/"):
            return False
        # simple filename with extension
        if re.match(r"^[\w\-.]+\.[A-Za-z0-9]+$", path):
            return True
        # relative or nested path
        if re.match(r"^[\w\-./\\]+\.[A-Za-z0-9]+$", path):
            return True
        return False

    @classmethod
    def _normalize_command(cls, command: str, shell_type: str) -> str:
        if not command:
            return ""
        try:
            # Use shlex to keep quoted arguments intact
            parts = shlex.split(command, posix=(shell_type != "powershell"))
            if not parts:
                return command.strip()
            # conservative: only normalize the verb (first token)
            verb = parts[0]
            verb_map = {
                "ls": "ls",
                "dir": "dir",
                "python": "python",
            }
            parts[0] = verb_map.get(verb, verb)
            return " ".join(parts)
        except Exception:
            return command.strip()

    @classmethod
    def _extract_command_flags(cls, command: str) -> Dict[str, Any]:
        flags = {}
        if not command:
            return flags
        # collect simple flags like -a, --all and key=value
        for m in re.finditer(
            r"(?:--(?P<long>[\w-]+)|-(?P<short>\w))(?:[= ](?P<val>[^\s]+))?", command
        ):
            key = m.group("long") or m.group("short")
            val = m.group("val") or True
            flags[key] = val
        return flags

    @classmethod
    def recognize(cls, text: str) -> Intent:
        text = (text or "").strip()
        if not text:
            return Intent()

        matches_found = []

        # try to match EDIT and extract file/old/new
        for intent_type, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence = 0.7
                    params: Dict[str, Any] = {}

                    if intent_type == IntentType.EDIT:
                        # filename explicit: 'en <file>' or 'en el archivo <file>'
                        file_match = re.search(
                            r"\b(?:en|en el archivo|in|in the file)\s+([\w\-./\\]+\.[A-Za-z0-9]+)\b",
                            text,
                            re.IGNORECASE,
                        )
                        if file_match:
                            candidate = file_match.group(1)
                            if cls._is_valid_file_path(candidate):
                                params["file"] = candidate

                        # also accept patterns like 'edita el archivo config.json' or 'edit the file config.json'
                        if "file" not in params:
                            file_match2 = re.search(
                                r"\b(?:archivo|file|fichero)\s+([\w\-./\\]+\.[A-Za-z0-9]+)\b",
                                text,
                                re.IGNORECASE,
                            )
                            if file_match2:
                                candidate2 = file_match2.group(1)
                                if cls._is_valid_file_path(candidate2):
                                    params["file"] = candidate2

                        # replace pattern: 'cambia "old" por "new" en file'
                        replace_match = re.search(
                            r"(?:cambia|reemplaza|sustituye|change|replace)\s+['\"`]?(.+?)['\"`]?\s+(?:por|a|con|to|with)\s+['\"`]?(.+?)['\"`]?(?:\s+en\s+([\w\-./\\]+\.[A-Za-z0-9]+))?",
                            text,
                            re.IGNORECASE,
                        )
                        if replace_match:
                            params["action"] = "replace"
                            params["old_content"] = replace_match.group(1)
                            params["new_content"] = replace_match.group(2)
                            if replace_match.group(3) and cls._is_valid_file_path(
                                replace_match.group(3)
                            ):
                                params["file"] = replace_match.group(3)

                    if intent_type == IntentType.TERMINAL:
                        # quoted command
                        cmd_match = re.search(r'["\'`]([^"\'`]+)["\'`]', text)
                        if cmd_match:
                            params["command"] = cmd_match.group(1)

                    matches_found.append((intent_type, confidence, params))

        # prefer EDIT with file
        for itype, conf, parms in matches_found:
            if itype == IntentType.EDIT and parms.get("file"):
                return Intent(itype, conf, parms)

        if matches_found:
            best = max(matches_found, key=lambda x: x[1])
            return Intent(best[0], best[1], best[2])

        return Intent()


if __name__ == "__main__":
    examples = [
        "Cambia 'timeout: 30' por 'timeout: 60' en config.json",
        "Edita el archivo config.json",
        "Ejecuta 'dir' en el terminal",
        "Run 'ls -la' in terminal",
    ]

    for msg in examples:
        print(msg, "->", IntentRecognizer.recognize(msg))
