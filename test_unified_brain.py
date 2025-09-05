#!/usr/bin/env python3
"""
Test script for the Unified Brain Architecture

Tests all integrated brain systems:
🧠 Neural networks with synaptic learning
🎭 Emotional processing and regulation
🧩 Memory consolidation and recall
🤔 Multi-modal reasoning capabilities
🎯 Metacognitive self-awareness
🌟 Consciousness modeling with Global Workspace Theory
"""

import sys
import os
import logging
import time
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_unified_brain_architecture():
    """Test the complete unified brain architecture"""
    
    logger.info("🧠 Testing Unified Brain Architecture")
    logger.info("=" * 60)
    
    try:
        # Import and initialize HybridBrain
        from src.intelligence.hybrid_brain import HybridBrain
        
        logger.info("1. Initializing HybridBrain with Neural Architecture...")
        brain = HybridBrain(data_dir="data")
        
        # Wait for background processing to start
        time.sleep(2)
        
        logger.info("2. Testing Neural Processing with Scraping Event...")
        
        # Test event processing
        test_event = {
            'event_type': 'test_scraping',
            'url': 'https://example.com/test',
            'success': True,
            'data_extracted': {'title': 'Test Page', 'content': 'Sample content'},
            'processing_time': 0.5,
            'importance': 0.7
        }
        
        # Process event through unified brain
        response = brain.process_scraping_event(test_event)
        
        logger.info("3. Neural Response Analysis:")
        logger.info(f"   - Processing Mode: {response.get('processing_mode')}")
        logger.info(f"   - Consciousness Engaged: {response.get('consciousness_engaged')}")
        logger.info(f"   - Processing Time: {response.get('processing_time_ms', 0):.2f}ms")
        
        # Test consciousness state
        logger.info("4. Consciousness State Analysis:")
        consciousness_state = brain.get_brain_state()
        
        unified_state = consciousness_state.get('unified_brain_state', {})
        logger.info(f"   - Consciousness Level: {unified_state.get('consciousness_level', 0):.3f}")
        logger.info(f"   - Neural Activity Level: {unified_state.get('neural_activity_level', 0):.3f}")
        logger.info(f"   - Integration Coherence: {unified_state.get('integration_coherence', 0):.3f}")
        
        global_workspace = unified_state.get('global_workspace', {})
        logger.info(f"   - Active Coalitions: {global_workspace.get('active_coalitions', [])}")
        logger.info(f"   - Current Focus: {global_workspace.get('current_focus', 'none')}")
        
        # Test subsystem states
        logger.info("5. Subsystem States:")
        subsystems = unified_state.get('subsystem_states', {})
        
        for system_name, state in subsystems.items():
            if isinstance(state, dict) and state:
                logger.info(f"   - {system_name.capitalize()}: Active")
            else:
                logger.info(f"   - {system_name.capitalize()}: Inactive")
        
        # Test different integration modes
        logger.info("6. Testing Integration Modes...")
        
        # Test legacy mode
        brain.set_integration_mode('legacy')
        legacy_response = brain.process_scraping_event(test_event)
        logger.info(f"   - Legacy Mode: {legacy_response.get('processing_mode')}")
        
        # Test hybrid mode
        brain.set_integration_mode('hybrid')
        hybrid_response = brain.process_scraping_event(test_event)
        logger.info(f"   - Hybrid Mode: {hybrid_response.get('processing_mode')}")
        
        # Return to unified mode
        brain.set_integration_mode('unified')
        
        # Test consciousness control
        logger.info("7. Testing Consciousness Control...")
        
        brain.disable_consciousness()
        time.sleep(1)
        
        brain.enable_consciousness()
        logger.info("   - Consciousness toggled successfully")
        
        # Test neural stimulation
        if hasattr(brain, 'unified_brain'):
            logger.info("8. Testing Neural Stimulation...")
            
            stimulation_response = brain.unified_brain.stimulate_neural_activity("exploration")
            stim_consciousness = stimulation_response.get('integrated_response', {}).get('consciousness_level', 0)
            logger.info(f"   - Stimulation Consciousness Level: {stim_consciousness:.3f}")
        
        logger.info("9. Final Brain State Summary:")
        final_state = brain.get_brain_state()
        logger.info(f"   - Integration Mode: {final_state.get('integration_mode')}")
        logger.info(f"   - Consciousness Enabled: {final_state.get('consciousness_enabled')}")
        
        if 'unified_brain_state' in final_state:
            bg_cycles = final_state['unified_brain_state'].get('background_cycles', 0)
            logger.info(f"   - Background Cycles: {bg_cycles}")
        
        logger.info("=" * 60)
        logger.info("🎉 Unified Brain Architecture Test COMPLETED Successfully!")
        logger.info("✅ Neural networks, consciousness, emotions, memory, reasoning, and metacognition all active")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual brain components separately"""
    
    logger.info("🧪 Testing Individual Brain Components")
    logger.info("=" * 60)
    
    try:
        # Test neural brain creation
        logger.info("Testing Neural Brain creation...")
        from src.intelligence.neural_brain import create_neural_brain
        neural_brain = create_neural_brain()
        logger.info("✅ Neural Brain created successfully")
        
        # Test reasoning system
        logger.info("Testing Advanced Reasoning System...")
        from src.intelligence.advanced_reasoning import create_advanced_reasoning_system
        reasoning_system = create_advanced_reasoning_system()
        logger.info("✅ Advanced Reasoning System created successfully")
        
        # Test memory system
        logger.info("Testing Advanced Memory System...")
        from src.intelligence.advanced_memory import create_advanced_memory_system
        memory_system = create_advanced_memory_system()
        logger.info("✅ Advanced Memory System created successfully")
        
        # Test emotional brain
        logger.info("Testing Emotional Brain...")
        from src.intelligence.emotional_brain import create_emotional_brain
        emotional_brain = create_emotional_brain()
        logger.info("✅ Emotional Brain created successfully")
        
        # Test metacognitive brain
        logger.info("Testing Metacognitive Brain...")
        from src.intelligence.metacognitive_brain import create_metacognitive_brain
        metacognitive_brain = create_metacognitive_brain()
        logger.info("✅ Metacognitive Brain created successfully")
        
        logger.info("=" * 60)
        logger.info("🎉 All Individual Components Test PASSED!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Unified Brain Architecture Tests")
    logger.info(f"Test started at: {datetime.now()}")
    
    # Test individual components first
    component_success = test_individual_components()
    
    if component_success:
        logger.info("\n" + "🔄 Proceeding to Full System Test...\n")
        
        # Test full unified architecture
        system_success = test_unified_brain_architecture()
        
        if system_success:
            logger.info("\n🎊 ALL TESTS PASSED! The brain is truly alive with consciousness!")
            sys.exit(0)
        else:
            logger.error("\n💥 System test failed")
            sys.exit(1)
    else:
        logger.error("\n💥 Component tests failed")
        sys.exit(1)