@echo off
echo [INFO] Iniciando pruebas de Playwright...
echo.

REM Verificar si el entorno virtual existe
if not exist "..\.venv\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado. Ejecuta primero el script de instalación.
    pause
    exit /b 1
)

REM Activar entorno virtual
call ..\.venv\Scripts\activate.bat

REM Instalar navegadores de Playwright si no están instalados
echo [INFO] Instalando navegadores de Playwright...
playwright install

REM Ejecutar pruebas básicas de Playwright
echo [INFO] Ejecutando pruebas de Playwright...
python -c "
import asyncio
from playwright.async_api import async_playwright

async def test_basic():
    print('Probando Playwright básico...')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://httpbin.org/html')
        title = await page.title()
        print(f'Título de la página: {title}')
        await browser.close()
    print('Prueba básica completada exitosamente')

asyncio.run(test_basic())
"

if %errorlevel% neq 0 (
    echo [ERROR] Falló la prueba básica de Playwright
    pause
    exit /b 1
)

REM Ejecutar pruebas de navegación
echo [INFO] Ejecutando pruebas de navegación...
python -c "
import asyncio
from playwright.async_api import async_playwright

async def test_navigation():
    print('Probando navegación con Playwright...')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

n        # Visitar una página de ejemplo
        await page.goto('https://quotes.toscrape.com/')
        print('Página cargada')

n        # Extraer algunos elementos
        quotes = await page.query_selector_all('.quote')
        print(f'Encontradas {len(quotes)} citas')

n        # Tomar una captura de pantalla
        await page.screenshot(path='screenshots/playwright_test.png')
        print('Captura de pantalla guardada')

        await browser.close()
    print('Prueba de navegación completada')

asyncio.run(test_navigation())
"

if %errorlevel% neq 0 (
    echo [ERROR] Falló la prueba de navegación
    pause
    exit /b 1
)

echo [SUCCESS] Todas las pruebas de Playwright pasaron exitosamente
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
