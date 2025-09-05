"""
Chat Widget for Conversational AI Interface

This widget provides a chat interface integrated with the scraper's TUI,
allowing users to interact naturally with the system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.events import Key
from textual.message import Message
from textual.widgets import Button, Input, Label, RichLog, Static
from textual.worker import Worker

from ..intelligence.command_processor import CommandProcessor
from ..intelligence.conversation_ai import ConversationalAI

logger = logging.getLogger(__name__)


class ChatMessage(Message):
    """Message sent when user submits chat input"""
    
    def __init__(self, text: str, session_id: str) -> None:
        self.text = text
        self.session_id = session_id
        super().__init__()


class ChatWidget(Container):
    """Interactive chat widget for conversational AI"""
    
    def __init__(
        self, 
        session_id: str = "default",
        command_processor: Optional[CommandProcessor] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.conversation_ai = ConversationalAI()
        self.command_processor = command_processor or CommandProcessor()
        
        # Chat state
        self.is_processing = False
        self.message_count = 0

    def compose(self) -> ComposeResult:
        """Compose the chat widget layout"""
        with Vertical(id="chat_container"):
            yield Static("💬 Asistente Conversacional", id="chat_title", classes="chat-title")
            yield RichLog(id="chat_log", highlight=True, markup=True, classes="chat-log")
            
            with Horizontal(id="chat_input_container", classes="chat-input"):
                yield Input(
                    placeholder="Escribe tu mensaje aquí... (ej: 'busca información sobre Python')",
                    id="chat_input",
                    classes="chat-input-field"
                )
                yield Button("Enviar", id="send_button", variant="primary", classes="send-button")
            
            with Horizontal(id="chat_actions", classes="chat-actions"):
                yield Button("Limpiar", id="clear_button", variant="default", classes="action-button")
                yield Button("Ayuda", id="help_button", variant="default", classes="action-button")
                yield Button("Estado", id="status_button", variant="default", classes="action-button")

    def on_mount(self) -> None:
        """Initialize chat when mounted"""
        self._add_system_message("¡Hola! Soy tu asistente de web scraping. Puedes hablarme de forma natural.")
        self._add_system_message("Ejemplos: 'busca información sobre APIs REST', 'extrae datos de esta URL', 'crea un bot para monitorear precios'")
        
        # Focus on input
        self.query_one("#chat_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "send_button":
            self._handle_send_message()
        elif event.button.id == "clear_button":
            self._handle_clear_chat()
        elif event.button.id == "help_button":
            self._handle_help_request()
        elif event.button.id == "status_button":
            self._handle_status_request()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)"""
        if event.input.id == "chat_input":
            self._handle_send_message()

    def on_key(self, event: Key) -> None:
        """Handle key events"""
        if event.key == "ctrl+c" and self.is_processing:
            self._handle_cancel_operation()

    def _handle_send_message(self) -> None:
        """Handle sending a chat message"""
        if self.is_processing:
            return
        
        chat_input = self.query_one("#chat_input", Input)
        message_text = chat_input.value.strip()
        
        if not message_text:
            return
        
        # Clear input
        chat_input.value = ""
        
        # Add user message to chat
        self._add_user_message(message_text)
        
        # Process message asynchronously
        self.run_worker(
            self._process_message_worker(message_text),
            name=f"chat_message_{self.message_count}"
        )

    async def _process_message_worker(self, message_text: str) -> None:
        """Worker to process chat message"""
        self.is_processing = True
        self._update_input_state(disabled=True, placeholder="Procesando...")
        
        try:
            # Add typing indicator
            typing_message_id = self._add_typing_indicator()
            
            # Process with conversational AI
            response = await self.conversation_ai.process_message(
                message_text, 
                self.session_id
            )
            
            # Remove typing indicator
            self._remove_typing_indicator(typing_message_id)
            
            # Add AI response
            self._add_ai_message(response.get('text', 'No response'))
            
            # Execute commands if any
            commands = response.get('commands', [])
            if commands:
                await self._execute_commands(commands)
                
        except Exception as e:
            logger.error(f"Error processing chat message: {e}", exc_info=True)
            self._add_error_message(f"Error: {str(e)}")
            
        finally:
            self.is_processing = False
            self._update_input_state(disabled=False, placeholder="Escribe tu mensaje aquí...")

    async def _execute_commands(self, commands: List[Dict[str, Any]]) -> None:
        """Execute commands from AI response"""
        if not commands:
            return
        
        self._add_system_message(f"Ejecutando {len(commands)} comando(s)...")
        
        try:
            results = await self.command_processor.execute_commands(commands, self.session_id)
            
            for result in results:
                status = result.get('status', 'unknown')
                command_type = result.get('command', {}).get('type', 'unknown')
                
                if status == 'success':
                    result_data = result.get('result', {})
                    self._add_success_message(f"✅ {command_type}: {result_data.get('status', 'Completado')}")
                    
                    # Show specific results
                    if 'bot_id' in result_data:
                        self._add_info_message(f"🤖 Bot creado: {result_data['bot_id']}")
                    
                    if 'urls' in result_data:
                        self._add_info_message(f"🔗 URLs procesadas: {len(result_data['urls'])}")
                        
                else:
                    error_msg = result.get('error', 'Unknown error')
                    self._add_error_message(f"❌ {command_type}: {error_msg}")
                    
        except Exception as e:
            logger.error(f"Error executing commands: {e}")
            self._add_error_message(f"Error ejecutando comandos: {str(e)}")

    def _handle_clear_chat(self) -> None:
        """Clear chat history"""
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.clear()
        self.message_count = 0
        self._add_system_message("Chat limpiado. ¿En qué puedo ayudarte?")

    def _handle_help_request(self) -> None:
        """Handle help button"""
        self.run_worker(self._process_message_worker("ayuda"), name="help_request")

    def _handle_status_request(self) -> None:
        """Handle status button"""
        self.run_worker(self._process_message_worker("estado"), name="status_request")

    def _handle_cancel_operation(self) -> None:
        """Handle operation cancellation"""
        if self.is_processing:
            self._add_warning_message("⚠️ Operación cancelada por el usuario")
            # Note: Actual cancellation would need to be implemented in the worker management

    def _add_user_message(self, text: str) -> None:
        """Add user message to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"[bold blue]👤 Usuario ({timestamp}):[/] {text}")
        self.message_count += 1

    def _add_ai_message(self, text: str) -> None:
        """Add AI message to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"[bold green]🤖 Asistente ({timestamp}):[/] {text}")

    def _add_system_message(self, text: str) -> None:
        """Add system message to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"[dim]💻 Sistema ({timestamp}): {text}[/]")

    def _add_success_message(self, text: str) -> None:
        """Add success message to chat"""
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"[bold green]{text}[/]")

    def _add_error_message(self, text: str) -> None:
        """Add error message to chat"""
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"[bold red]{text}[/]")

    def _add_warning_message(self, text: str) -> None:
        """Add warning message to chat"""
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"[bold yellow]{text}[/]")

    def _add_info_message(self, text: str) -> None:
        """Add info message to chat"""
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"[cyan]{text}[/]")

    def _add_typing_indicator(self) -> str:
        """Add typing indicator and return its ID"""
        typing_id = f"typing_{self.message_count}"
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"[dim italic]🤖 Asistente está escribiendo...[/]")
        return typing_id

    def _remove_typing_indicator(self, typing_id: str) -> None:
        """Remove typing indicator (simplified - would need log line management for real removal)"""
        # In a full implementation, you'd need to track and remove specific lines
        pass

    def _update_input_state(self, disabled: bool, placeholder: str) -> None:
        """Update input field state"""
        chat_input = self.query_one("#chat_input", Input)
        chat_input.disabled = disabled
        chat_input.placeholder = placeholder
        
        send_button = self.query_one("#send_button", Button)
        send_button.disabled = disabled

    def add_external_message(self, message: str, message_type: str = "info") -> None:
        """Add message from external source (e.g., bot notifications)"""
        if message_type == "error":
            self._add_error_message(message)
        elif message_type == "warning":
            self._add_warning_message(message)
        elif message_type == "success":
            self._add_success_message(message)
        else:
            self._add_info_message(message)

    async def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return await self.conversation_ai.get_conversation_history(self.session_id)

    async def clear_conversation_context(self) -> None:
        """Clear conversation context"""
        await self.conversation_ai.clear_context(self.session_id)
        self._add_system_message("Contexto de conversación reiniciado.")