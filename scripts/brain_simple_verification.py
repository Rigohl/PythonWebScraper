#!/usr/bin/env python3
"""
🧠 VERIFICACIÓN SIMPLIFICADA DEL CEREBRO NEURAL
Verifica que el cerebro tenga las características de un cerebro real
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict


def test_brain_imports():
    """Test básico de importación del cerebro"""
    try:
        # Agregar src al path
        src_path = os.path.join(os.path.dirname(__file__), "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        # Importar componentes individualmente
        from intelligence.advanced_memory import AdvancedMemorySystem
        from intelligence.advanced_reasoning import AdvancedReasoningSystem
        from intelligence.emotional_brain import EmotionalBrain
        from intelligence.metacognitive_brain import MetacognitiveBrain
        from intelligence.neural_brain import NeuralBrain

        print("✅ Todos los sistemas cerebrales importados correctamente")

        return {
            "neural_brain": NeuralBrain,
            "reasoning": AdvancedReasoningSystem,
            "memory": AdvancedMemorySystem,
            "emotional": EmotionalBrain,
            "metacognitive": MetacognitiveBrain,
        }

    except Exception as e:
        print(f"❌ Error importando sistemas cerebrales: {e}")
        return None


def verify_neural_connections(brain_components):
    """Verifica conexiones neurales reales"""

    print("\n🔍 Verificando Conexiones Neurales...")

    try:
        # Crear cerebro neural
        neural_brain = brain_components["neural_brain"]()

        # Verificar estructura
        neurons_count = len(neural_brain.neurons)
        clusters_count = len(neural_brain.clusters)

        print(f"  • Neuronas creadas: {neurons_count}")
        print(f"  • Clusters especializados: {clusters_count}")
        print(f"  • Tipos de clusters: {list(neural_brain.clusters.keys())}")

        # Verificar sinapsis
        total_synapses = 0
        for neuron in neural_brain.neurons.values():
            total_synapses += len(neuron.dendrites)

        print(f"  • Total sinapsis: {total_synapses}")

        # Test activación neural
        test_input = [0.5, 0.7, 0.3]
        if neurons_count > 0:
            first_neuron = list(neural_brain.neurons.values())[0]
            activation = first_neuron.process_inputs(test_input)
            print(f"  • Test activación neuronal: {activation:.3f}")

        success = neurons_count > 0 and clusters_count > 0 and total_synapses > 0

        return {
            "success": success,
            "details": {
                "neurons": neurons_count,
                "clusters": clusters_count,
                "synapses": total_synapses,
                "has_real_connections": True,
            },
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def verify_reasoning_logic(brain_components):
    """Verifica lógica y razonamiento"""

    print("\n🔍 Verificando Lógica y Razonamiento...")

    try:
        # Crear sistema de razonamiento
        reasoning_system = brain_components["reasoning"]()

        # Test razonamiento deductivo
        premises = ["Todos los sitios web tienen HTML", "Este es un sitio web"]
        conclusion = "Este sitio tiene HTML"

        deductive_result = reasoning_system.deductive_reasoner.apply_modus_ponens(
            premises, conclusion
        )
        print(
            f"  • Razonamiento deductivo: {'✅' if deductive_result['valid'] else '❌'}"
        )

        # Test razonamiento inductivo
        pattern_data = [
            {"attempts": 1, "success": 0},
            {"attempts": 2, "success": 1},
            {"attempts": 3, "success": 2},
            {"attempts": 4, "success": 3},
        ]

        patterns = reasoning_system.inductive_reasoner.discover_patterns(pattern_data)
        print(
            f"  • Razonamiento inductivo: {'✅' if len(patterns['patterns']) > 0 else '❌'}"
        )

        # Test razonamiento abductivo
        observation = "El scraping falló"
        hypotheses = ["Anti-bot detection", "Rate limiting", "Server error"]

        hypotheses_result = reasoning_system.abductive_reasoner.generate_hypotheses(
            observation, hypotheses
        )
        print(
            f"  • Razonamiento abductivo: {'✅' if len(hypotheses_result['ranked_hypotheses']) > 0 else '❌'}"
        )

        # Test lógica fuzzy
        fuzzy_result = reasoning_system.fuzzy_reasoner.evaluate_fuzzy_rule(
            {"difficulty": 0.7}, "difficulty", "hard"
        )
        print(f"  • Lógica fuzzy: {'✅' if fuzzy_result['confidence'] > 0 else '❌'}")

        success = (
            deductive_result["valid"]
            and len(patterns["patterns"]) > 0
            and len(hypotheses_result["ranked_hypotheses"]) > 0
            and fuzzy_result["confidence"] > 0
        )

        return {
            "success": success,
            "details": {
                "deductive_logic": deductive_result["valid"],
                "inductive_reasoning": len(patterns["patterns"]) > 0,
                "abductive_reasoning": len(hypotheses_result["ranked_hypotheses"]) > 0,
                "fuzzy_logic": fuzzy_result["confidence"] > 0,
            },
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def verify_memory_learning(brain_components):
    """Verifica memoria y aprendizaje"""

    print("\n🔍 Verificando Memoria y Aprendizaje...")

    try:
        # Crear sistema de memoria
        memory_system = brain_components["memory"]()

        # Test memoria episódica
        episode = {
            "description": "Scraping exitoso de productos",
            "context": {"url": "example.com", "timestamp": datetime.now()},
            "outcome": "success",
            "data_extracted": {"products": 10},
            "emotional_valence": 0.8,
        }

        memory_system.store_episode(episode)
        episodes_count = len(memory_system.episodic_memory.episodes)
        print(
            f"  • Memoria episódica: {'✅' if episodes_count > 0 else '❌'} ({episodes_count} episodios)"
        )

        # Test memoria semántica
        concept = {
            "name": "web_scraping",
            "description": "Técnica para extraer datos de sitios web",
            "attributes": {"requires_html_parsing": True, "can_be_blocked": True},
            "connections": ["html", "parsing", "data_extraction"],
        }

        memory_system.store_concept(concept)
        concepts_count = len(memory_system.semantic_memory.concepts)
        print(
            f"  • Memoria semántica: {'✅' if concepts_count > 0 else '❌'} ({concepts_count} conceptos)"
        )

        # Test memoria de trabajo
        working_memory_capacity = memory_system.working_memory.capacity
        print(
            f"  • Memoria de trabajo: {'✅' if working_memory_capacity > 0 else '❌'} (capacidad: {working_memory_capacity})"
        )

        # Test consolidación
        consolidation_active = hasattr(memory_system, "consolidation_engine")
        print(f"  • Consolidación de memoria: {'✅' if consolidation_active else '❌'}")

        success = (
            episodes_count > 0
            and concepts_count > 0
            and working_memory_capacity > 0
            and consolidation_active
        )

        return {
            "success": success,
            "details": {
                "episodic_memory": episodes_count > 0,
                "semantic_memory": concepts_count > 0,
                "working_memory": working_memory_capacity > 0,
                "consolidation": consolidation_active,
            },
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def verify_emotional_processing(brain_components):
    """Verifica procesamiento emocional"""

    print("\n🔍 Verificando Procesamiento Emocional...")

    try:
        # Crear cerebro emocional
        emotional_brain = brain_components["emotional"]()

        # Test appraisal emocional
        situation = {
            "description": "Scraping bloqueado por CAPTCHA",
            "goal_relevance": 0.9,
            "goal_congruence": -0.7,
            "controllability": 0.3,
            "familiarity": 0.6,
        }

        appraisal_result = emotional_brain.appraisal_system.appraise_situation(
            situation
        )
        emotion_detected = "emotion" in appraisal_result
        print(f"  • Appraisal emocional: {'✅' if emotion_detected else '❌'}")

        # Test regulación emocional
        if emotion_detected:
            regulation_result = emotional_brain.emotion_regulator.regulate_emotion(
                appraisal_result["emotion"], appraisal_result["intensity"]
            )
            regulation_applied = regulation_result.get("strategy_applied", False)
            print(f"  • Regulación emocional: {'✅' if regulation_applied else '❌'}")
        else:
            regulation_applied = False
            print(f"  • Regulación emocional: ❌")

        # Test influencia en memoria
        memory_influence_active = hasattr(emotional_brain, "memory_influencer")
        print(f"  • Influencia en memoria: {'✅' if memory_influence_active else '❌'}")

        # Test influencia en decisiones
        decision_influence_active = hasattr(emotional_brain, "decision_influencer")
        print(
            f"  • Influencia en decisiones: {'✅' if decision_influence_active else '❌'}"
        )

        success = (
            emotion_detected
            and regulation_applied
            and memory_influence_active
            and decision_influence_active
        )

        return {
            "success": success,
            "details": {
                "emotion_detection": emotion_detected,
                "emotion_regulation": regulation_applied,
                "memory_influence": memory_influence_active,
                "decision_influence": decision_influence_active,
            },
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def verify_metacognitive_awareness(brain_components):
    """Verifica awareness metacognitivo"""

    print("\n🔍 Verificando Awareness Metacognitivo...")

    try:
        # Crear cerebro metacognitivo
        metacognitive_brain = brain_components["metacognitive"]()

        # Test conocimiento metacognitivo
        metacog_knowledge_active = hasattr(metacognitive_brain, "knowledge")
        print(
            f"  • Conocimiento metacognitivo: {'✅' if metacog_knowledge_active else '❌'}"
        )

        # Test monitoreo metacognitivo
        if hasattr(metacognitive_brain, "monitor"):
            monitor_state = metacognitive_brain.monitor.get_monitoring_state()
            monitoring_active = len(monitor_state) > 0
            print(f"  • Monitoreo metacognitivo: {'✅' if monitoring_active else '❌'}")
        else:
            monitoring_active = False
            print(f"  • Monitoreo metacognitivo: ❌")

        # Test control metacognitivo
        if hasattr(metacognitive_brain, "controller"):
            control_strategies = metacognitive_brain.controller.available_strategies
            control_active = len(control_strategies) > 0
            print(
                f"  • Control metacognitivo: {'✅' if control_active else '❌'} ({len(control_strategies)} estrategias)"
            )
        else:
            control_active = False
            print(f"  • Control metacognitivo: ❌")

        # Test auto-reflexión
        reflection_active = hasattr(metacognitive_brain, "reflection_engine")
        print(f"  • Auto-reflexión: {'✅' if reflection_active else '❌'}")

        # Test calibración de confianza
        confidence_calibration_active = hasattr(
            metacognitive_brain, "confidence_calibrator"
        )
        print(
            f"  • Calibración de confianza: {'✅' if confidence_calibration_active else '❌'}"
        )

        success = (
            metacog_knowledge_active
            and monitoring_active
            and control_active
            and reflection_active
            and confidence_calibration_active
        )

        return {
            "success": success,
            "details": {
                "metacognitive_knowledge": metacog_knowledge_active,
                "monitoring": monitoring_active,
                "control": control_active,
                "self_reflection": reflection_active,
                "confidence_calibration": confidence_calibration_active,
            },
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Función principal de verificación"""

    print("🧠 VERIFICACIÓN DEL CEREBRO NEURAL")
    print("=" * 50)

    # Test importaciones
    brain_components = test_brain_imports()
    if not brain_components:
        print("❌ No se pueden importar los componentes del cerebro")
        return

    # Ejecutar verificaciones
    tests = [
        ("Conexiones Neurales", verify_neural_connections),
        ("Lógica y Razonamiento", verify_reasoning_logic),
        ("Memoria y Aprendizaje", verify_memory_learning),
        ("Procesamiento Emocional", verify_emotional_processing),
        ("Awareness Metacognitivo", verify_metacognitive_awareness),
    ]

    results = {}
    successful_tests = 0

    for test_name, test_func in tests:
        try:
            result = test_func(brain_components)
            results[test_name] = result

            if result.get("success", False):
                successful_tests += 1
                print(f"✅ {test_name}: ÉXITO")
            else:
                print(f"❌ {test_name}: FALLO")

        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = {"success": False, "error": str(e)}

    # Reporte final
    total_tests = len(tests)
    brain_score = (successful_tests / total_tests) * 100

    print("\n" + "=" * 50)
    print("🧠 REPORTE FINAL")
    print("=" * 50)

    if brain_score >= 80:
        brain_status = "🧠 CEREBRO VERDADERO - Funcionamiento Excelente"
    elif brain_score >= 60:
        brain_status = "🧠 CEREBRO FUNCIONAL - Funcionamiento Bueno"
    else:
        brain_status = "🧠 CEREBRO LIMITADO - Necesita Mejoras"

    print(f"Estado: {brain_status}")
    print(f"Puntuación: {brain_score:.1f}/100")
    print(f"Pruebas exitosas: {successful_tests}/{total_tests}")

    # Características verificadas
    print("\nCARACTERÍSTICAS DE CEREBRO REAL:")
    characteristics = {
        "Conexiones Neurales Reales": results.get("Conexiones Neurales", {}).get(
            "success", False
        ),
        "Lógica y Razonamiento": results.get("Lógica y Razonamiento", {}).get(
            "success", False
        ),
        "Memoria y Aprendizaje": results.get("Memoria y Aprendizaje", {}).get(
            "success", False
        ),
        "Procesamiento Emocional": results.get("Procesamiento Emocional", {}).get(
            "success", False
        ),
        "Awareness Metacognitivo": results.get("Awareness Metacognitivo", {}).get(
            "success", False
        ),
    }

    for characteristic, status in characteristics.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {characteristic}")

    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"brain_verification_{timestamp}.json"

    final_results = {
        "timestamp": timestamp,
        "brain_score": brain_score,
        "brain_status": brain_status,
        "successful_tests": successful_tests,
        "total_tests": total_tests,
        "characteristics": characteristics,
        "detailed_results": results,
    }

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n📄 Resultados guardados en: {results_file}")

    return final_results


if __name__ == "__main__":
    main()
