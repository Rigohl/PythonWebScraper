# test_professional_tui.py

import pytest
from textual.app import App
from textual.widgets import Input, RichLog, Button
from src.tui.professional_app import WebScraperProfessionalApp, ChatOverlay
from src.intelligence.intent_recognizer import IntentRecognizer
from src.intelligence.intent_recognizer import Intent, IntentType

# Pruebas de IntentRecognizer
def test_intent_recognition():
    # Test de búsqueda
    search_msg = "busca productos en la categoría 'electronics'"
    intent = IntentRecognizer.recognize(search_msg)
    assert intent.type == IntentType.SEARCH
    assert intent.parameters["query"] == "electronics"

    # Test de crawling
    crawl_msg = "crawl the website 'https://example.com' with depth=2"
    intent = IntentRecognizer.recognize(crawl_msg)
    assert intent.type == IntentType.CRAWL
    assert "https://example.com" in intent.parameters["urls"]
    assert intent.parameters["depth"] == 2

    # Test de edición
    edit_msg = "cambia 'timeout: 30' por 'timeout: 60' en config.json"
    intent = IntentRecognizer.recognize(edit_msg)
    assert intent.type == IntentType.EDIT
    assert intent.parameters["file"] == "config.json"
    assert intent.parameters["old_content"] == "timeout: 30"
    assert intent.parameters["new_content"] == "timeout: 60"

    # Test de comando terminal
    term_msg = "ejecuta 'ls -la' en el terminal"
    intent = IntentRecognizer.recognize(term_msg)
    assert intent.type == IntentType.TERMINAL
    assert intent.parameters["command"] == "ls -la"

def test_intent_parameters():
    # Test de conocimiento
    knowledge_msg = "aprende de la fuente 'dataset.csv'"
    intent = IntentRecognizer.recognize(knowledge_msg)
    assert intent.type == IntentType.KNOWLEDGE
    assert intent.parameters["source"] == "dataset.csv"

    # Test de snapshot
    snapshot_msg = "guarda un snapshot como 'backup-2025'"
    intent = IntentRecognizer.recognize(snapshot_msg)
    assert intent.type == IntentType.SNAPSHOT
    assert intent.parameters["name"] == "backup-2025"

    # Test de status
    status_msg = "check system status and health"
    intent = IntentRecognizer.recognize(status_msg)
    assert intent.type == IntentType.STATUS
    assert len(intent.parameters) == 0  # No params for status

def test_invalid_intents():
    # Test mensaje vacío
    intent = IntentRecognizer.recognize("")
    assert intent.type == IntentType.UNKNOWN
    assert intent.confidence == 0.0

    # Test mensaje sin intención clara
    intent = IntentRecognizer.recognize("hola mundo")
    assert intent.type == IntentType.UNKNOWN
    assert intent.confidence == 0.0

# Pruebas del TUI
@pytest.mark.asyncio
async def test_app_mount():
    """Test que la app se monta correctamente"""
    app = WebScraperProfessionalApp()
    async with app.run_test() as pilot:
        # Verificar que los widgets principales existen
        header = app.query_one("Header")
        assert header is not None
        assert header.name == "Web Scraper PRO"

        tabs = app.query_one("TabbedContent")
        assert tabs is not None
        assert tabs.active == "dashboard-tab"

        # Verificar chat overlay
        chat = app.query_one("ChatOverlay")
        assert chat is not None
        assert isinstance(chat, ChatOverlay)

@pytest.mark.asyncio
async def test_chat_interaction():
    """Test las interacciones del chat"""
    app = WebScraperProfessionalApp()
    async with app.run_test() as pilot:
        chat = app.query_one("ChatOverlay")
        log = chat.query_one("#chat_log", RichLog)
        input_box = chat.query_one("#chat_input", Input)

        # Test comando de ayuda
        await pilot.press("enter")  # mensaje vacío
        assert "Chat listo" in log.render_lines()[0]

        input_box.value = "/help"
        await pilot.press("enter")
        help_text = log.render_lines()
        assert any("COMANDOS DISPONIBLES" in line for line in help_text)

        # Test comando de status
        input_box.value = "/status"
        await pilot.press("enter")
        status_text = log.render_lines()
        assert any("Estado scraping:" in line for line in status_text)

@pytest.mark.asyncio
async def test_scraping_controls():
    """Test los controles de scraping"""
    app = WebScraperProfessionalApp()
    async with app.run_test() as pilot:
        # Verificar botones de control
        start_btn = app.query_one("#start_scraping_btn", Button)
        stop_btn = app.query_one("#stop_scraping_btn", Button)
        pause_btn = app.query_one("#pause_scraping_btn", Button)

        assert start_btn is not None and not start_btn.disabled
        assert stop_btn is not None and stop_btn.disabled
        assert pause_btn is not None and pause_btn.disabled

        # Test inicio/parada de scraping
        await pilot.click(start_btn)
        assert app.scraping_active
        assert start_btn.disabled
        assert not stop_btn.disabled
        assert not pause_btn.disabled

        await pilot.click(stop_btn)
        assert not app.scraping_active
        assert not start_btn.disabled
        assert stop_btn.disabled
        assert pause_btn.disabled

@pytest.mark.asyncio
async def test_brain_integration():
    """Test la integración con HybridBrain"""
    app = WebScraperProfessionalApp()
    async with app.run_test() as pilot:
        chat = app.query_one("ChatOverlay")
        log = chat.query_one("#chat_log", RichLog)

        # Verificar inicialización del cerebro
        brain_status = app._brain
        assert brain_status is None  # El cerebro se inicializa bajo demanda

        # Enviar consulta que requiere cerebro
        input_box = chat.query_one("#chat_input", Input)
        input_box.value = "/brain"
        await pilot.press("enter")

        # Verificar que se muestra el estado del cerebro
        brain_text = log.render_lines()
        assert any("ESTADO DEL CEREBRO" in line for line in brain_text)

@pytest.mark.asyncio
async def test_keyboard_bindings():
    """Test los keybindings principales"""
    app = WebScraperProfessionalApp()
    async with app.run_test() as pilot:
        # Test F9 (toggle chat)
        chat = app.query_one("ChatOverlay")
        assert "chat-hidden" not in chat.classes
        
        await pilot.press("f9")
        assert "chat-hidden" in chat.classes
        
        await pilot.press("f9")
        assert "chat-hidden" not in chat.classes

        # Test F2 (dashboard)
        tabs = app.query_one("TabbedContent")
        await pilot.press("f2")
        assert tabs.active == "dashboard-tab"

if __name__ == '__main__':
    pytest.main(['-v', __file__])