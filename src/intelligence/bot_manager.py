"""
Bot Management System for PythonWebScraper

This module provides a comprehensive bot creation and management system,
allowing users to create specialized scraping bots for different purposes.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

from pydantic import BaseModel, Field

from ..database import DatabaseManager
from ..intelligence.llm_extractor import LLMExtractor
from ..managers.user_agent_manager import UserAgentManager
from ..settings import settings

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from ..orchestrator import ScrapingOrchestrator

logger = logging.getLogger(__name__)


class BotType(str, Enum):
    """Types of bots that can be created"""
    SCRAPER = "scraper"
    MONITOR = "monitor"  
    CRAWLER = "crawler"
    ANALYZER = "analyzer"
    SEARCH = "search"


class BotStatus(str, Enum):
    """Bot execution status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"


class BotConfig(BaseModel):
    """Configuration for a bot"""
    name: str = Field(description="Bot name")
    description: str = Field(description="Bot description")
    bot_type: BotType = Field(description="Type of bot")
    target_urls: List[str] = Field(default_factory=list, description="URLs to process")
    keywords: List[str] = Field(default_factory=list, description="Keywords to search for")
    concurrency: int = Field(default=2, description="Number of concurrent workers")
    delay_between_requests: float = Field(default=1.0, description="Delay between requests in seconds")
    respect_robots_txt: bool = Field(default=True, description="Whether to respect robots.txt")
    max_pages: Optional[int] = Field(default=None, description="Maximum pages to scrape")
    max_depth: int = Field(default=3, description="Maximum crawl depth")
    
    # Filtering options
    include_patterns: List[str] = Field(default_factory=list, description="URL patterns to include")
    exclude_patterns: List[str] = Field(default_factory=list, description="URL patterns to exclude")
    
    # Data extraction
    extract_images: bool = Field(default=False, description="Extract and analyze images")
    extract_links: bool = Field(default=True, description="Extract links")
    extract_text: bool = Field(default=True, description="Extract text content")
    use_llm_extraction: bool = Field(default=True, description="Use LLM for data extraction")
    
    # Scheduling
    schedule_enabled: bool = Field(default=False, description="Enable scheduled execution")
    schedule_interval: int = Field(default=3600, description="Schedule interval in seconds")
    
    # Notification settings
    notify_on_completion: bool = Field(default=True, description="Notify when bot completes")
    notify_on_error: bool = Field(default=True, description="Notify on errors")
    
    # Custom extraction schema
    extraction_schema: Optional[Dict[str, Any]] = Field(default=None, description="Custom extraction schema")


class Bot(BaseModel):
    """Represents a scraping bot instance"""
    
    model_config = {"arbitrary_types_allowed": True}
    
    id: str = Field(description="Unique bot identifier")
    config: BotConfig = Field(description="Bot configuration")
    status: BotStatus = Field(default=BotStatus.CREATED, description="Current status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    
    # Statistics
    pages_processed: int = Field(default=0, description="Number of pages processed")
    pages_successful: int = Field(default=0, description="Number of successful pages")
    pages_failed: int = Field(default=0, description="Number of failed pages")
    total_runtime: float = Field(default=0.0, description="Total runtime in seconds")
    
    # Results
    results_count: int = Field(default=0, description="Number of results collected")
    last_error: Optional[str] = Field(default=None, description="Last error message")
    output_files: List[str] = Field(default_factory=list, description="Generated output files")
    
    # Runtime data (excluded from serialization)
    orchestrator_task: Optional[Any] = Field(default=None, exclude=True, description="Running orchestrator task")
    db_manager: Optional[DatabaseManager] = Field(default=None, exclude=True, description="Database manager")


class BotManager:
    """Manages creation, execution, and monitoring of scraping bots"""
    
    def __init__(self, base_db_path: str = "bots"):
        self.base_db_path = Path(base_db_path)
        self.base_db_path.mkdir(exist_ok=True)
        
        self.active_bots: Dict[str, Bot] = {}
        self.bot_configs_file = self.base_db_path / "bot_configs.json"
        
        # Load existing bot configurations
        self._load_bot_configs()
        
        # Initialize shared components
        self.user_agent_manager = UserAgentManager()
        self.llm_extractor = LLMExtractor() if settings.LLM_API_KEY else None

    def create_bot(
        self, 
        name: str,
        description: str,
        bot_type: BotType,
        **kwargs
    ) -> str:
        """
        Create a new bot with the given configuration
        
        Returns:
            Bot ID
        """
        bot_id = str(uuid.uuid4())
        
        config = BotConfig(
            name=name,
            description=description,
            bot_type=bot_type,
            **kwargs
        )
        
        bot = Bot(
            id=bot_id,
            config=config
        )
        
        self.active_bots[bot_id] = bot
        self._save_bot_configs()
        
        logger.info(f"Created bot '{name}' (ID: {bot_id}) of type {bot_type}")
        return bot_id

    def create_smart_bot_from_description(self, description: str) -> str:
        """
        Create a bot using AI to interpret the description and determine optimal configuration
        
        Args:
            description: Natural language description of what the bot should do
            
        Returns:
            Bot ID
        """
        # Parse description to determine bot type and configuration
        bot_config = self._parse_bot_description(description)
        
        return self.create_bot(**bot_config)

    def _parse_bot_description(self, description: str) -> Dict[str, Any]:
        """Parse natural language description into bot configuration"""
        description_lower = description.lower()
        
        # Determine bot type
        if any(word in description_lower for word in ['monitor', 'vigilar', 'watch']):
            bot_type = BotType.MONITOR
        elif any(word in description_lower for word in ['analyze', 'analizar', 'analysis']):
            bot_type = BotType.ANALYZER
        elif any(word in description_lower for word in ['search', 'buscar', 'find']):
            bot_type = BotType.SEARCH
        elif any(word in description_lower for word in ['crawl', 'crawler', 'deep']):
            bot_type = BotType.CRAWLER
        else:
            bot_type = BotType.SCRAPER
        
        # Extract keywords
        keywords = []
        keyword_indicators = ['sobre', 'about', 'de', 'for', 'relacionado', 'related']
        for indicator in keyword_indicators:
            if indicator in description_lower:
                parts = description_lower.split(indicator, 1)
                if len(parts) > 1:
                    keywords.extend([k.strip() for k in parts[1].split(',')[:3]])
        
        # Determine configuration based on type
        config = {
            'name': f"Bot_{bot_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'description': description,
            'bot_type': bot_type,
            'keywords': keywords[:5],  # Limit keywords
        }
        
        # Set type-specific defaults
        if bot_type == BotType.MONITOR:
            config.update({
                'schedule_enabled': True,
                'schedule_interval': 3600,  # 1 hour
                'concurrency': 1,
                'max_pages': 10
            })
        elif bot_type == BotType.CRAWLER:
            config.update({
                'max_depth': 5,
                'concurrency': 3,
                'max_pages': 100
            })
        elif bot_type == BotType.SEARCH:
            config.update({
                'use_llm_extraction': True,
                'concurrency': 2,
                'max_pages': 20
            })
        
        return config

    async def start_bot(self, bot_id: str) -> bool:
        """Start a bot by its ID"""
        if bot_id not in self.active_bots:
            logger.error(f"Bot {bot_id} not found")
            return False
        
        bot = self.active_bots[bot_id]
        
        if bot.status == BotStatus.RUNNING:
            logger.warning(f"Bot {bot_id} is already running")
            return True
        
        try:
            # Create database manager for this bot
            bot_db_path = self.base_db_path / f"bot_{bot_id}.db"
            bot.db_manager = DatabaseManager(str(bot_db_path))
            
            # Configure orchestrator based on bot type
            orchestrator = await self._create_orchestrator_for_bot(bot)
            
            # Start the bot
            bot.status = BotStatus.RUNNING
            bot.started_at = datetime.now()
            
            # Run orchestrator in background task
            bot.orchestrator_task = asyncio.create_task(
                self._run_bot_orchestrator(bot, orchestrator)
            )
            
            self._save_bot_configs()
            logger.info(f"Started bot {bot_id}")
            return True
            
        except Exception as e:
            bot.status = BotStatus.ERROR
            bot.last_error = str(e)
            self._save_bot_configs()
            logger.error(f"Failed to start bot {bot_id}: {e}")
            return False

    async def stop_bot(self, bot_id: str) -> bool:
        """Stop a running bot"""
        if bot_id not in self.active_bots:
            return False
        
        bot = self.active_bots[bot_id]
        
        if bot.orchestrator_task:
            bot.orchestrator_task.cancel()
            try:
                await bot.orchestrator_task
            except asyncio.CancelledError:
                pass
        
        bot.status = BotStatus.STOPPED
        bot.completed_at = datetime.now()
        if bot.started_at:
            bot.total_runtime = (bot.completed_at - bot.started_at).total_seconds()
        
        self._save_bot_configs()
        logger.info(f"Stopped bot {bot_id}")
        return True

    async def _create_orchestrator_for_bot(self, bot: Bot) -> "ScrapingOrchestrator":
        """Create and configure orchestrator for a specific bot"""
        # Import here to avoid circular import
        from ..orchestrator import ScrapingOrchestrator
        
        config = bot.config
        
        # Use bot-specific database
        db_manager = bot.db_manager
        
        # Configure start URLs based on bot type
        start_urls = config.target_urls.copy()
        
        if config.bot_type == BotType.SEARCH and config.keywords:
            # Generate search URLs for keywords
            search_urls = []
            for keyword in config.keywords:
                # Add common search engines (customize as needed)
                search_urls.extend([
                    f"https://www.google.com/search?q={keyword.replace(' ', '+')}",
                    f"https://duckduckgo.com/?q={keyword.replace(' ', '+')}",
                ])
            start_urls.extend(search_urls[:5])  # Limit search URLs
        
        if not start_urls:
            # Fallback URLs if none specified
            start_urls = ["https://example.com"]
        
        # Create orchestrator
        orchestrator = ScrapingOrchestrator(
            start_urls=start_urls,
            db_manager=db_manager,
            user_agent_manager=self.user_agent_manager,
            llm_extractor=self.llm_extractor,
            concurrency=config.concurrency,
            respect_robots_txt=config.respect_robots_txt,
            stats_callback=lambda stats: self._update_bot_stats(bot.id, stats),
            alert_callback=lambda msg, level: self._handle_bot_alert(bot.id, msg, level)
        )
        
        return orchestrator

    async def _run_bot_orchestrator(self, bot: Bot, orchestrator: "ScrapingOrchestrator"):
        """Run the orchestrator for a bot"""
        try:
            async with orchestrator.playwright_context() as browser:
                await orchestrator.run(browser)
            
            # Mark as completed
            bot.status = BotStatus.COMPLETED
            bot.completed_at = datetime.now()
            
        except asyncio.CancelledError:
            bot.status = BotStatus.STOPPED
        except Exception as e:
            bot.status = BotStatus.ERROR
            bot.last_error = str(e)
            logger.error(f"Bot {bot.id} error: {e}")
        finally:
            if bot.started_at:
                end_time = bot.completed_at or datetime.now()
                bot.total_runtime = (end_time - bot.started_at).total_seconds()
            self._save_bot_configs()

    def _update_bot_stats(self, bot_id: str, stats: Dict[str, Any]):
        """Update bot statistics from orchestrator callbacks"""
        if bot_id in self.active_bots:
            bot = self.active_bots[bot_id]
            bot.pages_processed = stats.get('processed', 0)
            bot.pages_successful = stats.get('SUCCESS', 0) 
            bot.pages_failed = stats.get('FAILED', 0)
            bot.results_count = stats.get('results_count', 0)

    def _handle_bot_alert(self, bot_id: str, message: str, level: str):
        """Handle alerts from bot orchestrators"""
        if level == 'error' and bot_id in self.active_bots:
            self.active_bots[bot_id].last_error = message
        
        logger.log(
            logging.ERROR if level == 'error' else logging.WARNING,
            f"Bot {bot_id}: {message}"
        )

    def get_bot_status(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a bot"""
        if bot_id not in self.active_bots:
            return None
        
        bot = self.active_bots[bot_id]
        return {
            'id': bot.id,
            'name': bot.config.name,
            'type': bot.config.bot_type,
            'status': bot.status,
            'created_at': bot.created_at.isoformat(),
            'started_at': bot.started_at.isoformat() if bot.started_at else None,
            'completed_at': bot.completed_at.isoformat() if bot.completed_at else None,
            'pages_processed': bot.pages_processed,
            'pages_successful': bot.pages_successful,
            'pages_failed': bot.pages_failed,
            'results_count': bot.results_count,
            'total_runtime': bot.total_runtime,
            'last_error': bot.last_error
        }

    def list_bots(self) -> List[Dict[str, Any]]:
        """List all bots and their statuses"""
        return [self.get_bot_status(bot_id) for bot_id in self.active_bots.keys()]

    def delete_bot(self, bot_id: str) -> bool:
        """Delete a bot and its data"""
        if bot_id not in self.active_bots:
            return False
        
        # Stop bot if running
        if self.active_bots[bot_id].status == BotStatus.RUNNING:
            asyncio.create_task(self.stop_bot(bot_id))
        
        # Delete bot database
        bot_db_path = self.base_db_path / f"bot_{bot_id}.db"
        if bot_db_path.exists():
            bot_db_path.unlink()
        
        # Remove from active bots
        del self.active_bots[bot_id]
        self._save_bot_configs()
        
        logger.info(f"Deleted bot {bot_id}")
        return True

    def _load_bot_configs(self):
        """Load bot configurations from disk"""
        if self.bot_configs_file.exists():
            try:
                with open(self.bot_configs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for bot_data in data.get('bots', []):
                    bot = Bot(**bot_data)
                    # Reset running status on restart
                    if bot.status == BotStatus.RUNNING:
                        bot.status = BotStatus.STOPPED
                    self.active_bots[bot.id] = bot
                    
                logger.info(f"Loaded {len(self.active_bots)} bot configurations")
            except Exception as e:
                logger.error(f"Failed to load bot configurations: {e}")

    def _save_bot_configs(self):
        """Save bot configurations to disk"""
        try:
            data = {
                'bots': [bot.model_dump() for bot in self.active_bots.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.bot_configs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save bot configurations: {e}")

    async def get_bot_results(self, bot_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get results from a bot's database"""
        if bot_id not in self.active_bots:
            return []
        
        bot = self.active_bots[bot_id]
        if not bot.db_manager:
            bot_db_path = self.base_db_path / f"bot_{bot_id}.db"
            if bot_db_path.exists():
                bot.db_manager = DatabaseManager(str(bot_db_path))
            else:
                return []
        
        try:
            # Get recent results from bot's database
            results = bot.db_manager.get_recent_results(limit=limit)
            return [result.model_dump() for result in results]
        except Exception as e:
            logger.error(f"Failed to get bot results for {bot_id}: {e}")
            return []

    async def export_bot_data(self, bot_id: str, format: str = 'json') -> Optional[str]:
        """Export bot data to file"""
        if bot_id not in self.active_bots:
            return None
        
        bot = self.active_bots[bot_id]
        results = await self.get_bot_results(bot_id, limit=1000)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"bot_{bot_id}_{timestamp}.{format}"
        filepath = self.base_db_path / filename
        
        try:
            if format == 'json':
                export_data = {
                    'bot_info': self.get_bot_status(bot_id),
                    'results': results,
                    'exported_at': datetime.now().isoformat()
                }
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            elif format == 'csv':
                if bot.db_manager:
                    bot.db_manager.export_to_csv(str(filepath))
            
            bot.output_files.append(str(filepath))
            self._save_bot_configs()
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to export bot data for {bot_id}: {e}")
            return None