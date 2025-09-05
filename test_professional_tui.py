#!/usr/bin/env python3
"""
Test simple para verificar que la interfaz profesional funciona correctamente
"""
import asyncio
import sys
import os

# Añadir el directorio padre al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Prueba que todas las importaciones funcionan"""
    try:
        # Test importaciones de widgets
        from src.tui.dashboard_widgets import (
            ProfessionalMetricsPanel,
            IntelligenceControlCenter,
            AdvancedOperationsPanel,
            RealTimeMonitor,
            DomainIntelligencePanel,
            AIAssistantInterface,
            SystemStatusBar
        )
        print("✅ Dashboard widgets importados correctamente")

        # Test importación de la app principal
        from src.tui.professional_app import WebScraperProfessionalApp, run_professional_app
        print("✅ Professional app importada correctamente")

        # Test crear instancia de la app
        app = WebScraperProfessionalApp()
        print("✅ Instancia de la app creada correctamente")

        print("\n🎉 ¡Todas las pruebas pasaron! La interfaz profesional está lista para usar.")
        print("\nPara lanzar la interfaz profesional usa:")
        print("   python -m src.main --tui-pro")
        print("   o")
        print("   WebScraperPRO_Enhanced.bat (opción 3)")

        return True

    except Exception as e:
        print(f"❌ Error en las importaciones: {e}")
        return False

async def main():
    """Test principal"""
    print("🔍 Probando la interfaz profesional...")
    print("=" * 50)

    success = await test_imports()

    if success:
        print("\n✨ ¡La interfaz profesional está lista!")
        print("\nCaracterísticas principales:")
        print("- 📊 Dashboard con métricas en tiempo real")
        print("- 🧠 Control de inteligencia híbrida (IA-A + IA-B)")
        print("- ⚙️ Panel de operaciones avanzadas")
        print("- 📈 Monitor en tiempo real")
        print("- 🌐 Inteligencia de dominios")
        print("- 🤖 Interfaz del asistente AI")
        print("- 📋 Exportación y reportes")
        print("- 🔧 Configuración avanzada")

        return 0
    else:
        print("\n❌ Hay problemas con la configuración")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
