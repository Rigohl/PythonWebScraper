"""
Integrador AI Assistant - Módulo que combina voz, búsqueda inteligente y generación de documentos
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Importaciones del proyecto
try:
    from .document_generator import DocumentGenerator
    from .hybrid_brain import HybridBrain
    from .intelligent_search import IntelligentSearchEngine
    from .voice_assistant import VoiceAssistant

    MODULES_AVAILABLE = True
except ImportError:
    # Importaciones alternativas para ejecución directa
    try:
        import sys

        sys.path.append(str(Path(__file__).parent))

        from hybrid_brain import HybridBrain

        from document_generator import DocumentGenerator
        from intelligent_search import IntelligentSearchEngine
        from voice_assistant import VoiceAssistant

        MODULES_AVAILABLE = True
    except ImportError:
        MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIAssistantIntegrator:
    """Integrador principal del asistente AI con todas las capacidades"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.brain = None
        self.voice_assistant = None
        self.search_engine = None
        self.document_generator = None

        # Estado del sistema
        self.system_status = {
            "initialized": False,
            "brain_active": False,
            "voice_active": False,
            "search_active": False,
            "documents_active": False,
            "last_activity": None,
        }

        # Historial de sesiones
        self.session_history: List[Dict[str, Any]] = []

        logger.info("🤖 AI Assistant Integrator inicializado")

    async def initialize_system(self) -> Dict[str, Any]:
        """Inicializa todos los componentes del sistema"""

        initialization_report = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "status": "starting",
            "errors": [],
        }

        try:
            logger.info("🔧 Inicializando componentes del AI Assistant...")

            # 1. Inicializar cerebro híbrido
            try:
                self.brain = HybridBrain()
                await self.brain.activate()
                self.system_status["brain_active"] = True
                initialization_report["components"]["brain"] = "success"
                logger.info("🧠 Cerebro híbrido activado")
            except Exception as e:
                error_msg = f"Error inicializando cerebro: {e}"
                logger.error(error_msg)
                initialization_report["components"]["brain"] = "error"
                initialization_report["errors"].append(error_msg)

            # 2. Inicializar motor de búsqueda
            try:
                self.search_engine = IntelligentSearchEngine(brain_instance=self.brain)
                self.system_status["search_active"] = True
                initialization_report["components"]["search"] = "success"
                logger.info("🔍 Motor de búsqueda inteligente activado")
            except Exception as e:
                error_msg = f"Error inicializando búsqueda: {e}"
                logger.error(error_msg)
                initialization_report["components"]["search"] = "error"
                initialization_report["errors"].append(error_msg)

            # 3. Inicializar generador de documentos
            try:
                self.document_generator = DocumentGenerator(
                    self.config.get("documents", {})
                )
                self.system_status["documents_active"] = True
                initialization_report["components"]["documents"] = "success"
                logger.info("📄 Generador de documentos activado")
            except Exception as e:
                error_msg = f"Error inicializando documentos: {e}"
                logger.error(error_msg)
                initialization_report["components"]["documents"] = "error"
                initialization_report["errors"].append(error_msg)

            # 4. Inicializar asistente de voz
            try:
                self.voice_assistant = VoiceAssistant(
                    brain_instance=self.brain,
                    search_engine=self.search_engine,
                    document_generator=self.document_generator,
                )
                self.system_status["voice_active"] = True
                initialization_report["components"]["voice"] = "success"
                logger.info("🎤 Asistente de voz activado")
            except Exception as e:
                error_msg = f"Error inicializando voz: {e}"
                logger.error(error_msg)
                initialization_report["components"]["voice"] = "error"
                initialization_report["errors"].append(error_msg)

            # Estado final
            active_components = sum(
                1
                for status in initialization_report["components"].values()
                if status == "success"
            )

            if active_components >= 2:  # Al menos 2 componentes activos
                self.system_status["initialized"] = True
                initialization_report["status"] = "success"
                logger.info(
                    f"✅ Sistema inicializado: {active_components}/4 componentes activos"
                )
            else:
                initialization_report["status"] = "partial"
                logger.warning(
                    f"⚠️ Inicialización parcial: {active_components}/4 componentes activos"
                )

            self.system_status["last_activity"] = datetime.now().isoformat()

            return initialization_report

        except Exception as e:
            logger.error(f"Error crítico en inicialización: {e}")
            initialization_report["status"] = "failed"
            initialization_report["errors"].append(f"Error crítico: {e}")
            return initialization_report

    async def process_user_request(
        self, request: str, interaction_mode: str = "text"
    ) -> Dict[str, Any]:
        """Procesa solicitud del usuario usando todos los componentes disponibles"""

        session = {
            "session_id": f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "request": request,
            "interaction_mode": interaction_mode,
            "timestamp": datetime.now().isoformat(),
            "status": "processing",
            "components_used": [],
            "results": {},
        }

        try:
            logger.info(
                f"🤖 Procesando solicitud ({interaction_mode}): {request[:100]}..."
            )

            # Análisis de intención con el cerebro
            if self.brain and self.system_status["brain_active"]:
                intention_analysis = await self._analyze_user_intention(request)
                session["intention_analysis"] = intention_analysis
                session["components_used"].append("brain")

                # Determinar acciones basadas en la intención
                actions = self._determine_actions(intention_analysis)
                session["planned_actions"] = actions
            else:
                # Análisis simple sin cerebro
                actions = self._simple_intention_analysis(request)
                session["planned_actions"] = actions

            # Ejecutar acciones determinadas
            for action in actions:
                try:
                    if action["type"] == "search":
                        result = await self._execute_search_action(action, request)
                        session["results"]["search"] = result
                        session["components_used"].append("search")

                    elif action["type"] == "document_generation":
                        # Requiere datos de búsqueda previa
                        search_data = session["results"].get("search")
                        if search_data:
                            result = await self._execute_document_action(
                                action, search_data
                            )
                            session["results"]["document"] = result
                            session["components_used"].append("documents")

                    elif action["type"] == "voice_response":
                        result = await self._execute_voice_action(
                            action, session["results"]
                        )
                        session["results"]["voice"] = result
                        session["components_used"].append("voice")

                    elif action["type"] == "analysis":
                        result = await self._execute_analysis_action(action, request)
                        session["results"]["analysis"] = result
                        session["components_used"].append("brain")

                except Exception as e:
                    logger.error(f"Error ejecutando acción {action['type']}: {e}")
                    session["results"][action["type"]] = {
                        "status": "error",
                        "error": str(e),
                    }

            # Generar respuesta final
            final_response = await self._generate_final_response(session)
            session["final_response"] = final_response
            session["status"] = "completed"

            # Guardar en historial
            self.session_history.append(session)
            self.system_status["last_activity"] = datetime.now().isoformat()

            logger.info(
                f"✅ Solicitud procesada usando: {', '.join(session['components_used'])}"
            )

            return session

        except Exception as e:
            logger.error(f"Error procesando solicitud: {e}")
            session["status"] = "error"
            session["error"] = str(e)
            return session

    async def _analyze_user_intention(self, request: str) -> Dict[str, Any]:
        """Analiza la intención del usuario usando el cerebro"""

        analysis_query = {
            "type": "intention_analysis",
            "content": request,
            "context": "ai_assistant_request",
            "available_capabilities": [
                "intelligent_search",
                "document_generation",
                "voice_interaction",
                "data_analysis",
            ],
        }

        brain_response = self.brain.process_intelligent_query(analysis_query)

        # Extraer intenciones
        intentions = {
            "primary_intent": "search",  # Por defecto
            "search_required": True,
            "document_generation": False,
            "voice_response": False,
            "analysis_type": "general",
            "confidence": brain_response.get("confidence", 0.7),
            "keywords": self._extract_keywords(request),
        }

        # Análisis de patrones en la solicitud
        request_lower = request.lower()

        if any(
            word in request_lower
            for word in ["busca", "encuentra", "información", "datos"]
        ):
            intentions["primary_intent"] = "search"
            intentions["search_required"] = True

        if any(
            word in request_lower
            for word in ["documento", "informe", "reporte", "generar", "crear"]
        ):
            intentions["document_generation"] = True

        if any(
            word in request_lower for word in ["lee", "dime", "habla", "voz", "audio"]
        ):
            intentions["voice_response"] = True

        if any(
            word in request_lower
            for word in ["analiza", "compara", "evalúa", "estudia"]
        ):
            intentions["analysis_type"] = "detailed"

        return intentions

    def _simple_intention_analysis(self, request: str) -> List[Dict[str, Any]]:
        """Análisis simple de intención sin cerebro"""

        actions = []
        request_lower = request.lower()

        # Siempre incluir búsqueda por defecto
        actions.append(
            {
                "type": "search",
                "priority": 1,
                "params": {"topic": request, "max_results": 5},
            }
        )

        # Determinar si generar documento
        if any(
            word in request_lower
            for word in ["documento", "informe", "reporte", "generar"]
        ):
            actions.append(
                {
                    "type": "document_generation",
                    "priority": 2,
                    "params": {"format_types": ["md", "docx"]},
                }
            )

        return actions

    def _determine_actions(
        self, intention_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Determina acciones a ejecutar basado en análisis de intención"""

        actions = []

        # Acción de búsqueda
        if intention_analysis.get("search_required", True):
            search_action = {
                "type": "search",
                "priority": 1,
                "params": {
                    "max_results": (
                        8
                        if intention_analysis.get("analysis_type") == "detailed"
                        else 5
                    ),
                    "content_types": ["definition", "examples", "tutorial"],
                },
            }
            actions.append(search_action)

        # Acción de generación de documentos
        if intention_analysis.get("document_generation", False):
            doc_action = {
                "type": "document_generation",
                "priority": 2,
                "params": {
                    "document_type": (
                        "research_report"
                        if intention_analysis.get("analysis_type") == "detailed"
                        else "summary"
                    ),
                    "format_types": ["md", "docx"],
                },
            }
            actions.append(doc_action)

        # Acción de respuesta por voz
        if intention_analysis.get("voice_response", False):
            voice_action = {
                "type": "voice_response",
                "priority": 3,
                "params": {"include_summary": True},
            }
            actions.append(voice_action)

        # Ordenar por prioridad
        actions.sort(key=lambda x: x["priority"])

        return actions

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave del texto"""

        # Palabras a ignorar
        stop_words = {
            "el",
            "la",
            "de",
            "que",
            "y",
            "en",
            "un",
            "es",
            "se",
            "no",
            "te",
            "lo",
            "le",
            "da",
            "su",
            "por",
            "son",
            "con",
            "para",
            "al",
            "del",
            "los",
            "las",
            "una",
            "sobre",
            "como",
            "más",
            "pero",
            "sus",
            "me",
            "hasta",
            "hay",
            "donde",
            "busca",
            "encuentra",
            "dime",
            "información",
            "datos",
        }

        words = text.lower().split()
        keywords = [
            word.strip(".,!?:;")
            for word in words
            if len(word) > 3 and word not in stop_words
        ]

        return list(set(keywords))[:10]  # Máximo 10 keywords únicos

    async def _execute_search_action(
        self, action: Dict[str, Any], request: str
    ) -> Dict[str, Any]:
        """Ejecuta acción de búsqueda"""

        if not self.search_engine or not self.system_status["search_active"]:
            return {"status": "unavailable", "reason": "Search engine not active"}

        search_params = action["params"].copy()

        # Extraer tema de la solicitud
        topic = request
        if len(topic) > 100:
            topic = topic[:100] + "..."

        try:
            search_result = await self.search_engine.intelligent_search(
                topic=topic,
                max_results=search_params.get("max_results", 5),
                content_types=search_params.get(
                    "content_types", ["definition", "examples"]
                ),
            )

            return search_result

        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return {"status": "error", "error": str(e)}

    async def _execute_document_action(
        self, action: Dict[str, Any], search_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta acción de generación de documentos"""

        if not self.document_generator or not self.system_status["documents_active"]:
            return {"status": "unavailable", "reason": "Document generator not active"}

        doc_params = action["params"].copy()

        try:
            generation_result = (
                await self.document_generator.generate_comprehensive_document(
                    search_data=search_data,
                    document_type=doc_params.get("document_type", "research_report"),
                    format_types=doc_params.get("format_types", ["md"]),
                )
            )

            return generation_result

        except Exception as e:
            logger.error(f"Error generando documento: {e}")
            return {"status": "error", "error": str(e)}

    async def _execute_voice_action(
        self, action: Dict[str, Any], results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta acción de respuesta por voz"""

        if not self.voice_assistant or not self.system_status["voice_active"]:
            return {"status": "unavailable", "reason": "Voice assistant not active"}

        try:
            # Preparar contenido para síntesis de voz
            content_to_speak = ""

            # Incluir resumen de búsqueda si está disponible
            if "search" in results and results["search"].get("status") == "completed":
                synthesis = results["search"].get("synthesis", {})
                content_to_speak = synthesis.get("summary", "")

            # Generar respuesta por voz
            if content_to_speak:
                voice_response = await self.voice_assistant.speak_content(
                    content_to_speak
                )
                return voice_response
            else:
                return {
                    "status": "no_content",
                    "message": "No hay contenido para sintetizar",
                }

        except Exception as e:
            logger.error(f"Error en respuesta de voz: {e}")
            return {"status": "error", "error": str(e)}

    async def _execute_analysis_action(
        self, action: Dict[str, Any], request: str
    ) -> Dict[str, Any]:
        """Ejecuta acción de análisis con el cerebro"""

        if not self.brain or not self.system_status["brain_active"]:
            return {"status": "unavailable", "reason": "Brain not active"}

        try:
            analysis_query = {
                "type": "detailed_analysis",
                "content": request,
                "context": "user_request_analysis",
            }

            analysis_result = self.brain.process_intelligent_query(analysis_query)

            return {
                "status": "completed",
                "analysis": analysis_result,
                "insights": analysis_result.get("insights", []),
                "confidence": analysis_result.get("confidence", 0.7),
            }

        except Exception as e:
            logger.error(f"Error en análisis: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_final_response(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Genera respuesta final consolidada"""

        response = {
            "session_id": session["session_id"],
            "timestamp": datetime.now().isoformat(),
            "summary": "",
            "components_used": session["components_used"],
            "artifacts_generated": [],
            "recommendations": [],
        }

        results = session.get("results", {})

        # Consolidar información de búsqueda
        if "search" in results and results["search"].get("status") == "completed":
            search_data = results["search"]
            synthesis = search_data.get("synthesis", {})

            response["summary"] = synthesis.get("summary", "Búsqueda completada")
            response["search_quality"] = synthesis.get("content_quality", 0.0)
            response["sources_consulted"] = synthesis.get("sources_count", 0)

        # Información de documentos generados
        if "document" in results and results["document"].get("status") == "completed":
            doc_data = results["document"]
            generated_files = doc_data.get("generated_files", [])

            for file_info in generated_files:
                if file_info.get("status") == "success":
                    response["artifacts_generated"].append(
                        {
                            "type": "document",
                            "format": file_info["format"],
                            "location": file_info.get(
                                "path", file_info.get("url", "Unknown")
                            ),
                        }
                    )

        # Recomendaciones basadas en resultados
        if response["sources_consulted"] > 5:
            response["recommendations"].append(
                "Los datos recopilados son suficientes para análisis profundo"
            )

        if "document" in results:
            response["recommendations"].append(
                "Documentos generados están listos para revisión"
            )

        if "voice" in session["components_used"]:
            response["recommendations"].append("Respuesta por voz disponible")

        return response

    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del sistema"""
        return self.system_status.copy()

    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene historial de sesiones"""
        return self.session_history[-limit:] if limit > 0 else self.session_history

    async def execute_voice_conversation(self) -> Dict[str, Any]:
        """Ejecuta conversación por voz interactiva"""

        if not self.voice_assistant or not self.system_status["voice_active"]:
            return {"status": "unavailable", "reason": "Voice assistant not available"}

        try:
            # Iniciar conversación por voz
            conversation_result = await self.voice_assistant.start_conversation()

            # Si se recibió una solicitud por voz, procesarla
            if conversation_result.get("user_input"):
                user_request = conversation_result["user_input"]
                processing_result = await self.process_user_request(
                    user_request, "voice"
                )

                # Responder por voz
                if processing_result.get("final_response"):
                    summary = processing_result["final_response"].get("summary", "")
                    if summary:
                        await self.voice_assistant.speak_content(summary)

                return {
                    "status": "completed",
                    "conversation": conversation_result,
                    "processing": processing_result,
                }

            return conversation_result

        except Exception as e:
            logger.error(f"Error en conversación por voz: {e}")
            return {"status": "error", "error": str(e)}


# Funciones de utilidad para integración con el sistema principal
def create_ai_assistant(config: Dict[str, Any] = None) -> AIAssistantIntegrator:
    """Crea instancia del asistente AI integrado"""
    return AIAssistantIntegrator(config)


async def quick_ai_request(
    request: str, config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Procesa solicitud rápida con el AI Assistant"""

    assistant = create_ai_assistant(config)

    # Inicializar solo componentes básicos
    await assistant.initialize_system()

    # Procesar solicitud
    return await assistant.process_user_request(request)


# Función principal para demostración
async def main():
    """Función principal para demostración"""
    print("🤖 Iniciando AI Assistant Integrado...")

    # Crear y inicializar asistente
    assistant = create_ai_assistant()

    print("🔧 Inicializando componentes...")
    init_result = await assistant.initialize_system()

    print(f"Estado de inicialización: {init_result['status']}")
    for component, status in init_result["components"].items():
        emoji = "✅" if status == "success" else "❌"
        print(f"{emoji} {component.title()}: {status}")

    if init_result["status"] in ["success", "partial"]:
        print("\n🎯 Sistema listo para recibir solicitudes!")

        # Solicitud de ejemplo
        sample_request = input(
            "\n¿Qué información necesitas? (o presiona Enter para ejemplo): "
        ).strip()

        if not sample_request:
            sample_request = "Busca información sobre inteligencia artificial y genera un documento resumen"

        print(f"\n🔍 Procesando: {sample_request}")

        result = await assistant.process_user_request(sample_request)

        if result["status"] == "completed":
            print("\n✅ Solicitud procesada exitosamente!")
            print(f"📊 Componentes utilizados: {', '.join(result['components_used'])}")

            final_response = result.get("final_response", {})
            if final_response.get("summary"):
                print(f"📋 Resumen: {final_response['summary'][:200]}...")

            artifacts = final_response.get("artifacts_generated", [])
            if artifacts:
                print("\n📄 Archivos generados:")
                for artifact in artifacts:
                    print(f"  • {artifact['format'].upper()}: {artifact['location']}")

        else:
            print(f"❌ Error: {result.get('error', 'Error desconocido')}")

    else:
        print("❌ No se pudo inicializar el sistema correctamente")


if __name__ == "__main__":
    asyncio.run(main())
