import random
from typing import Dict, Any

from src.user_agent_manager import UserAgentManager

# Lista de viewports comunes para simular diferentes resoluciones de pantalla.
# Fuente: https://www.w3schools.com/browsers/browsers_display.asp (aproximado)
COMMON_VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]

class FingerprintManager:
    """
    Gestiona y genera perfiles de huella digital (fingerprints) de navegador
    para hacer que el scraper parezca más humano y menos detectable.
    """

    def __init__(self, user_agent_manager: UserAgentManager, viewports: list = COMMON_VIEWPORTS):
        """
        Inicializa el gestor con un UserAgentManager y una lista de viewports.
        """
        if not user_agent_manager:
            raise ValueError("Se debe proporcionar un UserAgentManager.")
        if not viewports:
            raise ValueError("La lista de viewports no puede estar vacía.")

        self.user_agent_manager = user_agent_manager
        self.viewports = viewports

    def _get_platform_from_ua(self, user_agent: str) -> str:
        """Determina el valor de `navigator.platform` basado en el User-Agent."""
        ua_lower = user_agent.lower()
        if "windows" in ua_lower:
            return "Win32"
        if "macintosh" in ua_lower or "mac os" in ua_lower:
            return "MacIntel"
        if "linux" in ua_lower:
            return "Linux x86_64"
        if "iphone" in ua_lower or "ipad" in ua_lower:
            return "iPhone"
        if "android" in ua_lower:
            return "Linux armv8l" # Común en Android
        return "Win32" # Un valor por defecto razonable

    def get_fingerprint(self) -> Dict[str, Any]:
        """
        Genera un perfil de huella digital completo y consistente.
        """
        user_agent = self.user_agent_manager.get_user_agent()
        viewport = random.choice(self.viewports)
        platform = self._get_platform_from_ua(user_agent)

        js_overrides = {
            "navigator.webdriver": False,
            "navigator.languages": "['en-US', 'en']", # Como string para inyección directa en JS
            "navigator.platform": f"'{platform}'",
            "navigator.plugins.length": 0,
            "screen.colorDepth": 24,
            "navigator.hardwareConcurrency": random.choice([4, 8, 16]),
            "navigator.deviceMemory": random.choice([4, 8]),
        }

        return {
            "user_agent": user_agent,
            "viewport": viewport,
            "js_overrides": js_overrides
        }
