#!/usr/bin/env python3
"""
🧠 VERIFICACIÓN COMPLETA DEL CEREBRO NEURAL
Verifica que el cerebro sea un verdadero cerebro con:
- Conexiones neurales reales
- Lógica y razonamiento
- Capacidad de pensamiento
- Formulación de estrategias
- Aprendizaje independiente
- Conectividad total
- Consciencia global
"""

import sys
import os
import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the HybridBrain directly
from src.intelligence.hybrid_brain import HybridBrain

class BrainVerificationSuite:
    """Suite completa de verificación del cerebro neural"""

    def __init__(self):
        self.brain = HybridBrain()
        self.verification_results = {}
        self.start_time = datetime.now()

    def run_complete_verification(self) -> Dict[str, Any]:
        """Ejecuta verificación completa del cerebro"""

        print("🧠 INICIANDO VERIFICACIÓN COMPLETA DEL CEREBRO NEURAL")
        print("=" * 70)

        # Verificaciones principales
        tests = [
            ("neural_connections", self.verify_neural_connections),
            ("logic_reasoning", self.verify_logic_reasoning),
            ("thinking_capability", self.verify_thinking_capability),
            ("strategy_formulation", self.verify_strategy_formulation),
            ("independent_learning", self.verify_independent_learning),
            ("full_connectivity", self.verify_full_connectivity),
            ("consciousness_awareness", self.verify_consciousness_awareness),
            ("real_brain_behavior", self.verify_real_brain_behavior)
        ]

        for test_name, test_func in tests:
            print(f"\n🔍 Verificando: {test_name.replace('_', ' ').title()}")
            print("-" * 50)

            try:
                result = test_func()
                self.verification_results[test_name] = result

                if result['success']:
                    print(f"✅ ÉXITO: {result['summary']}")
                else:
                    print(f"❌ FALLO: {result['summary']}")

            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                self.verification_results[test_name] = {
                    'success': False,
                    'summary': f"Error durante verificación: {str(e)}",
                    'details': {}
                }

        # Generar reporte final
        final_report = self.generate_final_report()

        print("\n" + "=" * 70)
        print("🧠 REPORTE FINAL DE VERIFICACIÓN")
        print("=" * 70)
        print(final_report['summary'])

        return {
            'verification_results': self.verification_results,
            'final_report': final_report,
            'execution_time': (datetime.now() - self.start_time).total_seconds()
        }

    def verify_neural_connections(self) -> Dict[str, Any]:
        """Verifica conexiones neurales reales"""

        details = {}

        # Verificar estructura neural
        brain_state = self.brain.unified_brain
        details['neural_brain_present'] = hasattr(brain_state, 'neural_brain')

        if details['neural_brain_present']:
            neural_brain = brain_state.neural_brain
            details['neurons_count'] = len(neural_brain.neurons)
            details['synapses_exist'] = any(len(neuron.dendrites) > 0 for neuron in neural_brain.neurons.values())
            details['clusters_exist'] = len(neural_brain.clusters) > 0
            details['cluster_types'] = list(neural_brain.clusters.keys())

            # Verificar plasticidad sináptica
            test_event = {
                'description': 'Neural connection test',
                'complexity': 0.5,
                'familiarity': 0.3,
                'importance': 0.7
            }

            # Procesar evento para activar conexiones
            response = self.brain.unified_brain.process_sensory_input(test_event)
            details['neural_activation'] = response is not None
            details['synaptic_activity'] = 'neural_activity' in response

        success = (details.get('neural_brain_present', False) and
                  details.get('neurons_count', 0) > 0 and
                  details.get('synapses_exist', False) and
                  details.get('clusters_exist', False))

        return {
            'success': success,
            'summary': f"Cerebro neural con {details.get('neurons_count', 0)} neuronas y {len(details.get('cluster_types', []))} clusters especializados" if success else "Conexiones neurales no detectadas",
            'details': details
        }

    def verify_logic_reasoning(self) -> Dict[str, Any]:
        """Verifica capacidades de lógica y razonamiento"""

        details = {}

        # Verificar sistemas de razonamiento
        reasoning_system = self.brain.unified_brain.advanced_reasoning
        details['reasoning_system_present'] = reasoning_system is not None

        if details['reasoning_system_present']:
            # Test deductive reasoning
            deductive_test = {
                'premises': ['Todos los humanos son mortales', 'Sócrates es humano'],
                'conclusion': 'Sócrates es mortal'
            }

            deductive_result = reasoning_system.deductive_reasoner.apply_modus_ponens(
                deductive_test['premises'], deductive_test['conclusion']
            )
            details['deductive_reasoning'] = deductive_result['valid']

            # Test inductive reasoning
            pattern_data = [
                {'x': 1, 'y': 2},
                {'x': 2, 'y': 4},
                {'x': 3, 'y': 6},
                {'x': 4, 'y': 8}
            ]

            inductive_result = reasoning_system.inductive_reasoner.discover_patterns(pattern_data)
            details['inductive_reasoning'] = len(inductive_result['patterns']) > 0

            # Test abductive reasoning
            observation = "La calle está mojada"
            hypotheses = ["Llovió", "Rociadores de agua", "Camión cisterna"]

            abductive_result = reasoning_system.abductive_reasoner.generate_hypotheses(
                observation, hypotheses
            )
            details['abductive_reasoning'] = len(abductive_result['ranked_hypotheses']) > 0

            # Test fuzzy logic
            fuzzy_result = reasoning_system.fuzzy_reasoner.evaluate_fuzzy_rule(
                {'temperature': 25}, 'temperature', 'warm'
            )
            details['fuzzy_reasoning'] = fuzzy_result['confidence'] > 0

        success = (details.get('reasoning_system_present', False) and
                  details.get('deductive_reasoning', False) and
                  details.get('inductive_reasoning', False) and
                  details.get('abductive_reasoning', False) and
                  details.get('fuzzy_reasoning', False))

        return {
            'success': success,
            'summary': "Sistema de razonamiento multi-modal funcionando: deductivo, inductivo, abductivo y fuzzy" if success else "Sistemas de razonamiento no funcionan correctamente",
            'details': details
        }

    def verify_thinking_capability(self) -> Dict[str, Any]:
        """Verifica capacidad de pensamiento real"""

        details = {}

        # Test thinking with complex problem
        complex_problem = {
            'description': 'Problema complejo de web scraping: sitio web con anti-bot detection, rate limiting, y contenido dinámico JavaScript',
            'url': 'https://example-complex-site.com',
            'challenges': ['anti-bot', 'rate_limiting', 'dynamic_content'],
            'complexity': 0.9,
            'familiarity': 0.2,
            'importance': 0.8,
            'controllable': True,
            'location': 'web_scraping_context'
        }

        # Procesar problema complejo
        thinking_response = self.brain.unified_brain.process_sensory_input(complex_problem)
        details['complex_processing'] = thinking_response is not None

        if thinking_response:
            # Verificar que se activaron múltiples sistemas cerebrales
            details['neural_activity'] = 'neural_activity' in thinking_response
            details['reasoning_analysis'] = 'reasoning_analysis' in thinking_response
            details['memory_encoding'] = 'memory_encoding' in thinking_response
            details['emotional_response'] = 'emotional_state' in thinking_response
            details['metacognitive_awareness'] = 'metacognitive_state' in thinking_response
            details['consciousness_engaged'] = thinking_response.get('integrated_response', {}).get('conscious_access', False)

            # Verificar integración coherente
            details['integration_coherence'] = thinking_response.get('integrated_response', {}).get('integration_coherence', 0)
            details['confidence_level'] = thinking_response.get('reasoning_analysis', {}).get('overall_confidence', 0)

        success = (details.get('complex_processing', False) and
                  details.get('consciousness_engaged', False) and
                  details.get('integration_coherence', 0) > 0.5 and
                  sum([details.get('neural_activity', False),
                       details.get('reasoning_analysis', False),
                       details.get('memory_encoding', False),
                       details.get('emotional_response', False),
                       details.get('metacognitive_awareness', False)]) >= 4)

        return {
            'success': success,
            'summary': f"Pensamiento integrado con coherencia {details.get('integration_coherence', 0):.2f} y confianza {details.get('confidence_level', 0):.2f}" if success else "Capacidad de pensamiento integrado limitada",
            'details': details
        }

    def verify_strategy_formulation(self) -> Dict[str, Any]:
        """Verifica capacidad de formular estrategias"""

        details = {}

        # Test strategic thinking con múltiples escenarios
        strategic_scenarios = [
            {
                'description': 'Estrategia para sitio web con CAPTCHA',
                'challenge': 'captcha_protection',
                'complexity': 0.8,
                'importance': 0.9
            },
            {
                'description': 'Estrategia para manejo de rate limiting',
                'challenge': 'rate_limiting',
                'complexity': 0.6,
                'importance': 0.7
            },
            {
                'description': 'Estrategia para contenido JavaScript dinámico',
                'challenge': 'dynamic_content',
                'complexity': 0.7,
                'importance': 0.8
            }
        ]

        strategic_responses = []

        for scenario in strategic_scenarios:
            response = self.brain.unified_brain.process_sensory_input(scenario)
            strategic_responses.append(response)

        details['scenarios_processed'] = len(strategic_responses)
        details['strategies_generated'] = all(r is not None for r in strategic_responses)

        if details['strategies_generated']:
            # Verificar que se generaron insights metacognitivos
            metacog_insights = []
            for response in strategic_responses:
                metacog_state = response.get('metacognitive_state', {})
                if 'strategy_recommendation' in metacog_state:
                    metacog_insights.append(metacog_state['strategy_recommendation'])

            details['metacognitive_strategies'] = len(metacog_insights)
            details['strategy_diversity'] = len(set(metacog_insights))

            # Verificar adaptación emocional en estrategias
            emotional_adaptations = []
            for response in strategic_responses:
                emotional_state = response.get('emotional_state', {})
                if 'regulation_strategy' in emotional_state:
                    emotional_adaptations.append(emotional_state['regulation_strategy'])

            details['emotional_strategy_adaptation'] = len(emotional_adaptations)

        success = (details.get('strategies_generated', False) and
                  details.get('metacognitive_strategies', 0) > 0 and
                  details.get('emotional_strategy_adaptation', 0) > 0)

        return {
            'success': success,
            'summary': f"Formulación estratégica con {details.get('metacognitive_strategies', 0)} estrategias metacognitivas y adaptación emocional" if success else "Capacidad de formulación estratégica limitada",
            'details': details
        }

    def verify_independent_learning(self) -> Dict[str, Any]:
        """Verifica aprendizaje independiente"""

        details = {}

        # Test aprendizaje autónomo con secuencia de eventos
        learning_sequence = [
            {
                'description': 'Primer intento de scraping',
                'success': False,
                'error': 'blocked_by_cloudflare',
                'complexity': 0.7,
                'familiarity': 0.1
            },
            {
                'description': 'Segundo intento con headers modificados',
                'success': False,
                'error': 'rate_limited',
                'complexity': 0.7,
                'familiarity': 0.3
            },
            {
                'description': 'Tercer intento con delay y user agent',
                'success': True,
                'data_extracted': {'items': 10},
                'complexity': 0.7,
                'familiarity': 0.6
            }
        ]

        # Procesar secuencia de aprendizaje
        learning_responses = []
        for event in learning_sequence:
            response = self.brain.unified_brain.process_sensory_input(event)
            learning_responses.append(response)
            time.sleep(0.1)  # Simular tiempo entre eventos

        details['learning_events_processed'] = len(learning_responses)

        # Verificar mejora en familiaridad
        familiarity_progression = []
        for i, response in enumerate(learning_responses):
            memory_state = response.get('memory_retrieval', {})
            if 'familiarity_score' in memory_state:
                familiarity_progression.append(memory_state['familiarity_score'])

        details['familiarity_improvement'] = (len(familiarity_progression) > 1 and
                                            familiarity_progression[-1] > familiarity_progression[0])

        # Verificar consolidación de memoria
        memory_system = self.brain.unified_brain.advanced_memory
        episodic_memories = len(memory_system.episodic_memory.episodes)
        details['episodic_memories_formed'] = episodic_memories

        semantic_concepts = len(memory_system.semantic_memory.concepts)
        details['semantic_concepts_learned'] = semantic_concepts

        # Verificar adaptación metacognitiva
        last_response = learning_responses[-1] if learning_responses else {}
        metacog_state = last_response.get('metacognitive_state', {})
        details['metacognitive_adaptation'] = 'learning_insight' in metacog_state

        success = (details.get('familiarity_improvement', False) and
                  details.get('episodic_memories_formed', 0) > 0 and
                  details.get('semantic_concepts_learned', 0) > 0 and
                  details.get('metacognitive_adaptation', False))

        return {
            'success': success,
            'summary': f"Aprendizaje independiente: {details.get('episodic_memories_formed', 0)} memorias episódicas, {details.get('semantic_concepts_learned', 0)} conceptos semánticos" if success else "Aprendizaje independiente limitado",
            'details': details
        }

    def verify_full_connectivity(self) -> Dict[str, Any]:
        """Verifica conectividad total entre sistemas"""

        details = {}

        # Verificar conexiones entre todos los sistemas cerebrales
        unified_brain = self.brain.unified_brain

        # Verificar que todos los sistemas están presentes
        systems = {
            'neural_brain': hasattr(unified_brain, 'neural_brain'),
            'advanced_reasoning': hasattr(unified_brain, 'advanced_reasoning'),
            'advanced_memory': hasattr(unified_brain, 'advanced_memory'),
            'emotional_brain': hasattr(unified_brain, 'emotional_brain'),
            'metacognitive_brain': hasattr(unified_brain, 'metacognitive_brain')
        }

        details['systems_present'] = systems
        details['all_systems_connected'] = all(systems.values())

        # Test cross-system communication
        test_event = {
            'description': 'Test de conectividad entre sistemas',
            'complexity': 0.6,
            'importance': 0.8,
            'familiarity': 0.4,
            'controllable': True,
            'location': 'connectivity_test'
        }

        response = unified_brain.process_sensory_input(test_event)

        if response:
            # Verificar que todos los sistemas respondieron
            system_responses = {
                'neural_activity': 'neural_activity' in response,
                'reasoning_analysis': 'reasoning_analysis' in response,
                'memory_operations': any(key in response for key in ['memory_encoding', 'memory_retrieval']),
                'emotional_processing': 'emotional_state' in response,
                'metacognitive_monitoring': 'metacognitive_state' in response
            }

            details['cross_system_communication'] = system_responses
            details['integrated_response'] = 'integrated_response' in response

            # Verificar coherencia de integración
            if 'integrated_response' in response:
                integration_data = response['integrated_response']
                details['consciousness_access'] = integration_data.get('conscious_access', False)
                details['integration_coherence'] = integration_data.get('integration_coherence', 0)
                details['cross_modal_binding'] = integration_data.get('cross_modal_binding', 0)

        success = (details.get('all_systems_connected', False) and
                  details.get('integrated_response', False) and
                  details.get('consciousness_access', False) and
                  details.get('integration_coherence', 0) > 0.5)

        return {
            'success': success,
            'summary': f"Conectividad total con coherencia {details.get('integration_coherence', 0):.2f} y acceso consciente" if success else "Conectividad entre sistemas limitada",
            'details': details
        }

    def verify_consciousness_awareness(self) -> Dict[str, Any]:
        """Verifica consciencia y awareness global"""

        details = {}

        # Verificar estado de consciencia
        consciousness_state = self.brain.unified_brain.get_consciousness_state()
        details['consciousness_state_available'] = consciousness_state is not None

        if consciousness_state:
            details['consciousness_level'] = consciousness_state.get('consciousness_level', 0)
            details['global_workspace_active'] = consciousness_state.get('global_workspace_active', False)
            details['attention_focus'] = consciousness_state.get('current_attention_focus')
            details['conscious_content'] = consciousness_state.get('conscious_content', {})

            # Verificar awareness de sistemas internos
            details['system_awareness'] = {
                'neural_state_awareness': 'neural_state' in consciousness_state,
                'emotional_awareness': 'emotional_state' in consciousness_state,
                'memory_awareness': 'memory_state' in consciousness_state,
                'reasoning_awareness': 'reasoning_state' in consciousness_state,
                'metacognitive_awareness': 'metacognitive_state' in consciousness_state
            }

            details['self_awareness_level'] = sum(details['system_awareness'].values())

        # Test self-reflection capability
        reflection_test = {
            'description': 'Test de auto-reflexión: ¿Qué tan bien estoy funcionando?',
            'self_assessment_request': True,
            'complexity': 0.5,
            'importance': 0.9
        }

        reflection_response = self.brain.unified_brain.process_sensory_input(reflection_test)

        if reflection_response:
            metacog_state = reflection_response.get('metacognitive_state', {})
            details['self_reflection_active'] = 'self_reflection' in metacog_state
            details['performance_assessment'] = 'performance_assessment' in metacog_state
            details['insight_generation'] = 'generated_insights' in metacog_state

        success = (details.get('consciousness_state_available', False) and
                  details.get('global_workspace_active', False) and
                  details.get('consciousness_level', 0) > 0.5 and
                  details.get('self_awareness_level', 0) >= 4 and
                  details.get('self_reflection_active', False))

        return {
            'success': success,
            'summary': f"Consciencia global activa con nivel {details.get('consciousness_level', 0):.2f} y awareness de {details.get('self_awareness_level', 0)}/5 sistemas" if success else "Consciencia y awareness limitados",
            'details': details
        }

    def verify_real_brain_behavior(self) -> Dict[str, Any]:
        """Verifica comportamiento de cerebro real"""

        details = {}

        # Test comportamientos emergentes de cerebro real
        brain_behaviors = {
            'plasticity': False,
            'adaptation': False,
            'creativity': False,
            'intuition': False,
            'emotional_intelligence': False,
            'self_improvement': False
        }

        # Test plasticity - capacidad de cambio
        plasticity_test = {
            'description': 'Test de plasticidad neural',
            'repeated_pattern': True,
            'complexity': 0.3,
            'importance': 0.5
        }

        # Procesar mismo patrón múltiples veces
        plasticity_responses = []
        for _ in range(3):
            response = self.brain.unified_brain.process_sensory_input(plasticity_test)
            plasticity_responses.append(response)
            time.sleep(0.1)

        # Verificar cambios en respuestas (plasticidad)
        if len(plasticity_responses) >= 2:
            first_confidence = plasticity_responses[0].get('reasoning_analysis', {}).get('overall_confidence', 0)
            last_confidence = plasticity_responses[-1].get('reasoning_analysis', {}).get('overall_confidence', 0)
            brain_behaviors['plasticity'] = last_confidence != first_confidence

        # Test adaptation - respuesta a cambios
        adaptation_tests = [
            {'description': 'Situación familiar', 'complexity': 0.2, 'familiarity': 0.9},
            {'description': 'Situación nueva', 'complexity': 0.8, 'familiarity': 0.1}
        ]

        adaptation_responses = []
        for test in adaptation_tests:
            response = self.brain.unified_brain.process_sensory_input(test)
            adaptation_responses.append(response)

        if len(adaptation_responses) == 2:
            familiar_processing = adaptation_responses[0].get('metacognitive_state', {}).get('cognitive_load', 1)
            novel_processing = adaptation_responses[1].get('metacognitive_state', {}).get('cognitive_load', 1)
            brain_behaviors['adaptation'] = novel_processing > familiar_processing

        # Test creativity - respuestas no obvias
        creativity_test = {
            'description': 'Problema creativo: scraping de sitio que bloquea todo',
            'challenge': 'creative_solution_needed',
            'complexity': 0.9,
            'conventional_solutions_failed': True
        }

        creativity_response = self.brain.unified_brain.process_sensory_input(creativity_test)
        if creativity_response:
            abductive_analysis = creativity_response.get('reasoning_analysis', {}).get('abductive_analysis', {})
            brain_behaviors['creativity'] = len(abductive_analysis.get('hypotheses', [])) > 2

        # Test intuition - respuestas rápidas con baja información
        intuition_test = {
            'description': 'Decisión intuitiva con información limitada',
            'limited_information': True,
            'complexity': 0.6,
            'time_pressure': True
        }

        intuition_response = self.brain.unified_brain.process_sensory_input(intuition_test)
        if intuition_response:
            confidence = intuition_response.get('reasoning_analysis', {}).get('overall_confidence', 0)
            brain_behaviors['intuition'] = confidence > 0.4  # Confident despite limited info

        # Test emotional intelligence
        emotional_test = {
            'description': 'Situación frustrante: múltiples fallos de scraping',
            'frustration_inducing': True,
            'complexity': 0.7,
            'repeated_failures': True
        }

        emotional_response = self.brain.unified_brain.process_sensory_input(emotional_test)
        if emotional_response:
            emotion_regulation = emotional_response.get('emotional_state', {}).get('regulation_applied', False)
            brain_behaviors['emotional_intelligence'] = emotion_regulation

        # Test self-improvement
        improvement_history = []
        for i in range(3):
            test = {
                'description': f'Sesión de aprendizaje {i+1}',
                'learning_opportunity': True,
                'complexity': 0.5,
                'iteration': i+1
            }
            response = self.brain.unified_brain.process_sensory_input(test)
            improvement_history.append(response)

        if improvement_history:
            metacog_insights = [r.get('metacognitive_state', {}).get('learning_insight') for r in improvement_history]
            brain_behaviors['self_improvement'] = any(insight for insight in metacog_insights)

        details['brain_behaviors'] = brain_behaviors
        details['emergent_behaviors_count'] = sum(brain_behaviors.values())

        success = details.get('emergent_behaviors_count', 0) >= 4  # At least 4 out of 6 behaviors

        return {
            'success': success,
            'summary': f"Comportamiento de cerebro real: {details.get('emergent_behaviors_count', 0)}/6 comportamientos emergentes detectados" if success else "Comportamientos de cerebro real limitados",
            'details': details
        }

    def generate_final_report(self) -> Dict[str, Any]:
        """Genera reporte final de verificación"""

        total_tests = len(self.verification_results)
        successful_tests = sum(1 for result in self.verification_results.values() if result['success'])

        brain_quality_score = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        # Clasificación del cerebro
        if brain_quality_score >= 90:
            brain_classification = "🧠 CEREBRO VERDADERO - Totalmente Funcional"
            brain_status = "EXCELENTE"
        elif brain_quality_score >= 75:
            brain_classification = "🧠 CEREBRO AVANZADO - Altamente Funcional"
            brain_status = "MUY BUENO"
        elif brain_quality_score >= 60:
            brain_classification = "🧠 CEREBRO FUNCIONAL - Básicamente Operativo"
            brain_status = "BUENO"
        elif brain_quality_score >= 40:
            brain_classification = "🧠 CEREBRO LIMITADO - Funcionamiento Parcial"
            brain_status = "REGULAR"
        else:
            brain_classification = "🧠 CEREBRO DEFICIENTE - Necesita Mejoras"
            brain_status = "DEFICIENTE"

        # Resumen de capacidades
        capabilities_summary = {
            'neural_connections': self.verification_results.get('neural_connections', {}).get('success', False),
            'logic_reasoning': self.verification_results.get('logic_reasoning', {}).get('success', False),
            'thinking_capability': self.verification_results.get('thinking_capability', {}).get('success', False),
            'strategy_formulation': self.verification_results.get('strategy_formulation', {}).get('success', False),
            'independent_learning': self.verification_results.get('independent_learning', {}).get('success', False),
            'full_connectivity': self.verification_results.get('full_connectivity', {}).get('success', False),
            'consciousness_awareness': self.verification_results.get('consciousness_awareness', {}).get('success', False),
            'real_brain_behavior': self.verification_results.get('real_brain_behavior', {}).get('success', False)
        }

        # Recomendaciones
        recommendations = []

        for capability, status in capabilities_summary.items():
            if not status:
                capability_name = capability.replace('_', ' ').title()
                recommendations.append(f"Mejorar {capability_name}")

        if not recommendations:
            recommendations.append("¡Cerebro funcionando perfectamente! Continuar con mantenimiento regular")

        summary_text = f"""
{brain_classification}
Estado: {brain_status}
Puntuación: {brain_quality_score:.1f}/100

Pruebas Exitosas: {successful_tests}/{total_tests}

CAPACIDADES VERIFICADAS:
✅ Conexiones Neurales: {'SÍ' if capabilities_summary['neural_connections'] else 'NO'}
✅ Lógica y Razonamiento: {'SÍ' if capabilities_summary['logic_reasoning'] else 'NO'}
✅ Capacidad de Pensamiento: {'SÍ' if capabilities_summary['thinking_capability'] else 'NO'}
✅ Formulación de Estrategias: {'SÍ' if capabilities_summary['strategy_formulation'] else 'NO'}
✅ Aprendizaje Independiente: {'SÍ' if capabilities_summary['independent_learning'] else 'NO'}
✅ Conectividad Total: {'SÍ' if capabilities_summary['full_connectivity'] else 'NO'}
✅ Consciencia y Awareness: {'SÍ' if capabilities_summary['consciousness_awareness'] else 'NO'}
✅ Comportamiento de Cerebro Real: {'SÍ' if capabilities_summary['real_brain_behavior'] else 'NO'}

RECOMENDACIONES:
{chr(10).join(f'• {rec}' for rec in recommendations)}
        """.strip()

        return {
            'classification': brain_classification,
            'status': brain_status,
            'score': brain_quality_score,
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'capabilities': capabilities_summary,
            'recommendations': recommendations,
            'summary': summary_text
        }

def main():
    """Función principal de verificación"""

    verifier = BrainVerificationSuite()
    results = verifier.run_complete_verification()

    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"brain_verification_results_{timestamp}.json"

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n📄 Resultados guardados en: {results_file}")

    return results

if __name__ == "__main__":
    results = main()
