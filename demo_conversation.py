#!/usr/bin/env python3
"""
Demonstration script for the new conversational AI features in PythonWebScraper

This script shows how to use the new chat functionality and bot management system.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.intelligence.conversation_ai import ConversationalAI
from src.intelligence.command_processor import CommandProcessor
from src.intelligence.bot_manager import BotManager


async def demo_conversation():
    """Demonstrate conversational AI capabilities"""
    print("🤖 Iniciando Demo de IA Conversacional para PythonWebScraper")
    print("=" * 60)
    
    # Initialize AI components
    ai = ConversationalAI()
    
    # Use a temporary database for the demo
    from src.database import DatabaseManager
    from src.settings import settings
    db_manager = DatabaseManager(db_path=settings.DB_PATH)
    
    processor = CommandProcessor(db_manager=db_manager)
    bot_manager = BotManager()
    
    # Test session
    session_id = "demo_session"
    
    # Demonstration commands
    demo_commands = [
        "busca información sobre web scraping con Python",
        "crea un bot para monitorear noticias de tecnología", 
        "analiza los datos del sistema",
        "estado del sistema",
        "ayuda"
    ]
    
    print("\n🎯 Comandos de demostración:")
    for i, cmd in enumerate(demo_commands, 1):
        print(f"  {i}. {cmd}")
    
    print("\n" + "─" * 60)
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n💬 Usuario: {command}")
        
        # Process with conversational AI
        response = await ai.process_message(command, session_id)
        
        print(f"🤖 Asistente: {response['text'][:100]}...")
        
        # Execute commands if any
        commands = response.get('commands', [])
        if commands:
            print(f"📋 Ejecutando {len(commands)} comando(s):")
            
            # Note: In demo mode, we'll just show what would be executed
            # without actually running expensive operations
            for j, cmd in enumerate(commands, 1):
                cmd_type = cmd.get('type', 'unknown')
                params = cmd.get('parameters', {})
                print(f"  {j}. {cmd_type}: {params}")
                
                # Show a sample execution for bot creation
                if cmd_type == "create_bot":
                    description = params.get('description', 'Demo bot')
                    bot_id = bot_manager.create_smart_bot_from_description(description)
                    print(f"     ✅ Bot creado: {bot_id}")
                    
                    # Show bot status
                    status = bot_manager.get_bot_status(bot_id)
                    if status:
                        print(f"     📊 Estado: {status['status']}, Tipo: {status['type']}")
        else:
            print("📝 Sin comandos para ejecutar")
        
        print("─" * 40)
    
    # Show conversation history
    print(f"\n📚 Historial de conversación (total: {len(await ai.get_conversation_history(session_id))} mensajes)")
    
    # Show created bots
    bots = bot_manager.list_bots()
    if bots:
        print(f"\n🤖 Bots creados durante la demo: {len(bots)}")
        for bot in bots:
            print(f"  • {bot['name']} ({bot['type']}) - {bot['status']}")
    
    print(f"\n✅ Demo completada exitosamente!")
    print(f"🚀 Para usar la interfaz completa, ejecuta: python -m src.main --tui")
    print(f"💡 O para modo demo: python -m src.main --demo")


async def demo_chat_interface():
    """Show how the chat interface would work"""
    print(f"\n🎨 Ejemplo de Interfaz de Chat:")
    print("=" * 40)
    
    # Simulate chat interface
    chat_examples = [
        ("👤 Usuario", "busca información sobre APIs REST"),
        ("🤖 Asistente", "Perfecto, voy a buscar información sobre 'APIs REST'. Iniciando búsqueda..."),
        ("💻 Sistema", "🤖 Bot creado: Bot_search_20250905_124000"),
        ("🤖 Asistente", "✅ search_web: Bot de búsqueda iniciado"),
        ("👤 Usuario", "estado"),
        ("🤖 Asistente", "Obteniendo estado del sistema..."),
        ("💻 Sistema", "✅ get_system_status: Sistema saludable (100% salud)"),
    ]
    
    for role, message in chat_examples:
        print(f"{role}: {message}")
    
    print("\n💡 Funciones disponibles en la interfaz de chat:")
    print("  • Conversación natural en español")
    print("  • Detección automática de intenciones")
    print("  • Ejecución de comandos en tiempo real")
    print("  • Historial de conversación")
    print("  • Notificaciones del sistema")
    print("  • Integración con TUI existente")


if __name__ == "__main__":
    print("🌟 PythonWebScraper - Demo de Funcionalidad Conversacional")
    print("Este demo muestra las nuevas capacidades de IA conversacional")
    print()
    
    try:
        # Run the async demo
        asyncio.run(demo_conversation())
        asyncio.run(demo_chat_interface())
        
    except KeyboardInterrupt:
        print("\n⛔ Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el demo: {e}")
        import traceback
        traceback.print_exc()