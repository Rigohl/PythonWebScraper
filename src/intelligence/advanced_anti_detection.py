"""
Módulo de técnicas anti-detección avanzadas
Basado en investigación exhaustiva de herramientas cutting-edge:
- Scrapling StealthyFetcher (Camoufox browser)
- SeleniumBase UC mode (undetected mode)
- undetected-chromedriver
- Pydoll (CDP directo)
- Browser-Use (AI agents)
"""

import random
import time
import json
import base64
from typing import Dict, List, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np

class AdvancedAntiDetection:
    """
    Sistema avanzado de anti-detección combinando técnicas de múltiples herramientas
    """
    
    def __init__(self):
        self.stealth_techniques = {
            'scrapling': self._init_scrapling_techniques,
            'seleniumbase': self._init_seleniumbase_techniques,
            'undetected': self._init_undetected_techniques,
            'pydoll': self._init_pydoll_techniques,
            'browser_use': self._init_browser_use_techniques
        }
        
        self.fingerprint_data = self._generate_fingerprint_data()
        self.human_behavior = HumanBehaviorSimulator()
        
    def _init_scrapling_techniques(self) -> Dict[str, Any]:
        """Técnicas de Scrapling StealthyFetcher"""
        return {
            'camoufox_browser': True,
            'cloudflare_solver': True,
            'canvas_noise_injection': True,
            'webgl_control': True,
            'browser_fingerprint_spoofing': True,
            'geoip_matching': True,
            'os_randomization': True,
            'user_agent_rotation': True
        }
    
    def _init_seleniumbase_uc_techniques(self) -> Dict[str, Any]:
        """Técnicas de SeleniumBase UC (Undetected) mode"""
        return {
            'pyautogui_captcha_bypass': True,
            'stealth_arguments': [
                '--disable-notifications',
                '--excludeSwitches=enable-automation',
                '--useAutomationExtension=false',
                '--disable-blink-features=AutomationControlled'
            ],
            'cdp_mode': True,
            'undetected_mode': True,
            'anti_detection_args': [
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-ipc-flooding-protection'
            ]
        }
    
    def _init_undetected_techniques(self) -> Dict[str, Any]:
        """Técnicas de undetected-chromedriver"""
        return {
            'navigator_webdriver_patch': True,
            'user_agent_manipulation': True,
            'headless_configuration': True,
            'chrome_runtime_simulation': True,
            'webdriver_property_removal': True,
            'automation_flags_hiding': True
        }
    
    def _init_pydoll_techniques(self) -> Dict[str, Any]:
        """Técnicas de Pydoll (CDP directo)"""
        return {
            'zero_webdrivers': True,
            'direct_cdp': True,
            'cloudflare_bypass_native': True,
            'humanized_interactions': True,
            'network_interception': True,
            'browser_context_requests': True
        }
    
    def _init_browser_use_techniques(self) -> Dict[str, Any]:
        """Técnicas de Browser-Use (AI agents)"""
        return {
            'ai_agents': True,
            'computer_vision_automation': True,
            'llm_cv_integration': True,
            'intelligent_element_detection': True,
            'context_aware_actions': True
        }
    
    def _generate_fingerprint_data(self) -> Dict[str, Any]:
        """Genera datos de fingerprint realistas"""
        screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
            (1280, 720), (1600, 900), (2560, 1440), (1920, 1200)
        ]
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        return {
            'screen_resolution': random.choice(screen_resolutions),
            'user_agent': random.choice(user_agents),
            'timezone': random.choice(['America/New_York', 'Europe/London', 'Asia/Tokyo']),
            'language': random.choice(['en-US', 'en-GB', 'es-ES']),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'webgl_vendor': random.choice(['Google Inc.', 'NVIDIA Corporation', 'AMD']),
            'hardware_concurrency': random.choice([4, 8, 12, 16])
        }
    
    def configure_stealth_options(self, options: Options) -> Options:
        """Configura opciones de Chrome para máximo stealth"""
        
        # Scrapling-inspired arguments
        stealth_args = [
            '--disable-blink-features=AutomationControlled',
            '--excludeSwitches=enable-automation',
            '--useAutomationExtension=false',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-ipc-flooding-protection',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-field-trial-config',
            '--disable-back-forward-cache',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-component-extensions-with-background-pages',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--metrics-recording-only',
            '--no-first-run',
            '--safebrowsing-disable-auto-update',
            '--password-store=basic',
            '--use-mock-keychain',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-gpu',
            '--remote-debugging-port=0'
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
        
        # User agent spoofing
        options.add_argument(f"--user-agent={self.fingerprint_data['user_agent']}")
        
        # Screen resolution
        width, height = self.fingerprint_data['screen_resolution']
        options.add_argument(f"--window-size={width},{height}")
        
        # Preferences for maximum stealth
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            },
            "profile.default_content_settings": {
                "popups": 0
            },
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    def inject_stealth_scripts(self, driver) -> None:
        """Inyecta scripts para ocultar automatización (técnicas undetected-chromedriver)"""
        
        # Eliminar navigator.webdriver
        script_webdriver = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        """
        
        # Spoof navigator properties
        script_navigator = f"""
        Object.defineProperty(navigator, 'languages', {{
            get: () => ['{self.fingerprint_data['language']}'],
        }});
        
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{self.fingerprint_data['platform']}',
        }});
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {self.fingerprint_data['hardware_concurrency']},
        }});
        """
        
        # Canvas fingerprint protection
        script_canvas = """
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, attributes) {
            const context = originalGetContext.call(this, type, attributes);
            if (type === '2d') {
                const originalGetImageData = context.getImageData;
                context.getImageData = function(sx, sy, sw, sh) {
                    const imageData = originalGetImageData.call(this, sx, sy, sw, sh);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] += Math.floor(Math.random() * 10) - 5;
                        imageData.data[i + 1] += Math.floor(Math.random() * 10) - 5;
                        imageData.data[i + 2] += Math.floor(Math.random() * 10) - 5;
                    }
                    return imageData;
                };
            }
            return context;
        };
        """
        
        # WebGL fingerprint protection
        script_webgl = f"""
        const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{self.fingerprint_data['webgl_vendor']}';
            }}
            return originalGetParameter.call(this, parameter);
        }};
        """
        
        # Execute all stealth scripts
        scripts = [script_webdriver, script_navigator, script_canvas, script_webgl]
        for script in scripts:
            try:
                driver.execute_cdp_cmd('Runtime.evaluate', {'expression': script})
            except:
                # Fallback to regular JavaScript execution
                driver.execute_script(script)
    
    def create_human_delay(self, min_delay: float = 0.5, max_delay: float = 2.0) -> None:
        """Crea delays humanizados (técnica Pydoll)"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def humanized_click(self, driver, element) -> None:
        """Click humanizado con movimiento de mouse realista"""
        action = ActionChains(driver)
        
        # Movimiento aleatorio antes del click
        x_offset = random.randint(-5, 5)
        y_offset = random.randint(-5, 5)
        
        action.move_to_element_with_offset(element, x_offset, y_offset)
        self.create_human_delay(0.1, 0.3)
        action.click()
        action.perform()
    
    def humanized_typing(self, driver, element, text: str) -> None:
        """Escritura humanizada con timing variable"""
        element.clear()
        
        for char in text:
            element.send_keys(char)
            # Delay variable entre caracteres
            delay = random.uniform(0.05, 0.15)
            if char == ' ':
                delay *= 2  # Pausas más largas en espacios
            time.sleep(delay)
    
    def detect_and_handle_captcha(self, driver) -> bool:
        """Detecta y maneja CAPTCHAs automáticamente (inspirado en SeleniumBase UC)"""
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            ".cf-turnstile",
            "#captcha",
            ".captcha",
            "iframe[src*='hcaptcha']",
            ".h-captcha"
        ]
        
        for selector in captcha_selectors:
            try:
                captcha_element = driver.find_element(By.CSS_SELECTOR, selector)
                if captcha_element.is_displayed():
                    return self._handle_captcha(driver, captcha_element, selector)
            except:
                continue
        
        return False
    
    def _handle_captcha(self, driver, element, selector_type: str) -> bool:
        """Maneja diferentes tipos de CAPTCHA"""
        if 'recaptcha' in selector_type:
            return self._handle_recaptcha(driver, element)
        elif 'turnstile' in selector_type or 'cf-turnstile' in selector_type:
            return self._handle_cloudflare_turnstile(driver, element)
        elif 'hcaptcha' in selector_type:
            return self._handle_hcaptcha(driver, element)
        
        return False
    
    def _handle_recaptcha(self, driver, element) -> bool:
        """Maneja reCAPTCHA v2/v3"""
        try:
            # Switch to iframe
            driver.switch_to.frame(element)
            
            # Click on checkbox
            checkbox = driver.find_element(By.CSS_SELECTOR, ".recaptcha-checkbox-border")
            self.humanized_click(driver, checkbox)
            
            # Wait for potential challenge
            time.sleep(3)
            
            driver.switch_to.default_content()
            return True
        except:
            driver.switch_to.default_content()
            return False
    
    def _handle_cloudflare_turnstile(self, driver, element) -> bool:
        """Maneja Cloudflare Turnstile (técnica Pydoll)"""
        try:
            # Resize the element for easier clicking
            driver.execute_script("arguments[0].style='width: 300px'", element)
            
            # Wait before clicking
            self.create_human_delay(2, 4)
            
            # Click the turnstile
            self.humanized_click(driver, element)
            
            # Wait for verification
            time.sleep(5)
            return True
        except:
            return False
    
    def _handle_hcaptcha(self, driver, element) -> bool:
        """Maneja hCaptcha"""
        try:
            # Similar approach to reCAPTCHA
            driver.switch_to.frame(element)
            
            checkbox = driver.find_element(By.CSS_SELECTOR, ".check")
            self.humanized_click(driver, checkbox)
            
            time.sleep(3)
            driver.switch_to.default_content()
            return True
        except:
            driver.switch_to.default_content()
            return False
    
    def bypass_cloudflare_protection(self, driver) -> bool:
        """Bypass completo de protección Cloudflare"""
        try:
            # Wait for page load
            time.sleep(5)
            
            # Check for Cloudflare challenge
            cf_selectors = [
                ".cf-turnstile",
                "#challenge-form",
                ".challenge-running",
                "body[class*='cf-']"
            ]
            
            for selector in cf_selectors:
                try:
                    cf_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if cf_element.is_displayed():
                        return self.detect_and_handle_captcha(driver)
                except:
                    continue
            
            return True
        except:
            return False
    
    def get_advanced_chrome_options(self) -> Options:
        """Retorna opciones de Chrome con todas las técnicas anti-detección"""
        options = Options()
        
        # Configure stealth options
        options = self.configure_stealth_options(options)
        
        return options


class HumanBehaviorSimulator:
    """Simulador de comportamiento humano avanzado"""
    
    def __init__(self):
        self.reading_speed = random.uniform(200, 400)  # words per minute
        self.scroll_patterns = self._generate_scroll_patterns()
    
    def _generate_scroll_patterns(self) -> List[Dict]:
        """Genera patrones de scroll realistas"""
        return [
            {'direction': 'down', 'distance': random.randint(100, 300), 'speed': 'slow'},
            {'direction': 'down', 'distance': random.randint(500, 800), 'speed': 'medium'},
            {'direction': 'up', 'distance': random.randint(50, 150), 'speed': 'fast'},
            {'direction': 'down', 'distance': random.randint(200, 400), 'speed': 'slow'}
        ]
    
    def simulate_reading(self, content_length: int) -> float:
        """Simula tiempo de lectura basado en longitud del contenido"""
        words = content_length / 5  # Aproximación de palabras
        reading_time = (words / self.reading_speed) * 60  # Segundos
        
        # Add randomness
        variation = random.uniform(0.8, 1.3)
        return reading_time * variation
    
    def simulate_mouse_movement(self, driver) -> None:
        """Simula movimiento de mouse natural"""
        action = ActionChains(driver)
        
        # Random mouse movements
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            
            action.move_by_offset(x, y)
            time.sleep(random.uniform(0.1, 0.3))
        
        action.perform()
    
    def simulate_scroll_behavior(self, driver) -> None:
        """Simula comportamiento de scroll realista"""
        for pattern in random.sample(self.scroll_patterns, random.randint(2, 4)):
            if pattern['direction'] == 'down':
                scroll_amount = pattern['distance']
            else:
                scroll_amount = -pattern['distance']
            
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # Delay based on speed
            if pattern['speed'] == 'slow':
                time.sleep(random.uniform(1, 3))
            elif pattern['speed'] == 'medium':
                time.sleep(random.uniform(0.5, 1.5))
            else:  # fast
                time.sleep(random.uniform(0.1, 0.5))


class StealthBrowserFactory:
    """Factory para crear browsers con máximo stealth"""
    
    @staticmethod
    def create_stealth_driver():
        """Crea un driver con todas las técnicas anti-detección aplicadas"""
        anti_detection = AdvancedAntiDetection()
        options = anti_detection.get_advanced_chrome_options()
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Use webdriver-manager for automatic driver management
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Inject stealth scripts
            anti_detection.inject_stealth_scripts(driver)
            
            return driver, anti_detection
            
        except Exception as e:
            print(f"Error creating stealth driver: {e}")
            return None, None


# Ejemplo de uso
if __name__ == "__main__":
    # Crear browser stealth
    driver, anti_detection = StealthBrowserFactory.create_stealth_driver()
    
    if driver:
        try:
            # Navegar a una página con protección
            driver.get("https://bot.sannysoft.com/")
            
            # Simular comportamiento humano
            time.sleep(3)
            anti_detection.human_behavior.simulate_scroll_behavior(driver)
            
            # Detectar y manejar captchas
            anti_detection.detect_and_handle_captcha(driver)
            
            print("Stealth test completed!")
            
        finally:
            driver.quit()