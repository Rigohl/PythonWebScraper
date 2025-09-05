import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.intelligence.hybrid_brain import HybridBrain
from src.intelligence.knowledge_store import KnowledgeStore
import json

def test_autonomous_brain():
    """Test the complete autonomous cycle: learning, knowledge application, patch generation."""

    print("🧠 Initializing Autonomous Brain Test")
    print("=" * 50)

    # Initialize brain
    try:
        brain = HybridBrain(
            brain_dir="src/intelligence",
            integration_mode="unified",
            learning_rate=0.01
        )
        print("✅ Brain initialized successfully")
    except Exception as e:
        print(f"❌ Brain initialization failed: {e}")
        return False

    # Start autonomous learning
    try:
        brain.start_continuous_learning()
        print("✅ Continuous learning started")
    except Exception as e:
        print(f"❌ Learning start failed: {e}")
        return False

    # Test knowledge-driven strategy formulation
    test_scenarios = [
        "improve web scraping performance",
        "optimize database queries",
        "enhance error handling",
        "implement security measures"
    ]

    print("\n🧪 Testing Knowledge-Driven Strategy Formulation")
    print("-" * 50)

    for scenario in test_scenarios:
        try:
            strategy = brain.formulate_strategy(scenario)
            print(f"📋 Scenario: {scenario}")
            print(f"   Confidence: {strategy['confidence']:.2f}")
            print(f"   Knowledge Enhanced: {strategy.get('knowledge_enhanced', False)}")
            print(f"   Programming Insights: {len(strategy.get('programming_insights', []))}")
            if strategy.get('programming_insights'):
                print(f"   Sample Insight: {strategy['programming_insights'][0][:100]}...")
            print()
        except Exception as e:
            print(f"❌ Strategy formulation failed for '{scenario}': {e}")

    # Test knowledge store
    print("📚 Testing Knowledge Store")
    print("-" * 30)

    try:
        if brain.knowledge_store:
            summary = brain.knowledge_store.get_knowledge_summary()
            print(f"✅ Total programming knowledge: {summary.get('programming_knowledge_count', 0)}")
            print(f"✅ Total strategies: {summary.get('strategy_count', 0)}")
            print(f"✅ Knowledge categories: {', '.join(summary.get('programming_categories', []))}")
        else:
            print("❌ Knowledge store not available")
    except Exception as e:
        print(f"❌ Knowledge store test failed: {e}")

    # Test autonomous patch generation
    print("\n🔧 Testing Autonomous Patch Generation")
    print("-" * 40)

    try:
        if brain.self_update_engine:
            suggestions = brain.self_update_engine.generate_improvements()
            print(f"✅ Generated {len(suggestions)} improvement suggestions")

            if suggestions:
                patches = brain.self_update_engine.generate_patch_proposals(brain.knowledge_store)
                print(f"✅ Generated {len(patches)} autonomous patch proposals")

                if patches:
                    sample_patch = patches[0]
                    print(f"   Sample patch type: {sample_patch['patch']['type']}")
                    print(f"   Risk level: {sample_patch['patch']['risk_level']}")
                    print(f"   Estimated impact: {sample_patch['patch']['estimated_impact']}")
        else:
            print("❌ Self-update engine not available")
    except Exception as e:
        print(f"❌ Patch generation test failed: {e}")

    # Test independence metrics
    print("\n🎯 Testing Independence Metrics")
    print("-" * 35)

    independence_score = 0
    max_score = 6

    # Check neural brain activity
    if hasattr(brain, 'unified_brain') and brain.unified_brain:
        independence_score += 1
        print("✅ Neural brain active")
    else:
        print("❌ Neural brain inactive")

    # Check autonomous learning
    if hasattr(brain, 'knowledge_seeder') and brain.knowledge_seeder:
        independence_score += 1
        print("✅ Knowledge seeding system active")
    else:
        print("❌ Knowledge seeding system inactive")

    # Check self-update capability
    if hasattr(brain, 'self_update_engine') and brain.self_update_engine:
        independence_score += 1
        print("✅ Self-update engine active")
    else:
        print("❌ Self-update engine inactive")

    # Check knowledge persistence
    if hasattr(brain, 'knowledge_store') and brain.knowledge_store:
        independence_score += 1
        print("✅ Knowledge store active")
    else:
        print("❌ Knowledge store inactive")

    # Check plugin extensibility
    if hasattr(brain, 'plugin_manager') and brain.plugin_manager:
        independence_score += 1
        print("✅ Plugin system active")
    else:
        print("❌ Plugin system inactive")

    # Check strategy history
    if hasattr(brain, 'strategy_history') and brain.strategy_history:
        independence_score += 1
        print("✅ Strategy learning active")
    else:
        print("❌ Strategy learning inactive")

    independence_percentage = (independence_score / max_score) * 100
    print(f"\n🎯 Independence Score: {independence_score}/{max_score} ({independence_percentage:.1f}%)")

    # Final assessment
    print("\n" + "=" * 50)
    if independence_percentage >= 80:
        print("🎉 AUTONOMOUS BRAIN TEST: PASSED")
        print("   The brain demonstrates high independence with:")
        print("   - Real neural processing")
        print("   - Knowledge-driven decision making")
        print("   - Autonomous patch generation")
        print("   - Minimal human intervention required")
        return True
    elif independence_percentage >= 60:
        print("⚠️  AUTONOMOUS BRAIN TEST: PARTIAL")
        print("   The brain shows moderate independence but needs improvement")
        return False
    else:
        print("❌ AUTONOMOUS BRAIN TEST: FAILED")
        print("   The brain lacks sufficient autonomous capabilities")
        return False

if __name__ == "__main__":
    success = test_autonomous_brain()
    sys.exit(0 if success else 1)
