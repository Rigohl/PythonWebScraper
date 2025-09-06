"""
Módulo CDP (Chrome DevTools Protocol) directo
Inspirado en Pydoll para comunicación directa sin WebDriver
Máxima velocidad y stealth
"""

import asyncio
import json
import random
from typing import Callable, Dict, List

import aiohttp
import websockets


class CDPClient:
    """Cliente CDP directo para comunicación sin WebDriver"""

    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.websocket = None
        self.message_id = 0
        self.callbacks = {}
        self.event_handlers = {}

    async def connect(self):
        """Conecta al WebSocket CDP"""
        self.websocket = await websockets.connect(self.ws_url)

        # Start listening for messages
        asyncio.create_task(self._listen_messages())

    async def _listen_messages(self):
        """Escucha mensajes del WebSocket"""
        async for message in self.websocket:
            data = json.loads(message)

            if "id" in data and data["id"] in self.callbacks:
                # Response to a command
                callback = self.callbacks.pop(data["id"])
                callback["future"].set_result(data)
            elif "method" in data:
                # Event notification
                await self._handle_event(data)

    async def _handle_event(self, event_data: Dict):
        """Maneja eventos CDP"""
        method = event_data["method"]
        if method in self.event_handlers:
            for handler in self.event_handlers[method]:
                try:
                    await handler(event_data["params"])
                except Exception as e:
                    print(f"Error in event handler for {method}: {e}")

    async def send_command(self, method: str, params: Dict = None) -> Dict:
        """Envía comando CDP y espera respuesta"""
        self.message_id += 1
        message = {"id": self.message_id, "method": method, "params": params or {}}

        future = asyncio.Future()
        self.callbacks[self.message_id] = {"future": future}

        await self.websocket.send(json.dumps(message))

        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(future, timeout=30)
            return response
        except asyncio.TimeoutError:
            self.callbacks.pop(self.message_id, None)
            raise Exception(f"Timeout waiting for response to {method}")

    def on(self, event_method: str, handler: Callable):
        """Registra handler para eventos CDP"""
        if event_method not in self.event_handlers:
            self.event_handlers[event_method] = []
        self.event_handlers[event_method].append(handler)

    async def close(self):
        """Cierra conexión WebSocket"""
        if self.websocket:
            await self.websocket.close()


class StealthCDPTab:
    """Tab CDP con capacidades stealth avanzadas"""

    def __init__(self, cdp_client: CDPClient):
        self.cdp = cdp_client
        self.target_id = None
        self.session_id = None
        self.stealth_enabled = False

    async def enable_stealth_mode(self):
        """Habilita modo stealth completo"""
        if self.stealth_enabled:
            return

        # Enable required CDP domains
        await self.cdp.send_command("Runtime.enable")
        await self.cdp.send_command("Page.enable")
        await self.cdp.send_command("Network.enable")
        await self.cdp.send_command("DOM.enable")

        # Inject stealth scripts
        await self._inject_stealth_scripts()

        # Setup cloudflare detection
        self.cdp.on("Page.loadEventFired", self._handle_page_load)

        self.stealth_enabled = True

    async def _inject_stealth_scripts(self):
        """Inyecta scripts stealth usando CDP Runtime"""

        # Remove webdriver property
        webdriver_script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        """

        await self.cdp.send_command(
            "Runtime.evaluate", {"expression": webdriver_script}
        )

        # Spoof navigator properties
        navigator_script = """
        // Spoof navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
            configurable: true
        });

        // Spoof navigator.permissions
        const originalQuery = navigator.permissions.query;
        navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // Spoof navigator.plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
            configurable: true
        });
        """

        await self.cdp.send_command(
            "Runtime.evaluate", {"expression": navigator_script}
        )

        # Canvas fingerprint protection
        canvas_script = """
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, attributes) {
            const context = originalGetContext.call(this, type, attributes);

            if (type === '2d') {
                const originalGetImageData = context.getImageData;
                context.getImageData = function(sx, sy, sw, sh) {
                    const imageData = originalGetImageData.call(this, sx, sy, sw, sh);

                    // Add noise to canvas data
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        const noise = Math.floor(Math.random() * 10) - 5;
                        imageData.data[i] += noise;     // R
                        imageData.data[i + 1] += noise; // G
                        imageData.data[i + 2] += noise; // B
                    }

                    return imageData;
                };
            }

            return context;
        };
        """

        await self.cdp.send_command("Runtime.evaluate", {"expression": canvas_script})

        # WebGL fingerprint protection
        webgl_script = """
        const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // Spoof WEBGL_VENDOR and WEBGL_RENDERER
            if (parameter === 37445) { // WEBGL_VENDOR
                return 'Intel Inc.';
            }
            if (parameter === 37446) { // WEBGL_RENDERER
                return 'Intel(R) HD Graphics 620';
            }

            return originalGetParameter.call(this, parameter);
        };
        """

        await self.cdp.send_command("Runtime.evaluate", {"expression": webgl_script})

    async def _handle_page_load(self, params: Dict):
        """Maneja eventos de carga de página para detectar Cloudflare"""
        # Check for Cloudflare challenge
        cloudflare_check = """
        (() => {
            const cfElements = document.querySelectorAll('.cf-turnstile, #challenge-form, .challenge-running');
            return cfElements.length > 0;
        })()
        """

        result = await self.cdp.send_command(
            "Runtime.evaluate", {"expression": cloudflare_check, "returnByValue": True}
        )

        if result.get("result", {}).get("value"):
            await self._handle_cloudflare_challenge()

    async def _handle_cloudflare_challenge(self):
        """Maneja desafío Cloudflare automáticamente"""
        print("Cloudflare challenge detected, attempting bypass...")

        # Wait before attempting bypass
        await asyncio.sleep(random.uniform(2, 4))

        # Find and click turnstile
        turnstile_script = """
        (() => {
            const turnstile = document.querySelector('.cf-turnstile');
            if (turnstile) {
                // Resize for easier clicking
                turnstile.style.width = '300px';

                // Simulate human click
                const rect = turnstile.getBoundingClientRect();
                const x = rect.left + rect.width / 2 + (Math.random() - 0.5) * 10;
                const y = rect.top + rect.height / 2 + (Math.random() - 0.5) * 10;

                const clickEvent = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: x,
                    clientY: y
                });

                turnstile.dispatchEvent(clickEvent);
                return true;
            }
            return false;
        })()
        """

        result = await self.cdp.send_command(
            "Runtime.evaluate", {"expression": turnstile_script, "returnByValue": True}
        )

        if result.get("result", {}).get("value"):
            print("Cloudflare turnstile clicked, waiting for verification...")
            await asyncio.sleep(5)

    async def navigate(self, url: str):
        """Navega a una URL"""
        await self.cdp.send_command("Page.navigate", {"url": url})

        # Wait for load event
        load_event = asyncio.Future()

        async def on_load(params):
            load_event.set_result(True)

        self.cdp.on("Page.loadEventFired", on_load)

        try:
            await asyncio.wait_for(load_event, timeout=30)
        except asyncio.TimeoutError:
            print("Page load timeout")

    async def click_element(self, selector: str):
        """Hace click en elemento con comportamiento humanizado"""

        # Find element using DOM
        find_script = f"""
        (() => {{
            const element = document.querySelector('{selector}');
            if (element) {{
                const rect = element.getBoundingClientRect();
                return {{
                    x: rect.left + rect.width / 2,
                    y: rect.top + rect.height / 2,
                    found: true
                }};
            }}
            return {{ found: false }};
        }})()
        """

        result = await self.cdp.send_command(
            "Runtime.evaluate", {"expression": find_script, "returnByValue": True}
        )

        element_data = result.get("result", {}).get("value", {})

        if element_data.get("found"):
            # Add human-like randomness
            x = element_data["x"] + random.uniform(-5, 5)
            y = element_data["y"] + random.uniform(-5, 5)

            # Simulate mouse movement and click
            await self.cdp.send_command(
                "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y}
            )

            await asyncio.sleep(random.uniform(0.1, 0.3))

            await self.cdp.send_command(
                "Input.dispatchMouseEvent",
                {
                    "type": "mousePressed",
                    "x": x,
                    "y": y,
                    "button": "left",
                    "clickCount": 1,
                },
            )

            await asyncio.sleep(random.uniform(0.05, 0.15))

            await self.cdp.send_command(
                "Input.dispatchMouseEvent",
                {
                    "type": "mouseReleased",
                    "x": x,
                    "y": y,
                    "button": "left",
                    "clickCount": 1,
                },
            )

            return True

        return False

    async def type_text(self, text: str, humanized: bool = True):
        """Escribe texto con timing humanizado"""
        for char in text:
            await self.cdp.send_command(
                "Input.dispatchKeyEvent", {"type": "char", "text": char}
            )

            if humanized:
                # Variable delay between characters
                delay = random.uniform(0.05, 0.15)
                if char == " ":
                    delay *= 2  # Longer pause for spaces
                await asyncio.sleep(delay)

    async def get_content(self) -> str:
        """Obtiene contenido de la página"""
        result = await self.cdp.send_command(
            "Runtime.evaluate",
            {"expression": "document.documentElement.outerHTML", "returnByValue": True},
        )

        return result.get("result", {}).get("value", "")

    async def execute_script(self, script: str):
        """Ejecuta JavaScript y retorna resultado"""
        result = await self.cdp.send_command(
            "Runtime.evaluate", {"expression": script, "returnByValue": True}
        )

        return result.get("result", {}).get("value")

    async def intercept_requests(self, patterns: List[str] = None):
        """Intercepts network requests for analysis"""
        await self.cdp.send_command(
            "Fetch.enable",
            {"patterns": [{"urlPattern": pattern} for pattern in (patterns or ["*"])]},
        )

        # Handler for intercepted requests
        async def handle_request(params):
            request_id = params["requestId"]

            # Continue request (can be modified here)
            await self.cdp.send_command(
                "Fetch.continueRequest", {"requestId": request_id}
            )

        self.cdp.on("Fetch.requestPaused", handle_request)

    async def take_screenshot(self) -> str:
        """Toma screenshot en base64"""
        result = await self.cdp.send_command(
            "Page.captureScreenshot", {"format": "png", "quality": 80}
        )

        return result.get("result", {}).get("data", "")


class StealthCDPBrowser:
    """Browser CDP stealth completo"""

    def __init__(self):
        self.cdp_client = None
        self.tab = None
        self.browser_process = None

    async def launch(self, headless: bool = True, debug_port: int = 9222):
        """Lanza browser con CDP habilitado"""
        import platform
        import subprocess

        # Chrome arguments for maximum stealth
        args = [
            "--remote-debugging-port=" + str(debug_port),
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-blink-features=AutomationControlled",
            "--exclude-switches=enable-automation",
            "--use-automation-extension=false",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",
            "--disable-default-apps",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
        ]

        if headless:
            args.append("--headless")

        # Platform-specific Chrome path
        system = platform.system()
        if system == "Windows":
            chrome_path = "chrome.exe"
        elif system == "Darwin":  # macOS
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:  # Linux
            chrome_path = "google-chrome"

        # Launch browser
        try:
            self.browser_process = subprocess.Popen([chrome_path] + args)

            # Wait for browser to start
            await asyncio.sleep(3)

            # Connect to CDP
            await self._connect_cdp(debug_port)

        except Exception as e:
            print(f"Error launching browser: {e}")
            raise

    async def _connect_cdp(self, port: int):
        """Conecta al CDP WebSocket"""
        # Get WebSocket URL
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:{port}/json") as response:
                targets = await response.json()

                # Find page target
                page_target = None
                for target in targets:
                    if target["type"] == "page":
                        page_target = target
                        break

                if not page_target:
                    raise Exception("No page target found")

                ws_url = page_target["webSocketDebuggerUrl"]

        # Connect to WebSocket
        self.cdp_client = CDPClient(ws_url)
        await self.cdp_client.connect()

        # Create stealth tab
        self.tab = StealthCDPTab(self.cdp_client)
        await self.tab.enable_stealth_mode()

    async def close(self):
        """Cierra browser y conexiones"""
        if self.cdp_client:
            await self.cdp_client.close()

        if self.browser_process:
            self.browser_process.terminate()
            self.browser_process.wait()


# Ejemplo de uso
async def main():
    """Ejemplo de uso del browser CDP stealth"""
    browser = StealthCDPBrowser()

    try:
        # Launch browser
        await browser.launch(headless=False)

        # Navigate to test page
        await browser.tab.navigate("https://bot.sannysoft.com/")

        # Wait to see results
        await asyncio.sleep(10)

        # Take screenshot
        screenshot_data = await browser.tab.take_screenshot()
        print(f"Screenshot taken: {len(screenshot_data)} bytes")

        # Get page content
        content = await browser.tab.get_content()
        print(f"Page content length: {len(content)}")

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
