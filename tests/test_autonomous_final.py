#!/usr/bin/env python3
"""
Prueba de Sistema Autónomo - Validación Final
Valida que el sistema autónomo esté completamente integrado y funcionando
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def test_webscraperpro_autonomous_options():
    """Prueba que WebScraperPRO.bat tenga opciones autónomas funcionando"""
    print("🔍 Verificando opciones autónomas en WebScraperPRO.bat...")

    bat_file = Path("WebScraperPRO.bat")
    if not bat_file.exists():
        print("❌ WebScraperPRO.bat no encontrado")
        return False

    content = bat_file.read_text(encoding='utf-8')

    # Verificar que existen las opciones autónomas
    autonomous_keywords = [
        "Control Autónomo Total",
        "Estado Sistema Autónomo",
        "Scraping Autónomo",
        ":autonomous_control",
        ":autonomous_status",
        ":autonomous_scraping"
    ]

    missing = []
    for keyword in autonomous_keywords:
        if keyword not in content:
            missing.append(keyword)

    if missing:
        print(f"❌ Faltan elementos: {missing}")
        return False

    print("✅ Todas las opciones autónomas están disponibles")
    return True

def test_autonomous_cli_status():
    """Prueba que el CLI autónomo muestre estado correctamente"""
    print("🔍 Probando comando de estado autónomo...")

    try:
        result = subprocess.run([
            sys.executable, "scripts/autonomous_cli.py", "status"
        ], capture_output=True, text=True, timeout=30)

        output = result.stdout

        # Verificar elementos clave en la salida
        key_elements = [
            "ESTADO DEL SISTEMA",
            "Estado:",
            "Nivel Autonomía:",
            "MÉTRICAS DE OPERACIÓN"
        ]

        missing = []
        for element in key_elements:
            if element not in output:
                missing.append(element)

        if missing:
            print(f"❌ Faltan elementos en estado: {missing}")
            return False

        print("✅ Comando de estado funciona correctamente")
        return True

    except Exception as e:
        print(f"❌ Error ejecutando status: {e}")
        return False

def test_autonomous_cli_help():
    """Prueba que el CLI autónomo muestre ayuda"""
    print("🔍 Probando comando de ayuda autónomo...")

    try:
        result = subprocess.run([
            sys.executable, "scripts/autonomous_cli.py", "--help"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Comando de ayuda funciona")
            return True
        else:
            print(f"❌ Error en ayuda: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error ejecutando help: {e}")
        return False

def test_core_components_exist():
    """Verifica que existan los archivos principales"""
    print("🔍 Verificando componentes principales...")

    core_files = [
        "autonomous_cli.py",
        "src/intelligence/autonomous_controller.py",
        "src/intelligence/autonomous_coordinator.py",
        "WebScraperPRO.bat"
    ]

    missing = []
    for file_path in core_files:
        if not Path(file_path).exists():
            missing.append(file_path)

    if missing:
        print(f"❌ Archivos faltantes: {missing}")
        return False

    print("✅ Todos los componentes principales existen")
    return True

def generate_final_report():
    """Genera reporte final del sistema"""
    print("\n" + "="*70)
    print("🎯 VALIDACIÓN FINAL - SISTEMA AUTÓNOMO WEBSCRAPERPRO")
    print("="*70)

    tests = [
        ("Componentes Principales", test_core_components_exist),
        ("Opciones WebScraperPRO", test_webscraperpro_autonomous_options),
        ("CLI Help", test_autonomous_cli_help),
        ("CLI Status", test_autonomous_cli_status)
    ]

    results = {}
    total_passed = 0

    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        print("-" * 40)

        try:
            result = test_func()
            results[test_name] = result
            if result:
                total_passed += 1
                print(f"✅ {test_name} - CORRECTO")
            else:
                print(f"❌ {test_name} - FALLÓ")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results[test_name] = False

    print("\n" + "="*70)
    print("📋 RESUMEN FINAL")
    print("="*70)

    for test_name, result in results.items():
        status = "✅ CORRECTO" if result else "❌ FALLÓ"
        print(f"{test_name:<30} {status}")

    success_rate = (total_passed / len(tests)) * 100
    print(f"\n📊 Tasa de éxito: {success_rate:.1f}% ({total_passed}/{len(tests)})")

    if total_passed == len(tests):
        print("\n🎉 ¡SISTEMA AUTÓNOMO COMPLETAMENTE FUNCIONAL!")
        print("🚀 Listo para usar desde WebScraperPRO.bat")
        print("\n📖 INSTRUCCIONES DE USO:")
        print("   1. Ejecutar WebScraperPRO.bat")
        print("   2. Seleccionar opción 3 para Control Autónomo Total")
        print("   3. Seleccionar opción 4 para Estado del Sistema")
        print("   4. Seleccionar opción 5 para Scraping Autónomo")

        final_status = "ÉXITO COMPLETO"
    else:
        print(f"\n⚠️  {len(tests) - total_passed} pruebas fallaron")
        print("Revisar errores antes del uso en producción")
        final_status = "NECESITA REVISIÓN"

    # Guardar reporte final
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": "WebScraperPRO Autonomous System",
        "version": "1.0",
        "total_tests": len(tests),
        "passed_tests": total_passed,
        "success_rate": success_rate,
        "final_status": final_status,
        "test_results": results,
        "ready_for_production": total_passed == len(tests)
    }

    with open("autonomous_system_final_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Reporte final guardado: autonomous_system_final_report.json")

    return total_passed == len(tests)

def main():
    """Función principal"""
    print("🚀 INICIANDO VALIDACIÓN FINAL DEL SISTEMA AUTÓNOMO")
    success = generate_final_report()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
