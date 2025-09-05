#!/usr/bin/env python3
"""
Test de Integración - Sistema Autónomo con WebScraperPRO

Este script verifica que la integración entre el sistema autónomo
y el archivo principal WebScraperPRO.bat funcione correctamente.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def test_autonomous_cli_exists():
    """Verifica que autonomous_cli.py existe y es ejecutable"""
    print("🔍 Verificando autonomous_cli.py...")

    cli_path = Path("scripts/autonomous_cli.py")
    if not cli_path.exists():
        print("❌ ERROR: autonomous_cli.py no encontrado")
        return False

    print("✅ autonomous_cli.py encontrado")
    return True

def test_autonomous_controller_exists():
    """Verifica que el controlador autónomo existe"""
    print("🔍 Verificando autonomous_controller.py...")

    controller_path = Path("src/intelligence/autonomous_controller.py")
    if not controller_path.exists():
        print("❌ ERROR: autonomous_controller.py no encontrado")
        return False

    print("✅ autonomous_controller.py encontrado")
    return True

def test_autonomous_coordinator_exists():
    """Verifica que el coordinador autónomo existe"""
    print("🔍 Verificando autonomous_coordinator.py...")

    coordinator_path = Path("src/intelligence/autonomous_coordinator.py")
    if not coordinator_path.exists():
        print("❌ ERROR: autonomous_coordinator.py no encontrado")
        return False

    print("✅ autonomous_coordinator.py encontrado")
    return True

def test_webscraperpro_integration():
    """Verifica que WebScraperPRO.bat tiene las opciones autónomas"""
    print("🔍 Verificando integración en WebScraperPRO.bat...")

    bat_path = Path("WebScraperPRO.bat")
    if not bat_path.exists():
        print("❌ ERROR: WebScraperPRO.bat no encontrado")
        return False

    content = bat_path.read_text(encoding='utf-8', errors='ignore')

    required_sections = [
        "CONTROL AUTONOMO TOTAL",
        "Estado del Sistema Autonomo",
        "Scraping Autonomo Inteligente",
        ":autonomous_control",
        ":autonomous_status",
        ":autonomous_scraping"
    ]

    for section in required_sections:
        if section not in content:
            print(f"❌ ERROR: Sección '{section}' no encontrada en WebScraperPRO.bat")
            return False

    print("✅ Todas las secciones autónomas encontradas en WebScraperPRO.bat")
    return True

def test_cli_help():
    """Prueba que el CLI autónomo responde correctamente"""
    print("🔍 Probando autonomous_cli.py --help...")

    try:
        result = subprocess.run([
            sys.executable, "scripts/autonomous_cli.py", "--help"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ autonomous_cli.py responde correctamente")
            return True
        else:
            print(f"❌ ERROR: autonomous_cli.py falló con código {result.returncode}")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ ERROR ejecutando autonomous_cli.py: {e}")
        return False

def test_components_import():
    """Verifica que los componentes se pueden importar correctamente"""
    print("🔍 Verificando importación de componentes...")

    try:
        # Test import del controlador autónomo
        sys.path.insert(0, str(Path("src/intelligence")))
        from autonomous_controller import AutonomousControllerBrain
        print("✅ AutonomousControllerBrain importado correctamente")

        # Test import del coordinador autónomo
        from autonomous_coordinator import AutonomousScraperCoordinator
        print("✅ AutonomousScraperCoordinator importado correctamente")

        return True

    except ImportError as e:
        print(f"❌ ERROR de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        return False

def generate_integration_report():
    """Genera un reporte de la integración"""
    print("\n" + "="*60)
    print("📊 REPORTE DE INTEGRACIÓN - SISTEMA AUTÓNOMO")
    print("="*60)

    tests = [
        ("CLI Autónomo", test_autonomous_cli_exists),
        ("Controlador Autónomo", test_autonomous_controller_exists),
        ("Coordinador Autónomo", test_autonomous_coordinator_exists),
        ("Integración WebScraperPRO", test_webscraperpro_integration),
        ("CLI Help", test_cli_help),
        ("Importación Componentes", test_components_import)
    ]

    results = {}
    total_passed = 0

    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                total_passed += 1
        except Exception as e:
            print(f"❌ ERROR en {test_name}: {e}")
            results[test_name] = False

    print("\n" + "="*60)
    print("📋 RESUMEN DE RESULTADOS")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:<30} {status}")

    print(f"\n📊 Total: {total_passed}/{len(tests)} pruebas pasaron")

    if total_passed == len(tests):
        print("\n🎉 ¡INTEGRACIÓN COMPLETA EXITOSA!")
        print("El sistema autónomo está listo para usar desde WebScraperPRO.bat")
    else:
        print(f"\n⚠️  {len(tests) - total_passed} pruebas fallaron")
        print("Revisa los errores antes de usar el sistema autónomo")

    # Guardar reporte
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(tests),
        "passed_tests": total_passed,
        "results": results,
        "status": "SUCCESS" if total_passed == len(tests) else "FAILURE"
    }

    with open("integration_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Reporte guardado en: integration_test_report.json")

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN DEL SISTEMA AUTÓNOMO")
    print("=" * 60)

    # Cambiar al directorio del script
    os.chdir(Path(__file__).parent)

    generate_integration_report()

if __name__ == "__main__":
    main()
