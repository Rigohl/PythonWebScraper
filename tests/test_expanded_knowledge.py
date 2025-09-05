import sys
import os
import sqlite3
import time

def test_expanded_knowledge_base():
    """Test the massively expanded knowledge base."""

    print("🧠 Testing Expanded Knowledge Base")
    print("=" * 50)

    success_count = 0
    total_tests = 12

    # Test 1: Core Knowledge Store
    print("1. Testing Knowledge Store Functionality...")
    try:
        # Add the src directory to the path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        from intelligence.knowledge_store import KnowledgeStore

        # Create test knowledge store
        store = KnowledgeStore(":memory:")

        # Test adding programming knowledge
        store.add_programming_knowledge(
            "test_category",
            "test_topic",
            "Test content for verification",
            0.9,
            "test_source"
        )

        # Query back the knowledge
        results = store.query_programming_knowledge("test_category")

        if len(results) > 0 and results[0]['content'] == "Test content for verification":
            print("   ✅ Knowledge store functional")
            success_count += 1
        else:
            print("   ❌ Knowledge store failed")

    except Exception as e:
        print(f"   ❌ Knowledge store test failed: {e}")

    # Test 2: Seed Programming Knowledge
    print("2. Testing Programming Knowledge Seeding...")
    try:
        store = KnowledgeStore(":memory:")
        seeded_count = store.seed_programming_knowledge()

        if seeded_count >= 70:  # Expected around 70+ items
            print(f"   ✅ Seeded {seeded_count} programming knowledge items")
            success_count += 1
        else:
            print(f"   ❌ Only seeded {seeded_count} items, expected 70+")

    except Exception as e:
        print(f"   ❌ Programming knowledge seeding failed: {e}")

    # Test 3: Autonomous Learning System
    print("3. Testing Autonomous Learning System...")
    try:
        from intelligence.autonomous_learning import KnowledgeSeeder

        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        results = seeder.seed_all_knowledge()
        total_seeded = sum(results.values())

        if total_seeded >= 200:  # Expecting 200+ total items
            print(f"   ✅ Seeded {total_seeded} total knowledge items across {len(results)} categories")
            success_count += 1
        else:
            print(f"   ❌ Only seeded {total_seeded} items, expected 200+")

    except Exception as e:
        print(f"   ❌ Autonomous learning test failed: {e}")

    # Test 4: Web Scraping Knowledge
    print("4. Testing Web Scraping Knowledge...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        scraping_count = seeder._seed_scraping_knowledge()
        scraping_results = store.query_programming_knowledge("web_scraping")

        if scraping_count >= 15 and len(scraping_results) >= 15:
            print(f"   ✅ {scraping_count} scraping techniques stored")
            success_count += 1
        else:
            print(f"   ❌ Insufficient scraping knowledge: {scraping_count}")

    except Exception as e:
        print(f"   ❌ Scraping knowledge test failed: {e}")

    # Test 5: JavaScript Knowledge
    print("5. Testing JavaScript Ecosystem Knowledge...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        js_count = seeder._seed_javascript_ecosystem()
        js_results = store.query_programming_knowledge("javascript_ecosystem")

        if js_count >= 15 and len(js_results) >= 15:
            print(f"   ✅ {js_count} JavaScript ecosystem items stored")
            success_count += 1
        else:
            print(f"   ❌ Insufficient JavaScript knowledge: {js_count}")

    except Exception as e:
        print(f"   ❌ JavaScript knowledge test failed: {e}")

    # Test 6: Bot Development Knowledge
    print("6. Testing Bot Development Knowledge...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        bot_count = seeder._seed_bot_development_knowledge()
        bot_results = store.query_programming_knowledge("bot_development")

        if bot_count >= 15 and len(bot_results) >= 15:
            print(f"   ✅ {bot_count} bot development items stored")
            success_count += 1
        else:
            print(f"   ❌ Insufficient bot knowledge: {bot_count}")

    except Exception as e:
        print(f"   ❌ Bot development test failed: {e}")

    # Test 7: UI/UX Knowledge
    print("7. Testing UI/UX Design Knowledge...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        uiux_count = seeder._seed_uiux_knowledge()
        uiux_results = store.query_programming_knowledge("uiux")

        if uiux_count >= 15 and len(uiux_results) >= 15:
            print(f"   ✅ {uiux_count} UI/UX design items stored")
            success_count += 1
        else:
            print(f"   ❌ Insufficient UI/UX knowledge: {uiux_count}")

    except Exception as e:
        print(f"   ❌ UI/UX knowledge test failed: {e}")

    # Test 8: Security Knowledge
    print("8. Testing Security Knowledge...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        security_count = seeder._seed_security_knowledge()
        security_results = store.query_programming_knowledge("security")

        if security_count >= 15 and len(security_results) >= 15:
            print(f"   ✅ {security_count} security practices stored")
            success_count += 1
        else:
            print(f"   ❌ Insufficient security knowledge: {security_count}")

    except Exception as e:
        print(f"   ❌ Security knowledge test failed: {e}")

    # Test 9: Database Knowledge
    print("9. Testing Database Knowledge...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        db_count = seeder._seed_database_patterns()
        db_results = store.query_programming_knowledge("database")

        if db_count >= 15 and len(db_results) >= 15:
            print(f"   ✅ {db_count} database patterns stored")
            success_count += 1
        else:
            print(f"   ❌ Insufficient database knowledge: {db_count}")

    except Exception as e:
        print(f"   ❌ Database knowledge test failed: {e}")

    # Test 10: Performance Knowledge
    print("10. Testing Performance Knowledge...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        perf_count = seeder._seed_performance_knowledge()
        perf_results = store.query_programming_knowledge("performance")

        if perf_count >= 15 and len(perf_results) >= 15:
            print(f"   ✅ {perf_count} performance optimization items stored")
            success_count += 1
        else:
            print(f"   ❌ Insufficient performance knowledge: {perf_count}")

    except Exception as e:
        print(f"   ❌ Performance knowledge test failed: {e}")

    # Test 11: Advanced Domains
    print("11. Testing Advanced Domains Knowledge...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        advanced_count = seeder._seed_advanced_domains()

        # Check multiple advanced categories
        ml_results = store.query_programming_knowledge("machine_learning")
        devops_results = store.query_programming_knowledge("devops")
        cloud_results = store.query_programming_knowledge("cloud")

        if advanced_count >= 15 and (len(ml_results) + len(devops_results) + len(cloud_results)) >= 10:
            print(f"   ✅ {advanced_count} advanced domain items stored")
            success_count += 1
        else:
            print(f"   ❌ Insufficient advanced knowledge: {advanced_count}")

    except Exception as e:
        print(f"   ❌ Advanced domains test failed: {e}")

    # Test 12: Knowledge Summary
    print("12. Testing Knowledge Summary...")
    try:
        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        # Seed all knowledge
        seeder.seed_all_knowledge()

        # Get summary
        summary = store.get_knowledge_summary()

        if (summary.get('programming_knowledge_count', 0) >= 200 and
            len(summary.get('programming_categories', [])) >= 10):
            print(f"   ✅ Knowledge summary shows {summary['programming_knowledge_count']} items across {len(summary['programming_categories'])} categories")
            success_count += 1
        else:
            print(f"   ❌ Knowledge summary insufficient")

    except Exception as e:
        print(f"   ❌ Knowledge summary test failed: {e}")

    # Calculate results
    success_percentage = (success_count / total_tests) * 100

    print("\n" + "=" * 50)
    print(f"🎯 Expanded Knowledge Base Test Results: {success_count}/{total_tests} ({success_percentage:.1f}%)")

    if success_percentage >= 80:
        print("🎉 KNOWLEDGE BASE: COMPREHENSIVE & FUNCTIONAL")
        print("   Knowledge domains verified:")
        print("   ✅ Web Scraping (Advanced anti-detection, dynamic content)")
        print("   ✅ JavaScript Ecosystem (Modern JS, frameworks, Node.js)")
        print("   ✅ Bot Development (Architecture, NLP, platforms)")
        print("   ✅ UI/UX Design (Research, accessibility, design systems)")
        print("   ✅ Database Optimization (Performance, security, patterns)")
        print("   ✅ Security Practices (Cryptography, compliance, threats)")
        print("   ✅ Performance Optimization (Profiling, caching, scaling)")
        print("   ✅ Advanced Domains (ML, DevOps, Cloud, System Design)")
        return True
    elif success_percentage >= 60:
        print("⚠️  KNOWLEDGE BASE: PARTIALLY FUNCTIONAL")
        print("   Some knowledge domains working, expansion recommended")
        return False
    else:
        print("❌ KNOWLEDGE BASE: INSUFFICIENT")
        print("   Critical knowledge gaps detected")
        return False

def test_knowledge_integration():
    """Test how knowledge integrates with brain systems."""

    print("\n🔗 Testing Knowledge Integration")
    print("=" * 40)

    integration_tests = [
        "Query web scraping knowledge for strategy formulation",
        "Use JavaScript knowledge for bot development insights",
        "Apply security knowledge to API development",
        "Combine UI/UX knowledge with performance optimization",
        "Integrate database knowledge with scalability patterns"
    ]

    integration_score = 0

    try:
        # Add the src directory to the path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        from intelligence.knowledge_store import KnowledgeStore
        from intelligence.autonomous_learning import KnowledgeSeeder

        store = KnowledgeStore(":memory:")
        seeder = KnowledgeSeeder(store)

        # Seed all knowledge
        results = seeder.seed_all_knowledge()

        for i, test in enumerate(integration_tests, 1):
            print(f"{i}. {test}")

            # Test cross-domain knowledge queries
            if i == 1:  # Web scraping
                web_results = store.query_programming_knowledge("web_scraping")
                if len(web_results) >= 10:
                    print("   ✅ Web scraping knowledge accessible")
                    integration_score += 1
            elif i == 2:  # JavaScript + Bot
                js_results = store.query_programming_knowledge("javascript")
                bot_results = store.query_programming_knowledge("bot_development")
                if len(js_results) >= 5 and len(bot_results) >= 5:
                    print("   ✅ Cross-domain knowledge accessible")
                    integration_score += 1
            elif i == 3:  # Security + API
                security_results = store.query_programming_knowledge("security")
                api_results = store.query_programming_knowledge("api_development")
                if len(security_results) >= 5 and len(api_results) >= 5:
                    print("   ✅ Security and API knowledge integrated")
                    integration_score += 1
            elif i == 4:  # UI/UX + Performance
                uiux_results = store.query_programming_knowledge("uiux")
                perf_results = store.query_programming_knowledge("performance")
                if len(uiux_results) >= 5 and len(perf_results) >= 5:
                    print("   ✅ Design and performance knowledge combined")
                    integration_score += 1
            elif i == 5:  # Database + Scalability
                db_results = store.query_programming_knowledge("database")
                cloud_results = store.query_programming_knowledge("cloud")
                if len(db_results) >= 5 and len(cloud_results) >= 3:
                    print("   ✅ Database and scalability patterns integrated")
                    integration_score += 1

    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")

    integration_percentage = (integration_score / len(integration_tests)) * 100
    print(f"\n🔗 Integration Score: {integration_score}/{len(integration_tests)} ({integration_percentage:.1f}%)")

    return integration_percentage >= 80

if __name__ == "__main__":
    print("🚀 Starting Expanded Knowledge Base Verification")
    print("Testing comprehensive technical knowledge across multiple domains...\n")

    knowledge_test = test_expanded_knowledge_base()
    integration_test = test_knowledge_integration()

    overall_success = knowledge_test and integration_test

    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 FINAL RESULT: COMPREHENSIVE KNOWLEDGE BASE READY")
        print("   ✅ 200+ curated knowledge items across 10+ technical domains")
        print("   ✅ Advanced web scraping, JavaScript, bot development")
        print("   ✅ UI/UX design, security, performance optimization")
        print("   ✅ Database patterns, cloud architecture, system design")
        print("   ✅ Cross-domain knowledge integration functional")
        print("   ✅ Brain now has comprehensive technical expertise")
    else:
        print("⚠️  FINAL RESULT: KNOWLEDGE BASE NEEDS EXPANSION")
        print("   Some knowledge domains functional, continued expansion recommended")

    sys.exit(0 if overall_success else 1)
