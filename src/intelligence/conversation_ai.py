"""
Conversational AI Module for PythonWebScraper

This module provides natural language understanding and conversation management
for the web scraper, enabling users to interact through natural language
commands like "busca esto", "genera esto", etc.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from ..settings import settings
from .llm_extractor import LLMExtractor

logger = logging.getLogger(__name__)


class Intent(BaseModel):
    """Represents a detected user intent"""
    name: str = Field(description="The intent name (e.g., 'search', 'scrape', 'create_bot')")
    confidence: float = Field(description="Confidence score 0-1")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")


class ConversationContext(BaseModel):
    """Maintains conversation context and history"""
    session_id: str
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_topic: Optional[str] = None
    active_bots: List[str] = Field(default_factory=list)
    last_intent: Optional[Intent] = None
    context_data: Dict[str, Any] = Field(default_factory=dict)


class ConversationalAI:
    """
    Main conversational AI engine that processes natural language inputs
    and converts them to executable commands for the scraper system.
    """
    
    def __init__(self, llm_extractor: Optional[LLMExtractor] = None):
        self.llm_extractor = llm_extractor or LLMExtractor()
        self.context_store: Dict[str, ConversationContext] = {}
        
        # Intent patterns for Spanish commands
        self.intent_patterns = {
            'search': [
                r'busca\s+(.+)',
                r'buscar\s+(.+)', 
                r'encuentra\s+(.+)',
                r'encontrar\s+(.+)',
                r'busca\s*:\s*(.+)',
                r'search\s+(.+)',
                r'find\s+(.+)'
            ],
            'scrape': [
                r'extrae\s+(.+)',
                r'extraer\s+(.+)',
                r'raspa\s+(.+)',
                r'obtén\s+(.+)',
                r'scrape\s+(.+)',
                r'scraper?\s+(.+)',
                r'crawl\s+(.+)'
            ],
            'generate': [
                r'genera\s+(.+)',
                r'generar\s+(.+)',
                r'crea\s+(.+)',
                r'crear\s+(.+)',
                r'haz\s+(.+)',
                r'hacer\s+(.+)',
                r'generate\s+(.+)',
                r'create\s+(.+)'
            ],
            'analyze': [
                r'analiza\s+(.+)',
                r'analizar\s+(.+)',
                r'examina\s+(.+)',
                r'estudia\s+(.+)',
                r'analyze\s+(.+)',
                r'examine\s+(.+)'
            ],
            'help': [
                r'ayuda',
                r'help',
                r'qué\s+puedes\s+hacer',
                r'que\s+puedes\s+hacer',
                r'comandos',
                r'commands'
            ],
            'status': [
                r'estado',
                r'status',
                r'cómo\s+va',
                r'como\s+va',
                r'progreso',
                r'progress'
            ]
        }
        
        # Command mappings
        self.command_mappings = {
            'search': self._handle_search_intent,
            'scrape': self._handle_scrape_intent,
            'generate': self._handle_generate_intent,
            'analyze': self._handle_analyze_intent,
            'help': self._handle_help_intent,
            'status': self._handle_status_intent
        }

    async def process_message(
        self, 
        message: str, 
        session_id: str, 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language message and return actionable response
        
        Args:
            message: User's natural language input
            session_id: Unique session identifier
            user_id: Optional user identifier
            
        Returns:
            Dictionary containing response, commands, and metadata
        """
        # Get or create conversation context
        context = self._get_context(session_id, user_id)
        
        # Add message to history
        context.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'role': 'user',
            'message': message,
            'processed': False
        })
        
        try:
            # Detect intent
            intent = await self._detect_intent(message, context)
            context.last_intent = intent
            
            # Process intent and generate response
            response = await self._process_intent(intent, message, context)
            
            # Add response to history
            context.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'assistant',
                'message': response.get('text', ''),
                'intent': intent.name,
                'commands': response.get('commands', []),
                'processed': True
            })
            
            # Update context
            self.context_store[session_id] = context
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                'text': f"Lo siento, hubo un error procesando tu mensaje: {str(e)}",
                'commands': [],
                'error': str(e)
            }

    async def _detect_intent(self, message: str, context: ConversationContext) -> Intent:
        """Detect user intent from natural language message"""
        message_lower = message.lower().strip()
        
        # First try pattern matching for quick detection
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    entities = {}
                    if match.groups():
                        entities['target'] = match.group(1).strip()
                    
                    return Intent(
                        name=intent_name,
                        confidence=0.9,
                        entities=entities,
                        parameters={'matched_pattern': pattern}
                    )
        
        # Fall back to LLM-based intent detection for complex cases
        if self.llm_extractor and settings.LLM_API_KEY:
            try:
                llm_intent = await self._llm_intent_detection(message, context)
                if llm_intent:
                    return llm_intent
            except Exception as e:
                logger.warning(f"LLM intent detection failed: {e}")
        
        # Default to unknown intent
        return Intent(
            name='unknown',
            confidence=0.1,
            entities={'original_message': message},
            parameters={}
        )

    async def _llm_intent_detection(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Optional[Intent]:
        """Use LLM to detect complex intents"""
        
        system_prompt = """
        Eres un asistente que analiza mensajes para detectar intenciones. 
        Clasifica el mensaje en una de estas categorías:
        - search: buscar información
        - scrape: extraer datos de sitios web
        - generate: crear o generar algo
        - analyze: analizar datos o información
        - help: solicitar ayuda
        - status: consultar estado
        - unknown: no está claro
        
        Extrae también las entidades relevantes del mensaje.
        """
        
        # This would use the LLM to classify intent more accurately
        # For now, return None to fall back to pattern matching
        return None

    async def _process_intent(
        self, 
        intent: Intent, 
        original_message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Process detected intent and generate response with commands"""
        
        if intent.name in self.command_mappings:
            handler = self.command_mappings[intent.name]
            return await handler(intent, original_message, context)
        else:
            return await self._handle_unknown_intent(intent, original_message, context)

    async def _handle_search_intent(
        self, 
        intent: Intent, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle search-related intents"""
        target = intent.entities.get('target', '')
        
        if not target:
            return {
                'text': "¿Qué te gustaría que busque? Por favor, especifica el tema o término de búsqueda.",
                'commands': []
            }
        
        # Generate search commands
        commands = [
            {
                'type': 'search_web',
                'parameters': {
                    'query': target,
                    'max_results': 10,
                    'deep_crawl': False
                }
            }
        ]
        
        return {
            'text': f"Perfecto, voy a buscar información sobre '{target}'. Iniciando búsqueda...",
            'commands': commands,
            'intent': intent.name,
            'entities': intent.entities
        }

    async def _handle_scrape_intent(
        self, 
        intent: Intent, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle scraping-related intents"""
        target = intent.entities.get('target', '')
        
        # Check if target looks like a URL
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message)
        
        if urls:
            commands = [
                {
                    'type': 'crawl_urls',
                    'parameters': {
                        'urls': urls,
                        'respect_robots': False,
                        'concurrency': 3
                    }
                }
            ]
            return {
                'text': f"Iniciando el scraping de {len(urls)} URL(s)...",
                'commands': commands
            }
        elif target:
            return {
                'text': f"Para hacer scraping necesito una URL específica. ¿Podrías proporcionar la URL de '{target}'?",
                'commands': []
            }
        else:
            return {
                'text': "Para hacer scraping necesito que me proporciones una URL específica.",
                'commands': []
            }

    async def _handle_generate_intent(
        self, 
        intent: Intent, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle generation-related intents"""
        target = intent.entities.get('target', '')
        
        # Check for bot creation keywords
        bot_keywords = ['bot', 'scraper', 'crawler', 'monitor']
        if any(keyword in target.lower() for keyword in bot_keywords):
            return await self._handle_bot_creation(target, context)
        
        return {
            'text': f"¿Qué tipo de contenido te gustaría que genere? Puedo crear bots de scraping, reportes, análisis, etc.",
            'commands': []
        }

    async def _handle_bot_creation(self, description: str, context: ConversationContext) -> Dict[str, Any]:
        """Handle bot creation requests"""
        bot_id = f"bot_{len(context.active_bots) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        commands = [
            {
                'type': 'create_bot',
                'parameters': {
                    'bot_id': bot_id,
                    'description': description,
                    'type': 'scraper',
                    'config': {
                        'auto_start': True,
                        'concurrency': 2
                    }
                }
            }
        ]
        
        context.active_bots.append(bot_id)
        
        return {
            'text': f"Creando bot '{bot_id}' basado en: {description}",
            'commands': commands,
            'bot_id': bot_id
        }

    async def _handle_analyze_intent(
        self, 
        intent: Intent, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle analysis-related intents"""
        target = intent.entities.get('target', '')
        
        commands = [
            {
                'type': 'analyze_data',
                'parameters': {
                    'target': target,
                    'analysis_type': 'comprehensive'
                }
            }
        ]
        
        return {
            'text': f"Iniciando análisis de '{target}'...",
            'commands': commands
        }

    async def _handle_help_intent(
        self, 
        intent: Intent, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle help requests"""
        help_text = """
        🤖 **Comandos disponibles:**
        
        **Búsqueda:**
        - "busca información sobre Python"
        - "encuentra datos de APIs REST"
        
        **Scraping:**
        - "extrae datos de https://ejemplo.com"
        - "hacer scraping de esta página"
        
        **Generación:**
        - "crea un bot para monitorear precios"
        - "genera un scraper para noticias"
        
        **Análisis:**
        - "analiza los datos recopilados"
        - "examina las tendencias"
        
        **Estado:**
        - "estado" - ver progreso actual
        - "cómo va" - estadísticas del sistema
        
        ¡Puedes hablar de manera natural conmigo!
        """
        
        return {
            'text': help_text,
            'commands': []
        }

    async def _handle_status_intent(
        self, 
        intent: Intent, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle status requests"""
        commands = [
            {
                'type': 'get_system_status',
                'parameters': {}
            }
        ]
        
        return {
            'text': "Obteniendo estado del sistema...",
            'commands': commands
        }

    async def _handle_unknown_intent(
        self, 
        intent: Intent, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle unknown intents"""
        return {
            'text': "No estoy seguro de entender lo que necesitas. ¿Podrías ser más específico? Puedes decir 'ayuda' para ver los comandos disponibles.",
            'commands': [],
            'suggestions': [
                "busca información sobre...",
                "extrae datos de...",
                "crea un bot para...",
                "ayuda"
            ]
        }

    def _get_context(self, session_id: str, user_id: Optional[str] = None) -> ConversationContext:
        """Get or create conversation context"""
        if session_id not in self.context_store:
            self.context_store[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id
            )
        return self.context_store[session_id]

    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        if session_id in self.context_store:
            return self.context_store[session_id].conversation_history
        return []

    async def clear_context(self, session_id: str) -> bool:
        """Clear conversation context for a session"""
        if session_id in self.context_store:
            del self.context_store[session_id]
            return True
        return False