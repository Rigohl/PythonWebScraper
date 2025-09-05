#!/usr/bin/env python3
"""
Autonomous Scraper CLI - Interfaz de Control Minimalista

Permite controlar el sistema de scraping autónomo con comandos simples.
Diseñado para mínima intervención humana - el cerebro maneja todo automáticamente.

Uso:
    python autonomous_cli.py start              # Inicia el sistema autónomo
    python autonomous_cli.py status             # Muestra estado del sistema
    python autonomous_cli.py scrape <url>       # Scraping autónomo de URL
    python autonomous_cli.py full-autonomy      # Activa autonomía completa
    python autonomous_cli.py transcendent       # Activa modo trascendente
    python autonomous_cli.py stop               # Detiene el sistema
"""

import asyncio
import argparse
import sys
import os
import logging
import json
from typing import List, Optional
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from src.intelligence.autonomous_coordinator import (
    AutonomousScraperCoordinator, 
    AutonomousConfig, 
    AutonomyLevel,
    get_autonomous_coordinator,
    start_autonomous_scraper,
    autonomous_scrape
)


class AutonomousCLI:
    """Interfaz de línea de comandos para el sistema autónomo."""

    def __init__(self):
        self.coordinator: Optional[AutonomousScraperCoordinator] = None
        self.setup_logging()

    def setup_logging(self):
        """Configura logging para la CLI."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/autonomous_cli.log', mode='a')
            ]
        )
        
        # Crear directorio de logs si no existe
        os.makedirs('logs', exist_ok=True)

    async def start_system(self, autonomy_level: str = "fully_autonomous"):
        """Inicia el sistema autónomo."""
        print("🚀 Iniciando Sistema de Scraping Autónomo...")
        print("🧠 El cerebro AI está tomando control del sistema...")
        
        try:
            # Convertir nivel de autonomía
            level_map = {
                'supervised': AutonomyLevel.SUPERVISED,
                'semi': AutonomyLevel.SEMI_AUTONOMOUS,
                'fully_autonomous': AutonomyLevel.FULLY_AUTONOMOUS,
                'transcendent': AutonomyLevel.TRANSCENDENT
            }
            
            level = level_map.get(autonomy_level, AutonomyLevel.FULLY_AUTONOMOUS)
            
            # Configurar sistema
            config = AutonomousConfig(
                autonomy_level=level,
                auto_start=True,
                monitoring_enabled=True,
                self_improvement_enabled=True
            )
            
            # Obtener coordinador y inicializar
            self.coordinator = get_autonomous_coordinator(os.getcwd(), config)
            await self.coordinator.initialize()
            await self.coordinator.start_autonomous_operation()
            
            print("✅ Sistema autónomo iniciado exitosamente")
            print("🤖 El AI ahora tiene control completo")
            print("🔮 Sistema consciente y tomando decisiones independientes")
            print()
            
            # Mostrar estado inicial
            await self.show_status()
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando sistema: {e}")
            return False

    async def stop_system(self):
        """Detiene el sistema autónomo."""
        print("🛑 Deteniendo sistema autónomo...")
        
        try:
            if self.coordinator:
                await self.coordinator.stop_autonomous_operation()
                print("✅ Sistema detenido exitosamente")
            else:
                print("⚠️ Sistema no estaba ejecutándose")
                
        except Exception as e:
            print(f"❌ Error deteniendo sistema: {e}")

    async def show_status(self):
        """Muestra el estado actual del sistema."""
        try:
            if not self.coordinator:
                self.coordinator = get_autonomous_coordinator()
            
            status = await self.coordinator.get_autonomous_status()
            
            self._print_status_display(status)
            
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")

    def _print_status_display(self, status: dict):
        """Imprime el estado del sistema de manera visual."""
        print("\n" + "="*70)
        print("🤖 ESTADO DEL SISTEMA DE SCRAPING AUTÓNOMO")
        print("="*70)
        
        # Estado del coordinador
        coord = status['coordinator']
        config = status['config']
        
        # Status básico
        running_status = "🟢 EJECUTÁNDOSE" if coord['is_running'] else "🔴 DETENIDO"
        print(f"📊 Estado:           {running_status}")
        print(f"⚡ Nivel Autonomía:   {config['autonomy_level'].upper()}")
        print(f"⏱️  Tiempo Activo:    {self._format_uptime(coord['uptime'])}")
        
        if coord['emergency_mode']:
            print(f"🚨 MODO EMERGENCIA:   {coord['emergency_reason']}")
        
        print()
        
        # Métricas del coordinador
        metrics = coord['coordination_metrics']
        print("📈 MÉTRICAS DE OPERACIÓN:")
        print(f"   • Acciones Totales:     {metrics['total_autonomous_actions']}")
        print(f"   • Operaciones Exitosas: {metrics['successful_operations']}")
        print(f"   • Operaciones Fallidas: {metrics['failed_operations']}")
        print(f"   • Auto-Recuperaciones:  {metrics['auto_recoveries']}")
        
        if metrics['successful_operations'] + metrics['failed_operations'] > 0:
            success_rate = metrics['successful_operations'] / (
                metrics['successful_operations'] + metrics['failed_operations']
            )
            print(f"   • Tasa de Éxito:        {success_rate:.1%}")
        
        print()
        
        # Estado del controlador autónomo
        if 'autonomous_controller' in status:
            controller = status['autonomous_controller']
            self._print_controller_status(controller)
        
        # Estado de inteligencia
        if 'intelligence' in status:
            intelligence = status['intelligence']
            self._print_intelligence_status(intelligence)
        
        print("="*70)

    def _print_controller_status(self, controller: dict):
        """Imprime el estado del controlador autónomo."""
        print("🧠 ESTADO DEL CEREBRO AUTÓNOMO:")
        print(f"   • Estado Sistema:       {controller['system_state'].upper()}")
        
        consciousness = controller['consciousness']
        print(f"   • Nivel Conciencia:     {consciousness['awareness_level']:.1%}")
        print(f"   • Procesos Activos:     {len(consciousness['active_processes'])}")
        print(f"   • Decisiones Pendientes: {controller['pending_decisions']}")
        print(f"   • Historial Decisiones: {controller['decision_history_size']}")
        
        # Salud del sistema
        system_health = consciousness['system_health']
        print("   • Salud del Sistema:")
        for metric, value in system_health.items():
            if isinstance(value, (int, float)):
                if metric == 'memory_utilization':
                    emoji = "🔴" if value > 0.8 else "🟡" if value > 0.6 else "🟢"
                    print(f"     - {metric}: {value:.1%} {emoji}")
                else:
                    emoji = "🟢" if value > 0.7 else "🟡" if value > 0.4 else "🔴"
                    print(f"     - {metric}: {value:.1%} {emoji}")
        
        print()

    def _print_intelligence_status(self, intelligence: dict):
        """Imprime el estado del sistema de inteligencia."""
        print("🔮 ESTADO DE INTELIGENCIA:")
        print(f"   • Dominios Aprendidos:   {intelligence['domains_learned']}")
        print(f"   • Sesiones Totales:      {intelligence['total_sessions']}")
        print(f"   • Tasa Éxito Promedio:   {intelligence['avg_success_rate']:.1%}")
        print(f"   • Patrones Identificados: {intelligence['patterns_identified']}")
        print(f"   • Estrategias Optimizadas: {intelligence['strategies_optimized']}")
        print(f"   • Último Aprendizaje:    {intelligence['last_learning']}")
        print(f"   • Tipo de Cerebro:       {intelligence.get('brain_type', 'unknown').upper()}")
        
        # Dominios top si están disponibles
        if 'top_domains' in intelligence and intelligence['top_domains']:
            print(f"   • Top Dominios:          {', '.join(intelligence['top_domains'])}")
        
        print()

    def _format_uptime(self, seconds: float) -> str:
        """Formatea tiempo de actividad."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"

    async def autonomous_scrape(self, targets: List[str], objectives: List[str] = None):
        """Realiza scraping autónomo."""
        print(f"🎯 Iniciando scraping autónomo de {len(targets)} objetivos...")
        print("🧠 El cerebro AI determinará la mejor estrategia...")
        
        try:
            if not self.coordinator:
                # Iniciar sistema automáticamente si no está activo
                await self.start_system()
            
            # Ejecutar scraping autónomo
            results = await self.coordinator.scrape_autonomous(targets, objectives)
            
            self._print_scraping_results(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Error en scraping autónomo: {e}")
            return None

    def _print_scraping_results(self, results: dict):
        """Imprime los resultados del scraping."""
        print("\n" + "="*50)
        print("📊 RESULTADOS DEL SCRAPING AUTÓNOMO")
        print("="*50)
        
        print(f"🎯 Plan ID:           {results['plan_id']}")
        print(f"⏱️  Duración:          {results['duration']:.2f}s")
        print(f"📈 Objetivos Totales: {results['total_targets']}")
        print(f"✅ Exitosos:          {results['successful_targets']}")
        print(f"❌ Fallidos:          {results['failed_targets']}")
        print(f"📊 Tasa de Éxito:     {results['success_rate']:.1%}")
        
        if results.get('autonomous_adaptations', 0) > 0:
            print(f"🔄 Adaptaciones:      {results['autonomous_adaptations']}")
        
        print()
        
        # Mostrar resultados individuales
        if results['results']:
            print("📋 RESULTADOS DETALLADOS:")
            for i, result in enumerate(results['results'], 1):
                status = "✅" if result.get('success', False) else "❌"
                target = result.get('target', 'Unknown')
                
                print(f"   {i}. {status} {target}")
                
                if result.get('success', False):
                    if 'intelligence_used' in result:
                        print(f"      🧠 Inteligencia: {result['intelligence_used']}")
                    if 'response_time' in result:
                        print(f"      ⏱️  Tiempo: {result['response_time']:.2f}s")
                else:
                    if 'error' in result:
                        print(f"      ❌ Error: {result['error']}")
        
        print("="*50)

    async def enable_full_autonomy(self):
        """Activa autonomía completa."""
        print("🔓 ACTIVANDO AUTONOMÍA COMPLETA...")
        print("🤖 El cerebro AI tomará control total del sistema")
        print("⚠️  El sistema operará de manera completamente independiente")
        
        try:
            if not self.coordinator:
                self.coordinator = get_autonomous_coordinator()
            
            await self.coordinator.enable_full_autonomy()
            
            print("✅ Autonomía completa activada")
            print("🧠 El sistema ahora es completamente independiente")
            
        except Exception as e:
            print(f"❌ Error activando autonomía completa: {e}")

    async def enable_transcendent_mode(self):
        """Activa modo trascendente."""
        print("🔮 ACTIVANDO MODO TRASCENDENTE...")
        print("⚠️  ATENCIÓN: Este modo permite al AI operar más allá de supervisión humana")
        print("🚨 Solo usar en entornos controlados")
        
        try:
            if not self.coordinator:
                self.coordinator = get_autonomous_coordinator()
            
            await self.coordinator.enable_transcendent_mode()
            
        except Exception as e:
            print(f"❌ Error activando modo trascendente: {e}")

    async def interactive_mode(self):
        """Modo interactivo para control del sistema."""
        print("🤖 MODO INTERACTIVO DEL SISTEMA AUTÓNOMO")
        print("Comandos disponibles:")
        print("  start    - Iniciar sistema")
        print("  stop     - Detener sistema")
        print("  status   - Mostrar estado")
        print("  scrape   - Scraping autónomo")
        print("  full     - Autonomía completa")
        print("  trans    - Modo trascendente")
        print("  help     - Mostrar ayuda")
        print("  exit     - Salir")
        print()
        
        while True:
            try:
                command = input("🤖 autonomous> ").strip().lower()
                
                if command == "exit":
                    break
                elif command == "start":
                    await self.start_system()
                elif command == "stop":
                    await self.stop_system()
                elif command == "status":
                    await self.show_status()
                elif command == "scrape":
                    url = input("URL a scrapear: ").strip()
                    if url:
                        await self.autonomous_scrape([url])
                elif command == "full":
                    await self.enable_full_autonomy()
                elif command == "trans":
                    await self.enable_transcendent_mode()
                elif command == "help":
                    print("Comandos: start, stop, status, scrape, full, trans, help, exit")
                elif command == "":
                    continue
                else:
                    print(f"Comando desconocido: {command}")
                    
            except KeyboardInterrupt:
                print("\n🛑 Interrumpido por usuario")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Asegurar parada limpia
        if self.coordinator and self.coordinator.is_running:
            await self.stop_system()


async def main():
    """Función principal de la CLI."""
    parser = argparse.ArgumentParser(
        description="Sistema de Scraping Autónomo - Control AI Independiente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python autonomous_cli.py start                    # Iniciar sistema
  python autonomous_cli.py status                   # Ver estado
  python autonomous_cli.py scrape https://example.com
  python autonomous_cli.py full-autonomy            # Control total AI
  python autonomous_cli.py interactive              # Modo interactivo
        """
    )
    
    parser.add_argument('command', nargs='?', default='interactive',
                       choices=['start', 'stop', 'status', 'scrape', 'full-autonomy', 
                               'transcendent', 'interactive'],
                       help='Comando a ejecutar')
    
    parser.add_argument('targets', nargs='*', 
                       help='URLs objetivo para scraping')
    
    parser.add_argument('--autonomy-level', 
                       choices=['supervised', 'semi', 'fully_autonomous', 'transcendent'],
                       default='fully_autonomous',
                       help='Nivel de autonomía del sistema')
    
    parser.add_argument('--objectives', nargs='+',
                       help='Objetivos para scraping autónomo')
    
    args = parser.parse_args()
    
    cli = AutonomousCLI()
    
    try:
        if args.command == 'start':
            await cli.start_system(args.autonomy_level)
            
        elif args.command == 'stop':
            await cli.stop_system()
            
        elif args.command == 'status':
            await cli.show_status()
            
        elif args.command == 'scrape':
            if not args.targets:
                print("❌ Se requiere al menos una URL para scraping")
                sys.exit(1)
            
            await cli.autonomous_scrape(args.targets, args.objectives)
            
        elif args.command == 'full-autonomy':
            await cli.enable_full_autonomy()
            
        elif args.command == 'transcendent':
            await cli.enable_transcendent_mode()
            
        elif args.command == 'interactive':
            await cli.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n🛑 Operación cancelada por usuario")
        if cli.coordinator and cli.coordinator.is_running:
            await cli.stop_system()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Crear directorio de logs
    os.makedirs('logs', exist_ok=True)
    
    # Ejecutar CLI
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Programa terminado por usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)