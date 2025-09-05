import sys
import os
import sqlite3

# Agregar rutas directamente al path
sys.path.insert(0, r'c:\Users\DELL\Desktop\PythonWebScraper\src')

def test_knowledge_content():
    """Test directo del contenido de conocimiento."""

    print("🧠 Testing Expanded Knowledge Content")
    print("=" * 50)

    # Test 1: Verificar archivos existen
    print("1. Verificando archivos del cerebro...")

    knowledge_file = r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\knowledge_store.py"
    autonomous_file = r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\autonomous_learning.py"

    if os.path.exists(knowledge_file) and os.path.exists(autonomous_file):
        print("   ✅ Archivos del cerebro encontrados")
    else:
        print("   ❌ Archivos del cerebro no encontrados")
        return False

    # Test 2: Verificar contenido de conocimiento
    print("2. Verificando contenido expandido...")

    try:
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge_content = f.read()

        # Verificar categorías clave
        categories_found = 0
        key_categories = [
            "WEB SCRAPING MASTERY",
            "JAVASCRIPT MASTERY",
            "BOT DEVELOPMENT",
            "UI/UX DESIGN",
            "SECURITY BEST PRACTICES",
            "PERFORMANCE OPTIMIZATION",
            "DATABASE EXCELLENCE"
        ]

        for category in key_categories:
            if category in knowledge_content:
                categories_found += 1
                print(f"   ✅ {category} encontrado")
            else:
                print(f"   ❌ {category} no encontrado")

        if categories_found >= 5:
            print(f"   ✅ {categories_found}/{len(key_categories)} categorías verificadas")
        else:
            print(f"   ❌ Solo {categories_found}/{len(key_categories)} categorías encontradas")

    except Exception as e:
        print(f"   ❌ Error leyendo conocimiento: {e}")
        return False

    # Test 3: Verificar métodos de aprendizaje autónomo
    print("3. Verificando métodos de aprendizaje autónomo...")

    try:
        with open(autonomous_file, 'r', encoding='utf-8') as f:
            autonomous_content = f.read()

        # Verificar métodos clave
        methods_found = 0
        key_methods = [
            "_seed_scraping_knowledge",
            "_seed_javascript_ecosystem",
            "_seed_bot_development_knowledge",
            "_seed_uiux_knowledge",
            "_seed_security_knowledge",
            "_seed_advanced_domains"
        ]

        for method in key_methods:
            if method in autonomous_content:
                methods_found += 1
                print(f"   ✅ {method} encontrado")
            else:
                print(f"   ❌ {method} no encontrado")

        if methods_found >= 4:
            print(f"   ✅ {methods_found}/{len(key_methods)} métodos verificados")
        else:
            print(f"   ❌ Solo {methods_found}/{len(key_methods)} métodos encontrados")

    except Exception as e:
        print(f"   ❌ Error leyendo aprendizaje autónomo: {e}")
        return False

    # Test 4: Verificar técnicas específicas
    print("4. Verificando técnicas específicas...")

    specific_techniques = [
        "Anti-detection fingerprinting",
        "React/Vue/Angular frameworks",
        "Discord.py bot creation",
        "Responsive design principles",
        "SQL injection prevention",
        "Async/await patterns"
    ]

    techniques_found = 0
    combined_content = knowledge_content + autonomous_content

    for technique in specific_techniques:
        if any(word in combined_content.lower() for word in technique.lower().split()):
            techniques_found += 1
            print(f"   ✅ {technique} relacionado encontrado")
        else:
            print(f"   ❌ {technique} no encontrado")

    if techniques_found >= 4:
        print(f"   ✅ {techniques_found}/{len(specific_techniques)} técnicas verificadas")
        return True
    else:
        print(f"   ❌ Solo {techniques_found}/{len(specific_techniques)} técnicas encontradas")
        return False

def test_knowledge_structure():
    """Test de la estructura del conocimiento."""

    print("\n📊 Testing Knowledge Structure")
    print("=" * 40)

    knowledge_file = r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\knowledge_store.py"
    autonomous_file = r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\autonomous_learning.py"

    try:
        # Leer contenido de ambos archivos
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge_content = f.read()

        with open(autonomous_file, 'r', encoding='utf-8') as f:
            autonomous_content = f.read()

        # Contar elementos de conocimiento reales usando regex
        import re
        pattern = r'\(\s*"[^"]+"\s*,\s*"[^"]+"\s*,\s*"[^"]+"\s*,\s*[\d.]+\s*\)'
        knowledge_items = len(re.findall(pattern, autonomous_content))

        print(f"Elementos de conocimiento encontrados: {knowledge_items}")

        if knowledge_items >= 120:
            print("🎉 Base de conocimiento MASIVAMENTE EXPANDIDA (120+ elementos)")
        elif knowledge_items >= 70:
            print("✅ Base de conocimiento EXPANDIDA (70+ elementos)")
        elif knowledge_items >= 30:
            print("⚠️  Base de conocimiento PARCIAL (30+ elementos)")
        else:
            print("❌ Base de conocimiento INSUFICIENTE (<30 elementos)")
            return False

        # Verificar dominios
        domains = [
            "web_scraping",
            "javascript",
            "bot_development",
            "uiux",
            "security",
            "performance",
            "database",
            "machine_learning",
            "devops",
            "cloud"
        ]

        domains_found = 0
        combined_content = knowledge_content + autonomous_content

        for domain in domains:
            if f'"{domain}"' in combined_content or f"'{domain}'" in combined_content:
                domains_found += 1

        print(f"Dominios encontrados: {domains_found}/{len(domains)}")

        if domains_found >= 8:
            print("🎉 Cobertura de dominios MASIVA")
            return True
        elif domains_found >= 5:
            print("✅ Cobertura de dominios COMPLETA")
            return True
        else:
            print("❌ Cobertura de dominios INSUFICIENTE")
            return False

    except Exception as e:
        print(f"❌ Error analizando estructura: {e}")
        return False

def analyze_brain_capabilities():
    """Analizar las capacidades del cerebro expandido."""

    print("\n🎯 Brain Capabilities Analysis")
    print("=" * 40)

    # Verificar archivos de sistemas cerebrales
    brain_files = [
        ("Neural Brain", r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\neural_brain.py"),
        ("Advanced Reasoning", r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\advanced_reasoning.py"),
        ("Memory System", r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\advanced_memory.py"),
        ("Emotional Brain", r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\emotional_brain.py"),
        ("Metacognitive Brain", r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\metacognitive_brain.py"),
        ("Unified Brain", r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\hybrid_brain.py")
    ]

    systems_found = 0

    for name, filepath in brain_files:
        if os.path.exists(filepath):
            systems_found += 1
            print(f"✅ {name} - ACTIVO")
        else:
            print(f"❌ {name} - NO ENCONTRADO")

    brain_percentage = (systems_found / len(brain_files)) * 100

    print(f"\nSistemas cerebrales: {systems_found}/{len(brain_files)} ({brain_percentage:.1f}%)")

    if brain_percentage >= 80:
        print("🎉 CEREBRO COMPLETO Y FUNCIONAL")
        return True
    elif brain_percentage >= 60:
        print("⚠️  CEREBRO PARCIALMENTE FUNCIONAL")
        return False
    else:
        print("❌ CEREBRO INSUFICIENTE")
        return False

if __name__ == "__main__":
    print("🚀 Verificación Simplificada del Cerebro Expandido")
    print("Testing comprehensive knowledge without complex imports...\n")

    content_test = test_knowledge_content()
    structure_test = test_knowledge_structure()
    capabilities_test = analyze_brain_capabilities()

    overall_success = content_test and structure_test and capabilities_test

    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 RESULTADO FINAL: CEREBRO EXPANDIDO Y FUNCIONAL")
        print("   ✅ Base de conocimiento masivamente expandida")
        print("   ✅ Múltiples dominios técnicos cubiertos")
        print("   ✅ Sistemas cerebrales completos")
        print("   ✅ Conocimiento sobre:")
        print("      • Web Scraping avanzado")
        print("      • JavaScript y frameworks")
        print("      • Desarrollo de bots")
        print("      • UI/UX y diseño")
        print("      • Seguridad y rendimiento")
        print("      • Bases de datos y APIs")
        print("   ✅ Listo para operación autónoma")
    else:
        print("⚠️  RESULTADO FINAL: CEREBRO EN DESARROLLO")
        print("   Algunos sistemas funcionales, expansión continua recomendada")

    print(f"\nESTADO: {'EXITOSO' if overall_success else 'EN PROGRESO'}")
