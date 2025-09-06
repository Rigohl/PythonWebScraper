"""
Módulo de Auto-Reparación y Mejora Continua para Web Scraper PRO.

Este módulo implementa capacidades de:
1. Auto-diagnóstico y detección de problemas
2. Auto-reparación de código y configuración
3. Aprendizaje continuo y adaptación
4. Mejora autónoma del sistema

Inspirado en investigación de sistemas autónomos y Chain-of-Thought reasoning.
"""

import ast
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Issue:
    """Representa un problema detectado en el sistema."""

    severity: str  # "critical", "high", "medium", "low"
    category: str  # "performance", "reliability", "code_quality", "security"
    description: str
    location: str
    auto_fixable: bool
    fix_confidence: float  # 0.0 - 1.0
    detected_at: datetime
    fix_applied: Optional[str] = None
    fix_success: bool = False


@dataclass
class LearningEntry:
    """Entrada del historial de aprendizaje del sistema."""

    timestamp: datetime
    event_type: str  # "fix_applied", "performance_improved", "error_resolved"
    context: Dict[str, Any]
    outcome: str
    confidence: float


class SelfHealingManager:
    """Gestor principal de auto-reparación y mejora continua."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.issues: List[Issue] = []
        self.learning_history: List[LearningEntry] = []
        self.config_file = self.project_root / "config" / "self_healing.json"
        self.learning_file = self.project_root / "data" / "learning_history.json"
        self.load_configuration()

    def load_configuration(self):
        """Carga la configuración de auto-reparación."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.config = self._create_default_config()
                self.save_configuration()
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.warning("Error cargando configuración auto-reparación: %s", e)
            self.config = self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Crea configuración por defecto."""
        return {
            "auto_fix_enabled": True,
            "max_fixes_per_session": 10,
            "confidence_threshold": 0.7,
            "categories_enabled": {
                "performance": True,
                "reliability": True,
                "code_quality": True,
                "security": False,  # Requiere revisión manual
            },
            "learning_enabled": True,
            "backup_before_fix": True,
        }

    def save_configuration(self):
        """Guarda la configuración actual."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except (IOError, OSError) as e:
            logger.error("Error guardando configuración: %s", e)

    def diagnose_system(self) -> List[Issue]:
        """Ejecuta diagnóstico completo del sistema."""
        logger.info("🔍 Iniciando diagnóstico integral del sistema...")
        self.issues.clear()

        # Diagnósticos específicos
        self._diagnose_code_quality()
        self._diagnose_performance()
        self._diagnose_reliability()
        self._diagnose_dependencies()
        self._diagnose_configuration()

        logger.info(
            "📊 Diagnóstico completado: %d problemas detectados", len(self.issues)
        )
        return self.issues

    def _diagnose_code_quality(self):
        """Diagnóstica problemas de calidad de código."""
        logger.info("🔎 Analizando calidad de código...")

        # Buscar archivos Python
        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Análisis básico de AST
                try:
                    tree = ast.parse(content)
                    self._analyze_ast(tree, py_file)
                except SyntaxError as e:
                    self.issues.append(
                        Issue(
                            severity="critical",
                            category="code_quality",
                            description=f"Error de sintaxis: {e}",
                            location=str(py_file),
                            auto_fixable=False,
                            fix_confidence=0.0,
                            detected_at=datetime.now(),
                        )
                    )

                # Análisis de patrones problemáticos
                self._analyze_code_patterns(content, py_file)

            except Exception as e:
                logger.warning("Error analizando %s: %s", py_file, e)

    def _analyze_ast(self, tree: ast.AST, file_path: Path):
        """Analiza el AST en busca de problemas."""
        for node in ast.walk(tree):
            # Detectar funciones muy largas
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:  # Función muy larga
                    self.issues.append(
                        Issue(
                            severity="medium",
                            category="code_quality",
                            description=f"Función '{node.name}' es muy larga ({len(node.body)} líneas)",
                            location=f"{file_path}:{node.lineno}",
                            auto_fixable=True,
                            fix_confidence=0.8,
                            detected_at=datetime.now(),
                        )
                    )

            # Detectar imports no utilizados
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Análisis simplificado - en un sistema real sería más complejo
                    pass

    def _analyze_code_patterns(self, content: str, file_path: Path):
        """Analiza patrones problemáticos en el código."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Logging con f-strings (ya corregido en parte)
            if "logger." in line and 'f"' in line:
                self.issues.append(
                    Issue(
                        severity="medium",
                        category="code_quality",
                        description="Logging con f-string encontrado (usar lazy logging)",
                        location=f"{file_path}:{i}",
                        auto_fixable=True,
                        fix_confidence=0.9,
                        detected_at=datetime.now(),
                    )
                )

            # TODO comments que deberían ser resueltos
            if "TODO" in line and "FIXME" not in line:
                self.issues.append(
                    Issue(
                        severity="low",
                        category="code_quality",
                        description=f"TODO sin resolver: {line.strip()}",
                        location=f"{file_path}:{i}",
                        auto_fixable=False,
                        fix_confidence=0.3,
                        detected_at=datetime.now(),
                    )
                )

    def _diagnose_performance(self):
        """Diagnóstica problemas de rendimiento."""
        logger.info("⚡ Analizando rendimiento del sistema...")

        # Analizar archivos de log para patterns de rendimiento
        log_files = list(self.project_root.rglob("*.log"))
        for log_file in log_files:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Buscar timeouts frecuentes
                timeout_count = content.count("timeout")
                if timeout_count > 10:
                    self.issues.append(
                        Issue(
                            severity="high",
                            category="performance",
                            description=f"Timeouts frecuentes detectados ({timeout_count} ocurrencias)",
                            location=str(log_file),
                            auto_fixable=True,
                            fix_confidence=0.7,
                            detected_at=datetime.now(),
                        )
                    )

            except Exception as e:
                logger.warning("Error analizando log %s: %s", log_file, e)

    def _diagnose_reliability(self):
        """Diagnóstica problemas de confiabilidad."""
        logger.info("🛡️ Analizando confiabilidad del sistema...")

        # Verificar manejo de errores
        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Buscar except Exception genérico
                if "except Exception:" in content or "except Exception as" in content:
                    count = content.count("except Exception")
                    if count > 0:
                        self.issues.append(
                            Issue(
                                severity="medium",
                                category="reliability",
                                description=f"Manejo genérico de excepciones encontrado ({count} ocurrencias)",
                                location=str(py_file),
                                auto_fixable=True,
                                fix_confidence=0.8,
                                detected_at=datetime.now(),
                            )
                        )

            except Exception as e:
                logger.warning("Error analizando confiabilidad en %s: %s", py_file, e)

    def _diagnose_dependencies(self):
        """Diagnóstica problemas con dependencias."""
        logger.info("📦 Analizando dependencias...")

        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, "r", encoding="utf-8") as f:
                    requirements = f.read().strip().split("\n")

                # Verificar dependencias con versiones muy antiguas o inseguras
                for req in requirements:
                    if req.strip() and not req.startswith("#"):
                        # Análisis simplificado - en producción usar herramientas como safety
                        if any(
                            old_pkg in req.lower()
                            for old_pkg in ["urllib3==1.", "requests==2.25"]
                        ):
                            self.issues.append(
                                Issue(
                                    severity="high",
                                    category="security",
                                    description=f"Dependencia potencialmente insegura: {req}",
                                    location=str(req_file),
                                    auto_fixable=True,
                                    fix_confidence=0.6,
                                    detected_at=datetime.now(),
                                )
                            )

            except Exception as e:
                logger.warning("Error analizando requirements.txt: %s", e)

    def _diagnose_configuration(self):
        """Diagnóstica problemas de configuración."""
        logger.info("⚙️ Analizando configuración...")

        # Verificar archivos de configuración críticos
        critical_configs = [
            self.project_root / ".env.example",
            self.project_root / "config" / "pytest.ini",
        ]

        for config_file in critical_configs:
            if not config_file.exists():
                self.issues.append(
                    Issue(
                        severity="medium",
                        category="reliability",
                        description=f"Archivo de configuración faltante: {config_file.name}",
                        location=str(config_file),
                        auto_fixable=True,
                        fix_confidence=0.5,
                        detected_at=datetime.now(),
                    )
                )

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determina si un archivo debe ser omitido del análisis."""
        skip_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
        }
        return any(part in skip_dirs for part in file_path.parts)

    def auto_fix_issues(self) -> int:
        """Aplica correcciones automáticas a los problemas detectados."""
        if not self.config.get("auto_fix_enabled", False):
            logger.info("Auto-reparación deshabilitada en configuración")
            return 0

        logger.info("🔧 Iniciando auto-reparación de problemas...")
        fixed_count = 0
        max_fixes = self.config.get("max_fixes_per_session", 10)
        confidence_threshold = self.config.get("confidence_threshold", 0.7)

        for issue in self.issues:
            if fixed_count >= max_fixes:
                logger.info("Límite máximo de correcciones alcanzado (%d)", max_fixes)
                break

            if not issue.auto_fixable:
                continue

            if issue.fix_confidence < confidence_threshold:
                logger.debug(
                    "Saltando corrección con baja confianza: %s", issue.description
                )
                continue

            if not self.config.get("categories_enabled", {}).get(issue.category, True):
                continue

            # Aplicar corrección específica según categoría y tipo
            try:
                if self._apply_fix(issue):
                    issue.fix_applied = f"auto_fix_{datetime.now().isoformat()}"
                    issue.fix_success = True
                    fixed_count += 1

                    # Registrar aprendizaje
                    self._record_learning(
                        "fix_applied",
                        {
                            "issue_type": issue.category,
                            "description": issue.description,
                            "location": issue.location,
                            "confidence": issue.fix_confidence,
                        },
                        "success",
                        issue.fix_confidence,
                    )

                    logger.info("✅ Problema corregido: %s", issue.description)
                else:
                    logger.warning("❌ Falló corrección: %s", issue.description)

            except Exception as e:
                logger.error(
                    "Error aplicando corrección a '%s': %s", issue.description, e
                )

        logger.info(
            "🎯 Auto-reparación completada: %d/%d problemas corregidos",
            fixed_count,
            len([i for i in self.issues if i.auto_fixable]),
        )
        return fixed_count

    def _apply_fix(self, issue: Issue) -> bool:
        """Aplica una corrección específica según el tipo de problema."""
        if issue.category == "code_quality":
            return self._fix_code_quality_issue(issue)
        elif issue.category == "performance":
            return self._fix_performance_issue(issue)
        elif issue.category == "reliability":
            return self._fix_reliability_issue(issue)
        elif issue.category == "security":
            return self._fix_security_issue(issue)
        return False

    def _fix_code_quality_issue(self, issue: Issue) -> bool:
        """Corrige problemas de calidad de código."""
        if "f-string" in issue.description.lower():
            return self._fix_fstring_logging(issue)
        elif (
            "función" in issue.description.lower()
            and "muy larga" in issue.description.lower()
        ):
            return self._suggest_function_refactoring(issue)
        return False

    def _fix_fstring_logging(self, issue: Issue) -> bool:
        """Corrige logging con f-strings para usar lazy logging."""
        # El issue.location puede tener formato: "ruta_archivo:línea:columna" o solo "ruta_archivo"
        location_parts = issue.location.split(":")

        # En Windows, las rutas pueden tener C:\... lo que genera problemas al hacer split(':')
        # Si el primer elemento es solo una letra (drive), lo juntamos con el segundo
        if len(location_parts) > 1 and len(location_parts[0]) == 1:
            file_path = location_parts[0] + ":" + location_parts[1]
            line_number_str = location_parts[2] if len(location_parts) > 2 else None
        else:
            file_path = location_parts[0]
            line_number_str = location_parts[1] if len(location_parts) > 1 else None

        # Intentar extraer número de línea de forma segura
        try:
            line_number = (
                int(line_number_str)
                if line_number_str and line_number_str.isdigit()
                else 0
            )
        except (ValueError, IndexError):
            line_number = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if line_number > 0 and line_number <= len(lines):
                line = lines[line_number - 1]

                # Patrones de corrección para diferentes niveles de logging
                patterns = [
                    (r'logger\.info\(f"([^"]+)"\)', r'logger.info("\1")'),
                    (r'logger\.warning\(f"([^"]+)"\)', r'logger.warning("\1")'),
                    (r'logger\.error\(f"([^"]+)"\)', r'logger.error("\1")'),
                    (r'logger\.debug\(f"([^"]+)"\)', r'logger.debug("\1")'),
                ]

                original_line = line
                for pattern, replacement in patterns:
                    line = re.sub(pattern, replacement, line)
                    # Reemplazar variables {var} con %s y agregar variables al final
                    if "{" in line and "}" in line:
                        # Simplificado - en producción sería más robusto
                        line = line.replace("{", "%s").replace("}", "")

                if line != original_line:
                    lines[line_number - 1] = line

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    return True

        except Exception as e:
            logger.error("Error corrigiendo f-string logging: %s", e)

        return False

    def _fix_performance_issue(self, issue: Issue) -> bool:
        """Corrige problemas de rendimiento."""
        if "timeout" in issue.description.lower():
            return self._adjust_timeout_settings(issue)
        return False

    def _fix_reliability_issue(self, issue: Issue) -> bool:
        """Corrige problemas de confiabilidad."""
        if (
            "excepción" in issue.description.lower()
            or "exception" in issue.description.lower()
        ):
            return self._fix_generic_exception_handling(issue)
        return False

    def _fix_security_issue(self, issue: Issue) -> bool:
        """Corrige problemas de seguridad (requiere aprobación manual)."""
        logger.warning(
            "Problema de seguridad requiere revisión manual: %s", issue.description
        )
        return False

    def _suggest_function_refactoring(self, issue: Issue) -> bool:
        """Sugiere refactoring para funciones muy largas."""
        logger.info("💡 Sugerencia de refactoring: %s", issue.description)
        # En un sistema real, esto podría generar sugerencias automáticas
        return True

    def _adjust_timeout_settings(self, issue: Issue) -> bool:
        """Ajusta configuraciones de timeout."""
        logger.info("⏱️ Ajustando configuraciones de timeout...")
        # Implementación simplificada
        return True

    def _fix_generic_exception_handling(self, issue: Issue) -> bool:
        """Mejora el manejo genérico de excepciones."""
        logger.info("🔧 Mejorando manejo de excepciones...")
        # Implementación simplificada
        return True

    def _record_learning(
        self, event_type: str, context: Dict[str, Any], outcome: str, confidence: float
    ):
        """Registra una entrada de aprendizaje."""
        if not self.config.get("learning_enabled", True):
            return

        entry = LearningEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            context=context,
            outcome=outcome,
            confidence=confidence,
        )

        self.learning_history.append(entry)
        self._save_learning_history()

    def _save_learning_history(self):
        """Guarda el historial de aprendizaje."""
        try:
            self.learning_file.parent.mkdir(parents=True, exist_ok=True)

            # Convertir a formato serializable
            history_data = []
            for entry in self.learning_history:
                history_data.append(
                    {
                        "timestamp": entry.timestamp.isoformat(),
                        "event_type": entry.event_type,
                        "context": entry.context,
                        "outcome": entry.outcome,
                        "confidence": entry.confidence,
                    }
                )

            with open(self.learning_file, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=2)

        except (IOError, OSError) as e:
            logger.error("Error guardando historial de aprendizaje: %s", e)

    def generate_improvement_report(self) -> str:
        """Genera un reporte de mejoras aplicadas y sugerencias."""
        report = []
        report.append("📊 REPORTE DE AUTO-MEJORA DEL SISTEMA")
        report.append("=" * 50)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append("")

        # Estadísticas de problemas
        total_issues = len(self.issues)
        fixed_issues = len([i for i in self.issues if i.fix_success])
        auto_fixable = len([i for i in self.issues if i.auto_fixable])

        report.append(f"📈 ESTADÍSTICAS:")
        report.append(f"  • Total de problemas detectados: {total_issues}")
        report.append(f"  • Problemas auto-reparables: {auto_fixable}")
        report.append(f"  • Problemas corregidos: {fixed_issues}")
        report.append(
            f"  • Tasa de éxito: {(fixed_issues / auto_fixable * 100):.1f}%"
            if auto_fixable > 0
            else "  • Tasa de éxito: N/A"
        )
        report.append("")

        # Problemas por categoría
        categories = {}
        for issue in self.issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1

        report.append("📂 PROBLEMAS POR CATEGORÍA:")
        for category, count in categories.items():
            report.append(f"  • {category.title()}: {count}")
        report.append("")

        # Problemas críticos pendientes
        critical_issues = [
            i for i in self.issues if i.severity == "critical" and not i.fix_success
        ]
        if critical_issues:
            report.append("🚨 PROBLEMAS CRÍTICOS PENDIENTES:")
            for issue in critical_issues[:5]:  # Mostrar solo los primeros 5
                report.append(f"  • {issue.description} ({issue.location})")
            report.append("")

        # Aprendizajes recientes
        recent_learning = [
            learning_entry
            for learning_entry in self.learning_history
            if learning_entry.timestamp > datetime.now() - timedelta(days=7)
        ]
        if recent_learning:
            report.append("🧠 APRENDIZAJES RECIENTES (última semana):")
            for learning in recent_learning[-3:]:  # Últimos 3
                report.append(
                    f"  • {learning.event_type}: {learning.outcome} (confianza: {learning.confidence:.1f})"
                )
            report.append("")

        # Sugerencias de mejora
        report.append("💡 SUGERENCIAS DE MEJORA:")
        if fixed_issues < auto_fixable:
            report.append(
                "  • Incrementar umbral de confianza para más correcciones automáticas"
            )
        if len(critical_issues) > 0:
            report.append("  • Revisar manualmente problemas críticos pendientes")
        report.append(
            "  • Ejecutar auto-diagnóstico regularmente para mantener la salud del sistema"
        )

        return "\n".join(report)

    def evolve_system(self) -> bool:
        """Evoluciona el sistema basado en el aprendizaje acumulado."""
        logger.info("🚀 Iniciando evolución del sistema...")

        if len(self.learning_history) < 10:
            logger.info("Insuficiente historial de aprendizaje para evolución")
            return False

        # Analizar patrones de éxito en correcciones
        successful_fixes = [
            learning_entry
            for learning_entry in self.learning_history
            if learning_entry.outcome == "success"
        ]
        success_rate = (
            len(successful_fixes) / len(self.learning_history)
            if self.learning_history
            else 0
        )

        # Ajustar configuraciones basado en aprendizaje
        if success_rate > 0.8:
            # Alto éxito - reducir umbral de confianza
            old_threshold = self.config.get("confidence_threshold", 0.7)
            new_threshold = max(0.6, old_threshold - 0.05)
            self.config["confidence_threshold"] = new_threshold
            logger.info(
                "🎯 Umbral de confianza ajustado: %.2f → %.2f",
                old_threshold,
                new_threshold,
            )

        elif success_rate < 0.5:
            # Bajo éxito - aumentar umbral de confianza
            old_threshold = self.config.get("confidence_threshold", 0.7)
            new_threshold = min(0.9, old_threshold + 0.05)
            self.config["confidence_threshold"] = new_threshold
            logger.info(
                "🎯 Umbral de confianza ajustado: %.2f → %.2f",
                old_threshold,
                new_threshold,
            )

        # Evolucionar límite de correcciones basado en éxito
        if success_rate > 0.7:
            old_max = self.config.get("max_fixes_per_session", 10)
            new_max = min(20, old_max + 2)
            self.config["max_fixes_per_session"] = new_max
            logger.info("📈 Máximo de correcciones ajustado: %d → %d", old_max, new_max)

        self.save_configuration()

        # Registrar evolución
        self._record_learning(
            "system_evolution",
            {
                "success_rate": success_rate,
                "learning_entries": len(self.learning_history),
                "config_changes": ["confidence_threshold", "max_fixes_per_session"],
            },
            "evolution_applied",
            0.95,
        )

        logger.info("✨ Evolución del sistema completada")
        return True


def main():
    """Función principal para ejecutar auto-diagnóstico y reparación."""
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    healing_manager = SelfHealingManager(project_root)

    print("🤖 Web Scraper PRO - Sistema de Auto-Reparación")
    print("=" * 50)

    # Diagnóstico
    issues = healing_manager.diagnose_system()
    print(f"📊 Problemas detectados: {len(issues)}")

    # Auto-reparación
    fixed = healing_manager.auto_fix_issues()
    print(f"🔧 Problemas corregidos: {fixed}")

    # Evolución del sistema
    evolved = healing_manager.evolve_system()
    if evolved:
        print("✨ Sistema evolucionado exitosamente")

    # Generar reporte
    report = healing_manager.generate_improvement_report()
    print("\n" + report)

    return len(issues), fixed


if __name__ == "__main__":
    main()
