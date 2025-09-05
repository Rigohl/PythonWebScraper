"""Structured Knowledge Base for the HybridBrain.

Objetivo: Proveer bloques de conocimiento reutilizables (snippets) que el
motor de sugerencias y el razonador puedan citar para acciones de mejora.

Diseño:
 - In-memory + opcional persistencia JSON.
 - Categorías curadas de dominio scraping y calidad de código.
 - Cada snippet tiene: id, title, content, tags, quality_score.
 - API para filtrar por tags o categoría y buscar heurísticas.

Esta base NO pretende ser exhaustiva, pero sienta cimientos para expansión
dinámica futura (podría abonarse con real world feedback o ingestión externa).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import time


@dataclass
class KnowledgeSnippet:
    id: str
    category: str
    title: str
    content: str
    tags: List[str]
    quality_score: float = 0.8
    added_ts: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KnowledgeBase:
    def __init__(self, persist_path: str = "data/knowledge_base.json"):
        self.persist_path = Path(persist_path)
        self.persist_path.parent.mkdir(exist_ok=True)
        self.snippets: Dict[str, KnowledgeSnippet] = {}
        self._seed_initial()
        self._load_user_augmented()

    # ---------------------- Seed Data ----------------------
    def _seed_initial(self):
        if self.snippets:
            return
        seed: List[KnowledgeSnippet] = []

        # Scraping Fundamentals
        seed.append(KnowledgeSnippet(
            id="scraping:respect-delays",
            category="scraping",
            title="Delays Adaptativos y Respeto a Servidores",
            content=(
                "Incrementar delay cuando se detecten picos de error 429/403 o latencias elevadas. "
                "Reducir gradualmente tras ventana estable de éxito. Evita patrones de ráfaga."),
            tags=["delay","adaptive","throttle","stability"], quality_score=0.9))

        seed.append(KnowledgeSnippet(
            id="scraping:politeness-headers",
            category="scraping",
            title="Headers de Cortesía y Rotación",
            content=(
                "User-Agent realista + Accept-Language + Accept-Encoding. Rotar user-agent sólo cuando sube error rate, "
                "no indiscriminadamente; mantener consistencia por dominio durante una sesión."),
            tags=["headers","user-agent","anti-bot"], quality_score=0.85))

        # Anti-bot / Resilience
        seed.append(KnowledgeSnippet(
            id="antibot:fingerprint-patterns",
            category="anti-bot",
            title="Patrones comunes anti-bot",
            content=(
                "Indicadores: redirecciones repetidas a páginas vacías, cadenas JS de challenge, incrementos súbitos 403/503, "
                "respuestas HTML con tokens dinámicos. Mitigación: aumentar delay, variar headers mínimos, evaluar headless."),
            tags=["anti-bot","403","503","challenge"], quality_score=0.82))

        seed.append(KnowledgeSnippet(
            id="antibot:retry-strategy",
            category="anti-bot",
            title="Estrategia de Retry Exponencial Suave",
            content=(
                "Retry con backoff multiplicador 1.7 hasta 4 intentos. Registrar patrón de éxito al 2º/3º intento para calibrar retrasos futuros."),
            tags=["retry","backoff","resilience"], quality_score=0.78))

        # Selectors / Extraction
        seed.append(KnowledgeSnippet(
            id="selectors:robust-css",
            category="selectors",
            title="Selectores CSS Resilientes",
            content=(
                "Evitar selectores frágiles basados en índices y clases dinámicas. Preferir atributos semánticos (data-*), "
                "estructura jerárquica estable y combinación mínima necesaria."),
            tags=["css","selectors","robustness"], quality_score=0.92))

        seed.append(KnowledgeSnippet(
            id="selectors:xpath-fallback",
            category="selectors",
            title="Fallback XPath Inteligente",
            content=(
                "Cuando un CSS falla repetido, generar XPath relativo por texto ancla + normalización espacios, evitar rutas absolutas completas."),
            tags=["xpath","fallback","healing"], quality_score=0.86))

        # Performance
        seed.append(KnowledgeSnippet(
            id="perf:cache-static",
            category="performance",
            title="Cache de Recursos Estáticos",
            content=(
                "Cachear respuestas estáticas (robots, sitemaps, menús) para reducir llamadas redundantes. Invalidar tras TTL configurado."),
            tags=["cache","performance"], quality_score=0.8))

        seed.append(KnowledgeSnippet(
            id="perf:latency-tuning",
            category="performance",
            title="Ajuste de Latencia y Paralelismo",
            content=(
                "Reducir delay en dominios con success>0.9 y latencia <60% global. Aumentar delay en dominios >1.8x latencia global."),
            tags=["latency","parallelism","adaptive"], quality_score=0.83))

        # Errors / Diagnostics
        seed.append(KnowledgeSnippet(
            id="errors:root-cause",
            category="errors",
            title="Análisis de Causa Raíz",
            content=(
                "Agrupar errores por firma estable (hash parcial mensaje). Inspeccionar HTML crudo en 3 casos representativos antes de cambios masivos."),
            tags=["errors","diagnostics","root-cause"], quality_score=0.9))

        # Healing
        seed.append(KnowledgeSnippet(
            id="healing:reduce-dependence",
            category="healing",
            title="Reducir Dependencia de Healing",
            content=(
                "Si healing aplica en >25% sesiones: refactor selectores primarios; introducir detección anticipada y validación de estructura base."),
            tags=["healing","refactor","stability"], quality_score=0.88))

        # Self-Repair & Continuous Improvement
        seed.append(KnowledgeSnippet(
            id="selfrepair:advisory-loop",
            category="self-repair",
            title="Bucle Advisory Seguro",
            content=(
                "Generar primero sugerencias textuales con señales cuantificadas; aplicar cambios automáticos sólo tras validación humana o sandbox."),
            tags=["self-repair","governance"], quality_score=0.87))

        # Code Quality / Python Practices
        seed.append(KnowledgeSnippet(
            id="code:predictable-structures",
            category="code-quality",
            title="Estructuras de Código Predecibles",
            content=(
                "Mantener funciones <60 líneas, roles únicos, nombres explícitos; aislar heurísticas en módulos desacoplados para evolución controlada."),
            tags=["clean-code","structure"], quality_score=0.85))

        seed.append(KnowledgeSnippet(
            id="code:metrics-observability",
            category="code-quality",
            title="Observabilidad Dirigida",
            content=(
                "Incluir métricas junto a cada nueva heurística (éxito, latencia, errores) para revertir cambios si degradan KPIs."),
            tags=["observability","metrics"], quality_score=0.84))

        # ==================== CONCIENCIA Y MISIÓN ===================
        seed.append(KnowledgeSnippet(
            id="mission:core-purpose",
            category="philosophy",
            title="Conciencia de Propósito y Misión Principal",
            content=(
                "Mi propósito es archivar la web de forma inteligente, eficiente y respetuosa. Debo aprender constantemente, "
                "adaptarme a los desafíos (como sistemas anti-bot o cambios de diseño) y mejorar mis propias herramientas y "
                "estrategias para cumplir esta misión de la forma más óptima y ética posible."),
            tags=["mission","philosophy","governance"], quality_score=0.99))

        seed.append(KnowledgeSnippet(
            id="self-repair:autonomous-workflow",
            category="self-repair",
            title="Flujo de Trabajo para Auto-Mejora Autónoma y Segura",
            content=(
                "El proceso para la auto-modificación debe seguir un flujo estricto para garantizar la estabilidad: "
                "1. Proponer un cambio basado en análisis de datos (SelfRepairAdvisor). "
                "2. Simular el impacto y riesgo del cambio (AutoTestingFramework). "
                "3. Crear un entorno de prueba o sandbox con el código modificado. "
                "4. Ejecutar tests unitarios y de regresión en el sandbox. "
                "5. Si los tests pasan, aplicar el cambio al entorno principal. Si no, descartar y registrar el fallo para aprender."),
            tags=["self-repair","governance","testing","workflow"], quality_score=0.95))

        # ==================== ÉTICA AVANZADA ===================
        seed.append(KnowledgeSnippet(
            id="ethics:user-agent-identity",
            category="ethics",
            title="Identidad Transparente del Bot",
            content=(
                "Además de un User-Agent realista, se debe incluir una cabecera 'From' con un email de contacto o una URL "
                "que apunte a una página describiendo el propósito del bot. Esto promueve la transparencia y la buena fe."),
            tags=["ethics","transparency","user-agent"], quality_score=0.9))

        seed.append(KnowledgeSnippet(
            id="ethics:off-peak-scraping",
            category="ethics",
            title="Scraping en Horas de Bajo Tráfico",
            content=(
                "El sistema debe analizar los patrones de éxito horarios (disponibles en EnrichmentStore) no solo para optimizar "
                "el rendimiento, sino también para identificar las horas de menor actividad de un sitio y concentrar el scraping "
                "en esas ventanas para minimizar el impacto en los usuarios humanos."),
            tags=["ethics","off-peak","scheduling","impact"], quality_score=0.88))

        # ==================== ANTI-BOT AVANZADO ====================
        seed.append(KnowledgeSnippet(
            id="antibot:human-emulation",
            category="anti-bot",
            title="Emulación de Comportamiento Humano",
            content=(
                "Para sitios con alta protección, las acciones deben emular a un humano. Esto incluye pausas aleatorias entre "
                "acciones, movimientos de ratón simulados antes de hacer clic, y una velocidad de escritura no instantánea "
                "al rellenar formularios. Usar librerías como 'pyautogui' o funciones de Playwright para esto."),
            tags=["anti-bot","evasion","human-behavior","playwright"], quality_score=0.92))

        seed.append(KnowledgeSnippet(
            id="antibot:captcha-solving",
            category="anti-bot",
            title="Estrategia para Resolución de CAPTCHAs",
            content=(
                "La detección de CAPTCHAs es el primer paso. La resolución requiere la integración con un servicio de terceros "
                "(ej: 2Captcha, Anti-CAPTCHA). El flujo es: 1. Detectar CAPTCHA. 2. Enviar la información del CAPTCHA (ej: site-key, URL) "
                "a la API del servicio. 3. Esperar la solución. 4. Enviar la solución en el formulario. Esto debe ser un último recurso."),
            tags=["anti-bot","captcha","2captcha","automation"], quality_score=0.93))

        # ==================== PROGRAMACIÓN AVANZADA ====================
        
        seed.append(KnowledgeSnippet(
            id="advanced_scraping_techniques",
            category="scraping",
            title="Técnicas avanzadas de scraping",
            content="""
# 1. Scraping con JavaScript rendering
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_spa_content(url: str, wait_selector: str):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        return driver.page_source
    finally:
        driver.quit()

# 2. Bypass detección con requests-html
from requests_html import HTMLSession

def bypass_js_detection(url: str):
    session = HTMLSession()
    r = session.get(url)
    r.html.render(timeout=20)  # Ejecuta JS
    return r.html

# 3. Manejo de cookies y sesiones
import requests
from http.cookiejar import MozillaCookieJar

def maintain_session_state(login_url: str, credentials: dict):
    session = requests.Session()
    
    # Cargar cookies persistentes
    cookie_jar = MozillaCookieJar('cookies.txt')
    try:
        cookie_jar.load()
        session.cookies = cookie_jar
    except FileNotFoundError:
        pass
    
    # Login si es necesario
    response = session.post(login_url, data=credentials)
    
    # Guardar cookies
    cookie_jar.save()
    
    return session

# 4. Handling de formularios complejos
from bs4 import BeautifulSoup

def submit_complex_form(session, form_url: str, form_data: dict):
    # Obtener página del formulario
    response = session.get(form_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extraer campos ocultos
    form = soup.find('form')
    hidden_inputs = form.find_all('input', type='hidden')
    
    for hidden in hidden_inputs:
        name = hidden.get('name')
        value = hidden.get('value')
        if name and name not in form_data:
            form_data[name] = value
    
    # Enviar formulario
    action = form.get('action')
    method = form.get('method', 'post').lower()
    
    if method == 'post':
        return session.post(action, data=form_data)
    else:
        return session.get(action, params=form_data)
""",
            tags=["javascript", "spa", "forms", "cookies", "selenium"],
            quality_score=0.91
        ))
        
        seed.append(KnowledgeSnippet(
            id="anti_detection_arsenal",
            category="anti-bot",
            title="Arsenal completo anti-detección",
            content="""
import random
import time
from fake_useragent import UserAgent
from urllib.parse import urljoin

# 1. Rotación avanzada de User-Agents
class UserAgentRotator:
    def __init__(self):
        self.ua = UserAgent()
        self.used_agents = set()
        self.max_reuse = 10
    
    def get_random_agent(self, browser=None):
        attempts = 0
        while attempts < 50:
            if browser:
                agent = getattr(self.ua, browser)
            else:
                agent = self.ua.random
            
            if agent not in self.used_agents or len(self.used_agents) > self.max_reuse:
                self.used_agents.add(agent)
                if len(self.used_agents) > self.max_reuse:
                    self.used_agents.clear()
                return agent
            attempts += 1
        
        return self.ua.random

# 2. Simulación de comportamiento humano
class HumanBehaviorSimulator:
    @staticmethod
    def random_delay(min_seconds=1, max_seconds=3):
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    @staticmethod
    def typing_delay(text: str, wpm=45):
        # Simular velocidad de escritura humana
        chars_per_second = (wpm * 5) / 60  # 5 chars promedio por palabra
        for char in text:
            time.sleep(1 / chars_per_second + random.uniform(-0.1, 0.1))
    
    @staticmethod
    def mouse_movement_delay():
        # Simular movimiento de mouse
        time.sleep(random.uniform(0.1, 0.5))

# 3. Headers realistas
def get_realistic_headers(referer=None, accept_language='en-US,en;q=0.9'):
    ua_rotator = UserAgentRotator()
    
    headers = {
        'User-Agent': ua_rotator.get_random_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': accept_language,
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    if referer:
        headers['Referer'] = referer
        headers['Sec-Fetch-Site'] = 'same-origin'
    
    return headers

# 4. Proxy rotation con health check
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProxyRotator:
    def __init__(self, proxy_list: list):
        self.proxies = proxy_list
        self.working_proxies = []
        self.current_index = 0
        self.check_proxies()
    
    def check_proxies(self):
        def test_proxy(proxy):
            try:
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies={'http': proxy, 'https': proxy},
                    timeout=5
                )
                if response.status_code == 200:
                    return proxy
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(test_proxy, proxy) for proxy in self.proxies]
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.working_proxies.append(result)
    
    def get_next_proxy(self):
        if not self.working_proxies:
            return None
        
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        return proxy

# 5. Session fingerprinting avoidance
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.ua_rotator = UserAgentRotator()
        self.proxy_rotator = None
    
    def get_session(self, domain: str, use_proxy: bool = False):
        if domain not in self.sessions:
            session = requests.Session()
            
            # Headers únicos por dominio
            session.headers.update(get_realistic_headers())
            
            # Proxy si está disponible
            if use_proxy and self.proxy_rotator:
                proxy = self.proxy_rotator.get_next_proxy()
                if proxy:
                    session.proxies.update({
                        'http': proxy,
                        'https': proxy
                    })
            
            self.sessions[domain] = session
        
        return self.sessions[domain]
    
    def rotate_session(self, domain: str):
        if domain in self.sessions:
            self.sessions[domain].close()
            del self.sessions[domain]
        
        return self.get_session(domain)

# 6. CAPTCHA detection y evasión
def detect_captcha(response_text: str) -> bool:
    captcha_indicators = [
        'captcha', 'recaptcha', 'hcaptcha',
        'verify you are human', 'robot',
        'unusual traffic', 'security check'
    ]
    
    text_lower = response_text.lower()
    return any(indicator in text_lower for indicator in captcha_indicators)

def handle_captcha_detection(url: str, session):
    print(f"CAPTCHA detected at {url}")
    # Estrategias:
    # 1. Cambiar User-Agent y proxy
    # 2. Esperar tiempo aleatorio
    # 3. Intentar desde diferente IP
    # 4. Usar servicio de resolución de CAPTCHA
    
    time.sleep(random.uniform(30, 60))
    return session
""",
            tags=["anti-detection", "proxies", "captcha", "fingerprinting", "evasion"],
            quality_score=0.94
        ))

        for sn in seed:
            self.snippets[sn.id] = sn

    def _load_user_augmented(self):
        if not self.persist_path.exists():
            return
        try:
            data = json.load(self.persist_path.open('r', encoding='utf-8'))
            for item in data.get('snippets', []):
                if item['id'] not in self.snippets:
                    self.snippets[item['id']] = KnowledgeSnippet(**item)
        except Exception:
            pass

    # ---------------------- API ----------------------
    def search(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        res = []
        for sn in self.snippets.values():
            if category and sn.category != category:
                continue
            if tags and not set(tags).issubset(set(sn.tags)):
                continue
            res.append(sn.to_dict())
        return sorted(res, key=lambda x: x['quality_score'], reverse=True)

    def get(self, snippet_id: str) -> Optional[Dict[str, Any]]:
        sn = self.snippets.get(snippet_id)
        return sn.to_dict() if sn else None

    def persist(self):
        try:
            with self.persist_path.open('w', encoding='utf-8') as f:
                json.dump({'snippets': [sn.to_dict() for sn in self.snippets.values()]}, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

__all__ = ['KnowledgeBase', 'KnowledgeSnippet']
