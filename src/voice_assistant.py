"""
Sistema de Asistente de Voz Inteligente
Integra síntesis de voz, reconocimiento de voz y chat inteligente
"""

import logging
import threading
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import json

# Manejo de dependencias opcionales
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logging.warning("pyttsx3 no disponible - síntesis de voz deshabilitada")

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False
    logging.warning("speechrecognition no disponible - reconocimiento de voz deshabilitado")

logger = logging.getLogger(__name__)

class VoiceEngine:
    """Motor de síntesis de voz"""

    def __init__(self):
        self.enabled = TTS_AVAILABLE
        self.engine = None
        self.speaking = False

        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                self._configure_voice()
                logger.info("🎤 Motor de voz inicializado")
            except Exception as e:
                logger.error(f"Error inicializando motor de voz: {e}")
                self.enabled = False

    def _configure_voice(self):
        """Configura la voz del motor TTS"""
        if not self.engine:
            return

        # Configurar velocidad
        self.engine.setProperty('rate', 180)  # Palabras por minuto

        # Configurar volumen
        self.engine.setProperty('volume', 0.9)

        # Intentar configurar voz en español
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text: str, blocking: bool = False) -> bool:
        """Sintetiza texto a voz"""
        if not self.enabled or not text.strip():
            return False

        try:
            if blocking:
                self.speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.speaking = False
            else:
                # Modo no bloqueante
                threading.Thread(
                    target=self._speak_async,
                    args=(text,),
                    daemon=True
                ).start()
            return True
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            return False

    def _speak_async(self, text: str):
        """Síntesis de voz asíncrona"""
        try:
            self.speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.speaking = False
        except Exception as e:
            logger.error(f"Error en síntesis asíncrona: {e}")
            self.speaking = False

    def is_speaking(self) -> bool:
        """Verifica si está hablando actualmente"""
        return self.speaking

    def stop(self):
        """Detiene la síntesis de voz"""
        if self.engine:
            try:
                self.engine.stop()
                self.speaking = False
            except:
                pass

class SpeechRecognizer:
    """Motor de reconocimiento de voz"""

    def __init__(self):
        self.enabled = STT_AVAILABLE
        self.recognizer = None
        self.microphone = None
        self.listening = False

        if self.enabled:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()

                # Calibrar ruido ambiente
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)

                logger.info("🎧 Reconocedor de voz inicializado")
            except Exception as e:
                logger.error(f"Error inicializando reconocedor: {e}")
                self.enabled = False

    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Escucha y reconoce una frase"""
        if not self.enabled:
            return None

        try:
            with self.microphone as source:
                logger.info("🎧 Escuchando...")
                self.listening = True

                # Escuchar audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                self.listening = False

                # Reconocer usando Google
                text = self.recognizer.recognize_google(audio, language='es-ES')
                logger.info(f"🎧 Reconocido: {text}")
                return text.strip()

        except sr.WaitTimeoutError:
            logger.warning("🎧 Timeout - no se detectó voz")
            self.listening = False
            return None
        except sr.UnknownValueError:
            logger.warning("🎧 No se pudo entender el audio")
            self.listening = False
            return None
        except sr.RequestError as e:
            logger.error(f"🎧 Error del servicio de reconocimiento: {e}")
            self.listening = False
            return None
        except Exception as e:
            logger.error(f"🎧 Error inesperado: {e}")
            self.listening = False
            return None

    def is_listening(self) -> bool:
        """Verifica si está escuchando actualmente"""
        return self.listening

class IntelligentChat:
    """Sistema de chat inteligente con el cerebro híbrido"""

    def __init__(self, brain_instance=None):
        self.brain = brain_instance
        self.conversation_history: List[Dict[str, Any]] = []
        self.active = False

    def process_message(self, message: str, user_id: str = "user") -> Dict[str, Any]:
        """Procesa un mensaje y genera respuesta inteligente"""

        # Registrar mensaje en historial
        user_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'user_message',
            'user_id': user_id,
            'content': message,
            'processed': False
        }

        self.conversation_history.append(user_entry)

        # Procesar con el cerebro híbrido si está disponible
        brain_response = self._process_with_brain(message, user_entry)

        # Generar respuesta
        response = self._generate_response(message, brain_response)

        # Registrar respuesta
        assistant_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'assistant_response',
            'content': response['text'],
            'confidence': response.get('confidence', 0.8),
            'brain_analysis': brain_response,
            'actions_taken': response.get('actions', [])
        }

        self.conversation_history.append(assistant_entry)

        # Marcar mensaje como procesado
        user_entry['processed'] = True

        return response

    def _process_with_brain(self, message: str, user_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa el mensaje con el cerebro híbrido"""
        if not self.brain:
            return {'status': 'no_brain', 'analysis': 'Cerebro no disponible'}

        try:
            # Analizar el mensaje usando las capacidades del cerebro
            analysis = self.brain.process_user_interaction({
                'type': 'chat_message',
                'content': message,
                'user_entry': user_entry,
                'context': 'voice_chat',
                'importance': 0.8,
                'requires_response': True
            })

            return analysis

        except Exception as e:
            logger.error(f"Error procesando con cerebro: {e}")
            return {'status': 'error', 'error': str(e)}

    def _generate_response(self, message: str, brain_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera respuesta basada en el análisis del cerebro"""

        # Análisis básico del mensaje
        message_lower = message.lower()

        # Detectar comandos especiales
        if any(word in message_lower for word in ['buscar', 'busca', 'investiga', 'información sobre']):
            return self._handle_search_request(message, brain_analysis)

        elif any(word in message_lower for word in ['crear', 'generar', 'documento', 'archivo']):
            return self._handle_document_request(message, brain_analysis)

        elif any(word in message_lower for word in ['hola', 'saludo', 'qué tal', 'buenos días']):
            return {
                'text': "¡Hola! Soy tu asistente inteligente de Web Scraper PRO. Puedo ayudarte a buscar información, crear documentos, o responder preguntas. ¿En qué puedo ayudarte?",
                'confidence': 0.9,
                'actions': []
            }

        elif any(word in message_lower for word in ['ayuda', 'help', 'qué puedes hacer']):
            return {
                'text': """Puedo ayudarte con varias tareas:

🔍 Búsqueda inteligente: "Busca información sobre inteligencia artificial"
📄 Crear documentos: "Crea un documento Word sobre bots"
📊 Generar reportes: "Genera un Excel con datos de scraping"
🎤 Chat por voz: Habla conmigo directamente
🧠 Análisis inteligente: Uso mi cerebro híbrido para mejores respuestas

¿Qué te gustaría hacer?""",
                'confidence': 0.95,
                'actions': ['show_capabilities']
            }

        else:
            # Respuesta general usando análisis del cerebro
            brain_insight = brain_analysis.get('analysis', {})
            confidence = brain_insight.get('confidence', 0.7)

            if confidence > 0.8:
                response_text = f"Entiendo tu consulta sobre '{message}'. Según mi análisis, puedo ayudarte con esto."
            else:
                response_text = f"He analizado tu mensaje: '{message}'. ¿Podrías ser más específico sobre lo que necesitas?"

            return {
                'text': response_text,
                'confidence': confidence,
                'actions': [],
                'brain_analysis': brain_analysis
            }

    def _handle_search_request(self, message: str, brain_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja solicitudes de búsqueda"""
        # Extraer tema de búsqueda
        search_terms = self._extract_search_terms(message)

        return {
            'text': f"Perfecto! Voy a buscar información sobre: {', '.join(search_terms)}. Iniciaré una búsqueda inteligente y crearé un documento con los resultados.",
            'confidence': 0.9,
            'actions': ['intelligent_search'],
            'search_terms': search_terms
        }

    def _handle_document_request(self, message: str, brain_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja solicitudes de creación de documentos"""
        doc_type = self._detect_document_type(message)
        topic = self._extract_document_topic(message)

        return {
            'text': f"Entendido! Voy a crear un {doc_type} sobre '{topic}'. Recopilaré información relevante y generaré el documento.",
            'confidence': 0.85,
            'actions': ['create_document'],
            'document_type': doc_type,
            'topic': topic
        }

    def _extract_search_terms(self, message: str) -> List[str]:
        """Extrae términos de búsqueda del mensaje"""
        # Implementación básica - mejorar con NLP
        keywords = ['buscar', 'busca', 'información', 'sobre', 'acerca', 'de']
        words = message.lower().split()

        # Filtrar palabras de comando
        search_words = [w for w in words if w not in keywords and len(w) > 2]

        return search_words if search_words else ['tema general']

    def _detect_document_type(self, message: str) -> str:
        """Detecta el tipo de documento solicitado"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['word', 'documento', 'doc']):
            return 'documento Word'
        elif any(word in message_lower for word in ['excel', 'hoja de cálculo', 'spreadsheet']):
            return 'hoja de cálculo'
        elif any(word in message_lower for word in ['powerpoint', 'presentación', 'slides']):
            return 'presentación'
        elif any(word in message_lower for word in ['pdf']):
            return 'documento PDF'
        else:
            return 'documento'

    def _extract_document_topic(self, message: str) -> str:
        """Extrae el tema del documento del mensaje"""
        # Implementación básica
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() in ['sobre', 'acerca', 'de'] and i + 1 < len(words):
                return ' '.join(words[i+1:])

        return 'tema general'

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de la conversación"""
        if not self.conversation_history:
            return {'messages': 0, 'topics': [], 'summary': 'Sin conversación'}

        user_messages = [m for m in self.conversation_history if m['type'] == 'user_message']
        assistant_messages = [m for m in self.conversation_history if m['type'] == 'assistant_response']

        return {
            'total_messages': len(self.conversation_history),
            'user_messages': len(user_messages),
            'assistant_responses': len(assistant_messages),
            'duration_minutes': self._calculate_conversation_duration(),
            'topics_discussed': self._extract_conversation_topics(),
            'avg_confidence': self._calculate_avg_confidence()
        }

    def _calculate_conversation_duration(self) -> float:
        """Calcula duración de la conversación en minutos"""
        if len(self.conversation_history) < 2:
            return 0.0

        start_time = datetime.fromisoformat(self.conversation_history[0]['timestamp'])
        end_time = datetime.fromisoformat(self.conversation_history[-1]['timestamp'])

        return (end_time - start_time).total_seconds() / 60.0

    def _extract_conversation_topics(self) -> List[str]:
        """Extrae temas principales de la conversación"""
        # Implementación básica - mejorar con NLP
        topics = set()

        for entry in self.conversation_history:
            if entry['type'] == 'user_message':
                content = entry['content'].lower()
                # Palabras clave simples
                if 'bot' in content:
                    topics.add('bots')
                if 'documento' in content:
                    topics.add('documentos')
                if 'buscar' in content:
                    topics.add('búsquedas')

        return list(topics)

    def _calculate_avg_confidence(self) -> float:
        """Calcula confianza promedio de respuestas"""
        responses = [m for m in self.conversation_history if m['type'] == 'assistant_response']
        if not responses:
            return 0.0

        confidences = [r.get('confidence', 0.5) for r in responses]
        return sum(confidences) / len(confidences)

class VoiceAssistant:
    """Asistente de voz principal que integra todos los componentes"""

    def __init__(self, brain_instance=None):
        self.voice_engine = VoiceEngine()
        self.speech_recognizer = SpeechRecognizer()
        self.chat = IntelligentChat(brain_instance)

        self.active = False
        self.listening_mode = False
        self.conversation_active = False

        # Configuración
        self.config = {
            'voice_enabled': self.voice_engine.enabled,
            'speech_recognition_enabled': self.speech_recognizer.enabled,
            'auto_speak_responses': True,
            'listen_timeout': 10,
            'conversation_timeout': 300  # 5 minutos
        }

        logger.info(f"🤖 Asistente de voz inicializado - TTS: {self.voice_engine.enabled}, STT: {self.speech_recognizer.enabled}")

    def start_voice_conversation(self) -> bool:
        """Inicia conversación por voz"""
        if not self.speech_recognizer.enabled:
            self.speak("Lo siento, el reconocimiento de voz no está disponible.")
            return False

        self.conversation_active = True
        self.speak("¡Hola! Soy tu asistente inteligente. Puedes hablar conmigo. Di 'salir' para terminar.")

        try:
            while self.conversation_active:
                # Escuchar comando de voz
                user_speech = self.speech_recognizer.listen_once(timeout=self.config['listen_timeout'])

                if user_speech is None:
                    self.speak("No escuché nada. ¿Podrías repetir?")
                    continue

                # Comando de salida
                if any(word in user_speech.lower() for word in ['salir', 'terminar', 'adiós', 'chao']):
                    self.speak("¡Hasta luego! Ha sido un placer ayudarte.")
                    break

                # Procesar mensaje
                response = self.chat.process_message(user_speech)

                # Responder por voz
                if self.config['auto_speak_responses']:
                    self.speak(response['text'])

                # Ejecutar acciones si las hay
                self._execute_actions(response.get('actions', []), response)

        except KeyboardInterrupt:
            self.speak("Conversación interrumpida. ¡Hasta luego!")
        finally:
            self.conversation_active = False

        return True

    def start_text_conversation(self) -> bool:
        """Inicia conversación por texto"""
        self.conversation_active = True
        print("\n🤖 Asistente inteligente activado. Escribe 'salir' para terminar.\n")

        try:
            while self.conversation_active:
                user_input = input("Tú: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['salir', 'exit', 'quit', 'adiós']:
                    print("🤖 ¡Hasta luego! Ha sido un placer ayudarte.")
                    break

                # Procesar mensaje
                response = self.chat.process_message(user_input)

                print(f"🤖 Asistente: {response['text']}\n")

                # Opcional: hablar la respuesta
                if self.config['auto_speak_responses'] and self.voice_engine.enabled:
                    self.speak(response['text'])

                # Ejecutar acciones
                self._execute_actions(response.get('actions', []), response)

        except KeyboardInterrupt:
            print("\n🤖 Conversación interrumpida. ¡Hasta luego!")
        finally:
            self.conversation_active = False

        return True

    def _execute_actions(self, actions: List[str], response_data: Dict[str, Any]):
        """Ejecuta acciones solicitadas"""
        for action in actions:
            try:
                if action == 'intelligent_search':
                    self._perform_intelligent_search(response_data)
                elif action == 'create_document':
                    self._create_document(response_data)
                elif action == 'show_capabilities':
                    self._show_capabilities()
                else:
                    logger.warning(f"Acción desconocida: {action}")
            except Exception as e:
                logger.error(f"Error ejecutando acción {action}: {e}")
                self.speak(f"Hubo un error ejecutando la acción: {action}")

    def _perform_intelligent_search(self, response_data: Dict[str, Any]):
        """Realiza búsqueda inteligente"""
        search_terms = response_data.get('search_terms', ['información general'])

        # Placeholder - implementar búsqueda real
        self.speak(f"Iniciando búsqueda inteligente para: {', '.join(search_terms)}")
        logger.info(f"🔍 Búsqueda inteligente solicitada: {search_terms}")

        # TODO: Integrar con el sistema de scraping para búsqueda real

    def _create_document(self, response_data: Dict[str, Any]):
        """Crea documento solicitado"""
        doc_type = response_data.get('document_type', 'documento')
        topic = response_data.get('topic', 'tema general')

        self.speak(f"Iniciando creación de {doc_type} sobre {topic}")
        logger.info(f"📄 Creación de documento solicitada: {doc_type} - {topic}")

        # TODO: Integrar con sistema de generación de documentos

    def _show_capabilities(self):
        """Muestra capacidades del asistente"""
        print("\n" + "="*60)
        print("🤖 CAPACIDADES DEL ASISTENTE INTELIGENTE")
        print("="*60)
        print("🎤 Reconocimiento de voz:", "✅" if self.speech_recognizer.enabled else "❌")
        print("🔊 Síntesis de voz:", "✅" if self.voice_engine.enabled else "❌")
        print("🧠 Cerebro híbrido:", "✅" if self.chat.brain else "❌")
        print("\n📋 COMANDOS DISPONIBLES:")
        print("• 'Busca información sobre [tema]' - Búsqueda inteligente")
        print("• 'Crea un documento sobre [tema]' - Generación de documentos")
        print("• 'Ayuda' - Mostrar esta información")
        print("• 'Salir' - Terminar conversación")
        print("="*60 + "\n")

    def speak(self, text: str, blocking: bool = False) -> bool:
        """Síntesis de voz con logging"""
        logger.info(f"🔊 Hablando: {text[:50]}...")
        return self.voice_engine.speak(text, blocking)

    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del asistente"""
        return {
            'voice_synthesis': self.voice_engine.enabled,
            'speech_recognition': self.speech_recognizer.enabled,
            'conversation_active': self.conversation_active,
            'is_speaking': self.voice_engine.is_speaking(),
            'is_listening': self.speech_recognizer.is_listening(),
            'conversation_stats': self.chat.get_conversation_summary(),
            'config': self.config
        }

    def shutdown(self):
        """Apaga el asistente"""
        self.conversation_active = False
        self.voice_engine.stop()
        logger.info("🤖 Asistente de voz apagado")

# Función de utilidad para crear asistente
def create_voice_assistant(brain_instance=None) -> VoiceAssistant:
    """Crea una instancia del asistente de voz"""
    return VoiceAssistant(brain_instance)

# Función principal para demostración
def main():
    """Función principal para demostración"""
    print("🤖 Iniciando Asistente de Voz Inteligente...")

    assistant = create_voice_assistant()

    print("\nSelecciona modo de conversación:")
    print("1. Conversación por voz")
    print("2. Conversación por texto")

    choice = input("Opción (1 o 2): ").strip()

    if choice == "1":
        assistant.start_voice_conversation()
    else:
        assistant.start_text_conversation()

    # Mostrar estadísticas finales
    stats = assistant.get_status()
    print(f"\n📊 Estadísticas de la conversación:")
    print(f"Mensajes totales: {stats['conversation_stats']['total_messages']}")
    print(f"Duración: {stats['conversation_stats']['duration_minutes']:.1f} minutos")

    assistant.shutdown()

if __name__ == "__main__":
    main()
