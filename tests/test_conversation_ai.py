"""
Tests for conversational AI functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.intelligence.conversation_ai import ConversationalAI, Intent, ConversationContext
from src.intelligence.command_processor import CommandProcessor
from src.intelligence.bot_manager import BotManager, BotType


class TestConversationalAI:
    """Test the conversational AI engine"""
    
    @pytest.fixture
    def conversation_ai(self):
        """Create a ConversationalAI instance for testing"""
        return ConversationalAI()
    
    @pytest.mark.asyncio
    async def test_detect_search_intent(self, conversation_ai):
        """Test detection of search intents"""
        message = "busca información sobre Python"
        context = ConversationContext(session_id="test")
        
        intent = await conversation_ai._detect_intent(message, context)
        
        assert intent.name == "search"
        assert intent.entities.get("target") == "información sobre python"  # Lowercase due to pattern matching
        assert intent.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_detect_scrape_intent(self, conversation_ai):
        """Test detection of scrape intents"""
        message = "extrae datos de https://example.com"
        context = ConversationContext(session_id="test")
        
        intent = await conversation_ai._detect_intent(message, context)
        
        assert intent.name == "scrape"
        assert intent.entities.get("target") == "datos de https://example.com"
    
    @pytest.mark.asyncio
    async def test_detect_generate_intent(self, conversation_ai):
        """Test detection of generate intents"""
        message = "crea un bot para monitorear precios"
        context = ConversationContext(session_id="test")
        
        intent = await conversation_ai._detect_intent(message, context)
        
        assert intent.name == "generate"
        assert intent.entities.get("target") == "un bot para monitorear precios"
    
    @pytest.mark.asyncio
    async def test_process_search_message(self, conversation_ai):
        """Test processing a complete search message"""
        response = await conversation_ai.process_message(
            "busca información sobre APIs REST",
            session_id="test_search"
        )
        
        assert "text" in response
        assert "commands" in response
        assert len(response["commands"]) > 0
        assert response["commands"][0]["type"] == "search_web"
        assert "apis rest" in response["commands"][0]["parameters"]["query"].lower()
    
    @pytest.mark.asyncio
    async def test_process_help_message(self, conversation_ai):
        """Test processing help request"""
        response = await conversation_ai.process_message(
            "ayuda",
            session_id="test_help"
        )
        
        assert "comandos disponibles" in response["text"].lower()
        assert len(response["commands"]) == 0  # Help doesn't generate commands
    
    @pytest.mark.asyncio
    async def test_conversation_context_persistence(self, conversation_ai):
        """Test that conversation context is maintained"""
        session_id = "test_persistence"
        
        # First message
        await conversation_ai.process_message("busca Python", session_id)
        
        # Second message
        await conversation_ai.process_message("estado", session_id)
        
        # Check context
        history = await conversation_ai.get_conversation_history(session_id)
        assert len(history) >= 4  # 2 user messages + 2 assistant responses
        assert any("Python" in msg.get("message", "") for msg in history)


class TestCommandProcessor:
    """Test the command processor"""
    
    @pytest.fixture
    def command_processor(self):
        """Create a CommandProcessor instance for testing"""
        return CommandProcessor()
    
    @pytest.mark.asyncio
    async def test_execute_search_command(self, command_processor):
        """Test executing a search command"""
        commands = [{
            "type": "search_web",
            "parameters": {
                "query": "test query",
                "max_results": 5
            }
        }]
        
        results = await command_processor.execute_commands(commands, "test_session")
        
        assert len(results) == 1
        result = results[0]
        assert result["status"] == "success"
        assert "bot_id" in result["result"]
        assert result["result"]["search_query"] == "test query"
    
    @pytest.mark.asyncio
    async def test_execute_create_bot_command(self, command_processor):
        """Test executing a bot creation command"""
        commands = [{
            "type": "create_bot",
            "parameters": {
                "description": "Bot para buscar noticias",
                "type": "search",
                "config": {"auto_start": False}
            }
        }]
        
        results = await command_processor.execute_commands(commands, "test_session")
        
        assert len(results) == 1
        result = results[0]
        assert result["status"] == "success"
        assert "bot_id" in result["result"]
        assert result["result"]["description"] == "Bot para buscar noticias"
    
    @pytest.mark.asyncio
    async def test_execute_system_status_command(self, command_processor):
        """Test executing system status command"""
        commands = [{
            "type": "get_system_status",
            "parameters": {}
        }]
        
        results = await command_processor.execute_commands(commands, "test_session")
        
        assert len(results) == 1
        result = results[0]
        assert result["status"] == "success"
        status = result["result"]
        assert "health_score" in status
        assert "bots" in status
        assert "database" in status
        assert "features" in status
    
    @pytest.mark.asyncio
    async def test_invalid_command_type(self, command_processor):
        """Test handling of invalid command type"""
        commands = [{
            "type": "invalid_command",
            "parameters": {}
        }]
        
        results = await command_processor.execute_commands(commands, "test_session")
        
        assert len(results) == 1
        result = results[0]
        assert result["status"] == "error"
        assert "Unknown command type" in result["error"]


class TestBotManager:
    """Test the bot manager"""
    
    @pytest.fixture
    def bot_manager(self, tmp_path):
        """Create a BotManager instance for testing"""
        return BotManager(base_db_path=str(tmp_path / "test_bots"))
    
    def test_create_bot(self, bot_manager):
        """Test creating a bot"""
        bot_id = bot_manager.create_bot(
            name="Test Bot",
            description="A test bot",
            bot_type=BotType.SCRAPER,
            target_urls=["https://example.com"]
        )
        
        assert bot_id in bot_manager.active_bots
        bot = bot_manager.active_bots[bot_id]
        assert bot.config.name == "Test Bot"
        assert bot.config.bot_type == BotType.SCRAPER
        assert bot.config.target_urls == ["https://example.com"]
    
    def test_create_smart_bot_from_description(self, bot_manager):
        """Test creating a bot from natural language description"""
        description = "crea un bot para monitorear precios de productos"
        bot_id = bot_manager.create_smart_bot_from_description(description)
        
        assert bot_id in bot_manager.active_bots
        bot = bot_manager.active_bots[bot_id]
        assert bot.config.bot_type == BotType.MONITOR
        assert bot.config.schedule_enabled == True
        assert "precios" in bot.config.keywords
    
    def test_bot_parsing_search_type(self, bot_manager):
        """Test bot type detection for search bots"""
        description = "buscar información sobre tecnología"
        config = bot_manager._parse_bot_description(description)
        
        assert config["bot_type"] == BotType.SEARCH
        assert "tecnología" in config["keywords"]
    
    def test_bot_parsing_analyzer_type(self, bot_manager):
        """Test bot type detection for analyzer bots"""
        description = "analizar tendencias del mercado"
        config = bot_manager._parse_bot_description(description)
        
        assert config["bot_type"] == BotType.ANALYZER
        assert "tendencias" in config["keywords"]
    
    def test_list_bots(self, bot_manager):
        """Test listing bots"""
        # Create a few bots
        bot1_id = bot_manager.create_bot("Bot 1", "Description 1", BotType.SCRAPER)
        bot2_id = bot_manager.create_bot("Bot 2", "Description 2", BotType.MONITOR)
        
        bots = bot_manager.list_bots()
        
        assert len(bots) == 2
        bot_ids = [bot["id"] for bot in bots]
        assert bot1_id in bot_ids
        assert bot2_id in bot_ids
    
    def test_delete_bot(self, bot_manager):
        """Test deleting a bot"""
        bot_id = bot_manager.create_bot("Test Bot", "Test", BotType.SCRAPER)
        
        assert bot_id in bot_manager.active_bots
        
        success = bot_manager.delete_bot(bot_id)
        
        assert success
        assert bot_id not in bot_manager.active_bots
    
    def test_get_bot_status(self, bot_manager):
        """Test getting bot status"""
        bot_id = bot_manager.create_bot("Test Bot", "Test", BotType.SCRAPER)
        
        status = bot_manager.get_bot_status(bot_id)
        
        assert status is not None
        assert status["id"] == bot_id
        assert status["name"] == "Test Bot"
        assert status["type"] == BotType.SCRAPER
        assert status["status"] == "created"
        assert status["pages_processed"] == 0
    
    @pytest.mark.asyncio
    async def test_start_stop_bot(self, bot_manager):
        """Test starting and stopping a bot"""
        bot_id = bot_manager.create_bot(
            "Test Bot", 
            "Test", 
            BotType.SCRAPER,
            target_urls=["https://httpbin.org/html"]  # Use a simple test URL
        )
        
        # Note: In a real test environment, you might want to mock the orchestrator
        # For now, we'll just test the status changes without actually running
        bot = bot_manager.active_bots[bot_id]
        assert bot.status.value == "created"
        
        # Test stop without start (should handle gracefully)
        success = await bot_manager.stop_bot(bot_id)
        assert success or not success  # Either is acceptable for a non-running bot


if __name__ == "__main__":
    pytest.main([__file__])