import re
from typing import Any, Dict

# Blocked commands for security
BLOCKED_COMMAND_PATTERNS = [
    r"remove-item.*-recurse.*-force",
    r"set-executionpolicy.*bypass",
    r"invoke-webrequest.*\|.*invoke-expression",
    r"curl.*http.*\|.*bash",
    r"del\s+.*",
    r"rmdir\s+.*",
    r"rm\s+.*",
]

ALIAS_MAP = {
    "ls": "Get-ChildItem",
    "ps": "Get-Process",
    "cat": "Get-Content",
    "pwd": "Get-Location",
}

CMDLET_REGEX = re.compile(
    r"^(get|set|new|remove|start|stop|restart|enable|disable|test|invoke|clear|select|sort|measure|convert|format|write|out|import|export|where|foreach|join|compare)-[A-Za-z][A-Za-z0-9-]+(?:\s.*)?$",
    re.IGNORECASE,
)
SAFE_VERBS = re.compile(
    r"^(get|select|measure|format|where|foreach|join|compare|test|import|export)\b",
    re.IGNORECASE,
)
DESTRUCTIVE_VERBS = re.compile(
    r"^(remove|set|restart|stop|write|out-file|invoke-webrequest|invoke-expression|set-executionpolicy|new-item|remove-item|del|rmdir|rm)\b",
    re.IGNORECASE,
)
PIPE_DANGER = re.compile(
    r"[|]\s*(Invoke-Expression|iex|bash|-c)|[>]{1,2}\s*\S", re.IGNORECASE
)

# Edit actions
EDIT_ACTIONS = {
    "replace": [
        "reemplaza",
        "replace",
        "cambia",
        "modifica",
        "sustituye",
        "change",
        "modify",
        "update",
    ],
    "append": [
        "agrega",
        "añade",
        "anade",
        "append",
        "inserta",
        "insert",
        "add",
        "agregar",
    ],
    "remove": ["elimina", "borra", "borrar", "remove", "delete", "quitar", "sacar"],
    "show": [
        "muestra",
        "enséñame",
        "ensename",
        "abre",
        "visualiza",
        "ver",
        "mostrar",
        "show",
        "open",
        "display",
        "view",
        "read",
        "cat",
    ],
}

PATH_REGEX = re.compile(
    r"([A-Za-z]:\\|/)?([\w\-. ]+[/\\])*[\w\-. ]+\.[A-Za-z0-9]+(\.[A-Za-z0-9]+)*"
)


def extract_terminal_intent(text: str) -> Dict[str, Any]:
    """Extracts terminal intent details from text."""
    result = {
        "cmdlet": None,
        "args": None,
        "is_destructive": False,
        "danger_tokens": [],
        "confidence": 0.0,
        "reason": [],
    }
    text = text.strip()
    cmdlet_match = CMDLET_REGEX.match(text)
    if cmdlet_match:
        result["cmdlet"] = cmdlet_match.group(0)
        verb = cmdlet_match.group(1)
        result["is_destructive"] = bool(DESTRUCTIVE_VERBS.match(verb))
        result["confidence"] = 0.9
        result["reason"].append("cmdlet detected")
        if PIPE_DANGER.search(text):
            result["danger_tokens"].append("pipe/redirection detected")
            result["is_destructive"] = True
    else:
        alias = ALIAS_MAP.get(text.split()[0].lower())
        if alias:
            result["cmdlet"] = alias
            result["confidence"] = 0.7
            result["reason"].append("alias normalized")
        if DESTRUCTIVE_VERBS.match(text.split()[0]):
            result["is_destructive"] = True
            result["confidence"] = 0.8
            result["reason"].append("destructive verb detected")
        if PIPE_DANGER.search(text):
            result["danger_tokens"].append("pipe/redirection detected")
            result["is_destructive"] = True
    # Blocked command patterns
    for pat in BLOCKED_COMMAND_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            result["is_destructive"] = True
            result["danger_tokens"].append("blocked pattern")
            result["confidence"] = 1.0
            result["reason"].append("blocked command pattern")
    return result


def extract_edit_intent(text: str) -> Dict[str, Any]:
    """Extracts edit intent details from text."""
    result = {
        "action": "show",
        "path": None,
        "from": None,
        "to": None,
        "content": None,
        "confidence": 0.0,
        "out_of_scope": False,
        "reason": [],
    }
    text = text.strip()
    # Detect action
    for action, keywords in EDIT_ACTIONS.items():
        for kw in keywords:
            if kw in text.lower():
                result["action"] = action
                result["reason"].append(f"action:{action}")
                break
    # Extract path
    path_match = PATH_REGEX.search(text)
    if path_match:
        result["path"] = path_match.group(0)
        result["confidence"] += 0.5
        result["reason"].append("path detected")
    # Extract replace/append/remove content
    replace_match = re.search(
        r'(?:reemplaza|replace|cambia|modifica|sustituye|change|modify|update)\s*["\'`](.+?)["\'`]\s*(?:por|a|con|to|with|by)\s*["\'`](.+?)["\'`]',
        text,
        re.IGNORECASE,
    )
    if replace_match:
        result["from"] = replace_match.group(1)
        result["to"] = replace_match.group(2)
        result["confidence"] += 0.3
        result["reason"].append("replace detected")
    append_match = re.search(
        r'(?:agrega|añade|anade|append|inserta|insert|add|agregar)\s*["\'`](.+?)["\'`]',
        text,
        re.IGNORECASE,
    )
    if append_match:
        result["content"] = append_match.group(1)
        result["confidence"] += 0.2
        result["reason"].append("append detected")
    remove_match = re.search(
        r'(?:elimina|borra|borrar|remove|delete|quitar|sacar)\s*["\'`](.+?)["\'`]',
        text,
        re.IGNORECASE,
    )
    if remove_match:
        result["content"] = remove_match.group(1)
        result["confidence"] += 0.2
        result["reason"].append("remove detected")
    return result


def is_blocked(command_str: str) -> bool:
    """Checks if a command matches any blocked pattern."""
    for pat in BLOCKED_COMMAND_PATTERNS:
        if re.search(pat, command_str, re.IGNORECASE):
            return True
    return False
