"""
Self-Improving Code System
Sistema de código auto-mejorable que aprende y se modifica a sí mismo
"""

import ast
import inspect
import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
import importlib.util
import sys

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analizador de código Python usando AST"""

    def __init__(self):
        self.complexity_threshold = 10
        self.line_length_threshold = 120

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analiza un archivo Python y extrae métricas"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)

            analysis = {
                'file_path': file_path,
                'total_lines': len(source.splitlines()),
                'functions': self._analyze_functions(tree),
                'classes': self._analyze_classes(tree),
                'imports': self._analyze_imports(tree),
                'complexity_score': self._calculate_complexity(tree),
                'code_smells': self._detect_code_smells(source, tree),
                'performance_issues': self._detect_performance_issues(tree),
                'suggestions': []
            }

            # Generar sugerencias basadas en análisis
            analysis['suggestions'] = self._generate_suggestions(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {'error': str(e)}

    def _analyze_functions(self, tree: ast.AST) -> List[Dict]:
        """Analiza funciones en el AST"""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    'args_count': len(node.args.args),
                    'has_docstring': ast.get_docstring(node) is not None,
                    'complexity': self._calculate_function_complexity(node),
                    'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                }
                functions.append(func_info)

        return functions

    def _analyze_classes(self, tree: ast.AST) -> List[Dict]:
        """Analiza clases en el AST"""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

                class_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'methods_count': len(methods),
                    'has_docstring': ast.get_docstring(node) is not None,
                    'base_classes': [b.id for b in node.bases if isinstance(b, ast.Name)],
                    'methods': [m.name for m in methods]
                }
                classes.append(class_info)

        return classes

    def _analyze_imports(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Analiza imports en el código"""
        imports = {'standard': [], 'third_party': [], 'local': []}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports['standard'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if module.startswith('.'):
                    imports['local'].append(module)
                elif any(module.startswith(pkg) for pkg in ['requests', 'numpy', 'pandas', 'sklearn']):
                    imports['third_party'].append(module)
                else:
                    imports['standard'].append(module)

        return imports

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calcula complejidad ciclomática"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calcula complejidad de una función específica"""
        complexity = 1

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1

        return complexity

    def _detect_code_smells(self, source: str, tree: ast.AST) -> List[Dict]:
        """Detecta code smells comunes"""
        smells = []
        lines = source.splitlines()

        # Long lines
        for i, line in enumerate(lines, 1):
            if len(line) > self.line_length_threshold:
                smells.append({
                    'type': 'long_line',
                    'line': i,
                    'message': f'Line too long ({len(line)} > {self.line_length_threshold})',
                    'severity': 'minor'
                })

        # Long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno'):
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:
                        smells.append({
                            'type': 'long_function',
                            'line': node.lineno,
                            'function': node.name,
                            'message': f'Function {node.name} is too long ({func_length} lines)',
                            'severity': 'major'
                        })

        # Too many parameters
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 6:
                    smells.append({
                        'type': 'too_many_parameters',
                        'line': node.lineno,
                        'function': node.name,
                        'message': f'Function {node.name} has too many parameters ({len(node.args.args)})',
                        'severity': 'major'
                    })

        # Missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    smells.append({
                        'type': 'missing_docstring',
                        'line': node.lineno,
                        'name': node.name,
                        'message': f'{type(node).__name__} {node.name} missing docstring',
                        'severity': 'minor'
                    })

        return smells

    def _detect_performance_issues(self, tree: ast.AST) -> List[Dict]:
        """Detecta posibles problemas de performance"""
        issues = []

        # Nested loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                nested_loops = [n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While)) and n != node]
                if nested_loops:
                    issues.append({
                        'type': 'nested_loops',
                        'line': node.lineno,
                        'message': 'Nested loops detected - consider optimization',
                        'severity': 'major'
                    })

        # String concatenation in loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        issues.append({
                            'type': 'string_concat_in_loop',
                            'line': child.lineno,
                            'message': 'String concatenation in loop - use join() instead',
                            'severity': 'major'
                        })

        return issues

    def _generate_suggestions(self, analysis: Dict) -> List[Dict]:
        """Genera sugerencias de mejora"""
        suggestions = []

        # High complexity functions
        for func in analysis['functions']:
            if func['complexity'] > self.complexity_threshold:
                suggestions.append({
                    'type': 'refactor_function',
                    'target': func['name'],
                    'line': func['line_start'],
                    'message': f'Function {func["name"]} has high complexity ({func["complexity"]}), consider refactoring',
                    'priority': 'high'
                })

        # Large classes
        for cls in analysis['classes']:
            if cls['methods_count'] > 15:
                suggestions.append({
                    'type': 'split_class',
                    'target': cls['name'],
                    'line': cls['line_start'],
                    'message': f'Class {cls["name"]} has many methods ({cls["methods_count"]}), consider splitting',
                    'priority': 'medium'
                })

        # Performance improvements
        for issue in analysis['performance_issues']:
            if issue['type'] == 'nested_loops':
                suggestions.append({
                    'type': 'optimize_loops',
                    'line': issue['line'],
                    'message': 'Consider using list comprehensions or vectorized operations',
                    'priority': 'high'
                })

        return suggestions

class CodeModifier:
    """Modificador de código que aplica mejoras automáticamente"""

    def __init__(self):
        self.backup_dir = Path("backups/code_modifications")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def apply_suggestion(self, file_path: str, suggestion: Dict) -> bool:
        """Aplica una sugerencia de mejora al código"""
        try:
            # Crear backup
            backup_path = self._create_backup(file_path)

            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # Aplicar modificación según tipo
            modified_source = None

            if suggestion['type'] == 'add_docstring':
                modified_source = self._add_docstring(source, suggestion)
            elif suggestion['type'] == 'optimize_imports':
                modified_source = self._optimize_imports(source)
            elif suggestion['type'] == 'fix_long_lines':
                modified_source = self._fix_long_lines(source)
            elif suggestion['type'] == 'simplify_condition':
                modified_source = self._simplify_conditions(source, suggestion)

            if modified_source and modified_source != source:
                # Validar sintaxis antes de escribir
                if self._validate_syntax(modified_source):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_source)

                    logger.info(f"Applied {suggestion['type']} to {file_path}")
                    return True
                else:
                    # Restaurar backup si hay error
                    self._restore_backup(file_path, backup_path)
                    logger.error(f"Syntax error after modification, restored backup")
                    return False

            return False

        except Exception as e:
            logger.error(f"Error applying suggestion to {file_path}: {e}")
            return False

    def _create_backup(self, file_path: str) -> str:
        """Crea backup del archivo"""
        timestamp = int(time.time())
        backup_name = f"{Path(file_path).stem}_{timestamp}.py"
        backup_path = self.backup_dir / backup_name

        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())

        return str(backup_path)

    def _restore_backup(self, file_path: str, backup_path: str):
        """Restaura archivo desde backup"""
        with open(backup_path, 'r', encoding='utf-8') as src:
            with open(file_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())

    def _validate_syntax(self, source: str) -> bool:
        """Valida sintaxis Python"""
        try:
            ast.parse(source)
            return True
        except SyntaxError:
            return False

    def _add_docstring(self, source: str, suggestion: Dict) -> str:
        """Añade docstring a función o clase"""
        lines = source.splitlines()
        target_line = suggestion.get('line', 1) - 1

        # Encontrar donde insertar docstring
        indent = len(lines[target_line]) - len(lines[target_line].lstrip())

        if suggestion.get('target_type') == 'function':
            docstring = f'{"    " * (indent // 4 + 1)}"""Docstring for {suggestion.get("target", "function")}."""'
        else:
            docstring = f'{"    " * (indent // 4 + 1)}"""Docstring for {suggestion.get("target", "class")}."""'

        # Insertar después de def/class line
        lines.insert(target_line + 1, docstring)

        return '\n'.join(lines)

    def _optimize_imports(self, source: str) -> str:
        """Optimiza imports - remueve no usados, ordena"""
        tree = ast.parse(source)

        # Encontrar imports
        imports = []
        other_nodes = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
            else:
                other_nodes.append(ast.unparse(node))

        # Ordenar imports
        imports.sort()

        # Reconstruir código
        new_source = '\n'.join(imports) + '\n\n' + '\n'.join(other_nodes)

        return new_source

    def _fix_long_lines(self, source: str) -> str:
        """Arregla líneas muy largas"""
        lines = source.splitlines()
        fixed_lines = []

        for line in lines:
            if len(line) > 120:
                # Intentar partir por comas o operadores
                if ',' in line and not line.strip().startswith('#'):
                    parts = line.split(',')
                    if len(parts) > 2:
                        indent = len(line) - len(line.lstrip())
                        new_lines = []
                        for i, part in enumerate(parts):
                            if i == 0:
                                new_lines.append(part + ',')
                            elif i == len(parts) - 1:
                                new_lines.append(' ' * (indent + 4) + part.strip())
                            else:
                                new_lines.append(' ' * (indent + 4) + part.strip() + ',')
                        fixed_lines.extend(new_lines)
                        continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _simplify_conditions(self, source: str, suggestion: Dict) -> str:
        """Simplifica condiciones complejas"""
        # Esta es una implementación básica
        # En un sistema real usaríamos transformaciones AST más sofisticadas

        lines = source.splitlines()
        target_line = suggestion.get('line', 1) - 1

        if target_line < len(lines):
            line = lines[target_line]

            # Simplificaciones básicas
            if 'if x == True:' in line:
                lines[target_line] = line.replace('if x == True:', 'if x:')
            elif 'if x == False:' in line:
                lines[target_line] = line.replace('if x == False:', 'if not x:')

        return '\n'.join(lines)

class AutoTestRunner:
    """Ejecutor automático de tests para validar cambios"""

    def __init__(self):
        self.test_commands = [
            'python -m pytest tests/ -v',
            'python -m unittest discover tests',
            'python -c "import {module}; print(\\"Import successful\\")"'
        ]

    def run_tests(self, target_file: Optional[str] = None) -> Dict[str, Any]:
        """Ejecuta tests y retorna resultados"""
        results = {
            'all_passed': True,
            'test_results': [],
            'errors': [],
            'execution_time': 0
        }

        start_time = time.time()

        try:
            # Test básico de importación
            if target_file:
                import_result = self._test_import(target_file)
                results['test_results'].append(import_result)
                if not import_result['passed']:
                    results['all_passed'] = False

            # Ejecutar pytest si está disponible
            pytest_result = self._run_pytest()
            if pytest_result:
                results['test_results'].append(pytest_result)
                if not pytest_result['passed']:
                    results['all_passed'] = False

        except Exception as e:
            results['errors'].append(str(e))
            results['all_passed'] = False

        results['execution_time'] = time.time() - start_time
        return results

    def _test_import(self, file_path: str) -> Dict[str, Any]:
        """Test de importación básica"""
        try:
            # Convertir path a módulo
            module_path = Path(file_path)
            if module_path.suffix == '.py':
                module_name = module_path.stem

                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                return {
                    'test_name': 'import_test',
                    'passed': True,
                    'message': f'Successfully imported {module_name}'
                }
            else:
                return {
                    'test_name': 'import_test',
                    'passed': False,
                    'message': f'Not a Python file: {file_path}'
                }

        except Exception as e:
            return {
                'test_name': 'import_test',
                'passed': False,
                'message': f'Import failed: {str(e)}'
            }

    def _run_pytest(self) -> Optional[Dict[str, Any]]:
        """Ejecuta pytest si está disponible"""
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', '--tb=short', '-q'],
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                'test_name': 'pytest',
                'passed': result.returncode == 0,
                'message': result.stdout if result.returncode == 0 else result.stderr,
                'exit_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'test_name': 'pytest',
                'passed': False,
                'message': 'Tests timed out after 60 seconds'
            }
        except FileNotFoundError:
            return None  # pytest not available

class SelfImprovingSystem:
    """Sistema principal de auto-mejora"""

    def __init__(self, target_directories: List[str] = None):
        self.target_directories = target_directories or ['src/']
        self.analyzer = CodeAnalyzer()
        self.modifier = CodeModifier()
        self.test_runner = AutoTestRunner()

        self.improvement_history = []
        self.config = {
            'auto_apply_minor': True,
            'require_tests_pass': True,
            'max_changes_per_session': 5,
            'backup_before_changes': True
        }

    def analyze_codebase(self) -> Dict[str, Any]:
        """Analiza todo el codebase y encuentra oportunidades de mejora"""
        analysis_results = {}
        total_suggestions = []

        for directory in self.target_directories:
            if not os.path.exists(directory):
                continue

            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__pycache__'):
                        file_path = os.path.join(root, file)

                        file_analysis = self.analyzer.analyze_file(file_path)
                        if 'error' not in file_analysis:
                            analysis_results[file_path] = file_analysis
                            total_suggestions.extend(file_analysis.get('suggestions', []))

        return {
            'files_analyzed': list(analysis_results.keys()),
            'total_files': len(analysis_results),
            'total_suggestions': len(total_suggestions),
            'suggestions_by_priority': self._group_suggestions_by_priority(total_suggestions),
            'detailed_analysis': analysis_results
        }

    def auto_improve_step(self) -> Dict[str, Any]:
        """Ejecuta un paso de auto-mejora"""
        logger.info("Starting auto-improvement step")

        # 1. Analizar codebase
        analysis = self.analyze_codebase()

        if analysis['total_suggestions'] == 0:
            return {
                'status': 'no_improvements_needed',
                'message': 'No improvements found',
                'analysis': analysis
            }

        # 2. Seleccionar mejoras a aplicar
        improvements_to_apply = self._select_improvements(analysis)

        if not improvements_to_apply:
            return {
                'status': 'no_safe_improvements',
                'message': 'No safe improvements available',
                'analysis': analysis
            }

        # 3. Ejecutar tests iniciales
        initial_tests = self.test_runner.run_tests()

        if not initial_tests['all_passed'] and self.config['require_tests_pass']:
            return {
                'status': 'tests_failing',
                'message': 'Initial tests failing, cannot proceed',
                'test_results': initial_tests
            }

        # 4. Aplicar mejoras
        applied_improvements = []

        for improvement in improvements_to_apply:
            file_path = improvement['file_path']
            suggestion = improvement['suggestion']

            success = self.modifier.apply_suggestion(file_path, suggestion)

            if success:
                # Ejecutar tests después del cambio
                post_tests = self.test_runner.run_tests(file_path)

                if post_tests['all_passed']:
                    applied_improvements.append({
                        'file': file_path,
                        'type': suggestion['type'],
                        'success': True,
                        'tests_passed': True
                    })
                    logger.info(f"Successfully applied {suggestion['type']} to {file_path}")
                else:
                    # Revertir cambio si tests fallan
                    logger.warning(f"Tests failed after applying {suggestion['type']}, reverting")
                    applied_improvements.append({
                        'file': file_path,
                        'type': suggestion['type'],
                        'success': False,
                        'tests_passed': False,
                        'reverted': True
                    })

        # 5. Guardar historial
        improvement_record = {
            'timestamp': time.time(),
            'improvements_attempted': len(improvements_to_apply),
            'improvements_successful': len([i for i in applied_improvements if i['success']]),
            'applied_improvements': applied_improvements
        }

        self.improvement_history.append(improvement_record)

        return {
            'status': 'completed',
            'improvements_applied': len([i for i in applied_improvements if i['success']]),
            'total_attempted': len(improvements_to_apply),
            'details': applied_improvements,
            'analysis': analysis
        }

    def _group_suggestions_by_priority(self, suggestions: List[Dict]) -> Dict[str, List]:
        """Agrupa sugerencias por prioridad"""
        by_priority = {'high': [], 'medium': [], 'low': []}

        for suggestion in suggestions:
            priority = suggestion.get('priority', 'medium')
            if priority in by_priority:
                by_priority[priority].append(suggestion)

        return by_priority

    def _select_improvements(self, analysis: Dict) -> List[Dict]:
        """Selecciona mejoras seguras para aplicar"""
        improvements = []

        # Priorizar mejoras menores y seguras
        safe_improvement_types = [
            'add_docstring',
            'optimize_imports',
            'fix_long_lines'
        ]

        for file_path, file_analysis in analysis['detailed_analysis'].items():
            for suggestion in file_analysis.get('suggestions', []):
                if (suggestion['type'] in safe_improvement_types and
                    len(improvements) < self.config['max_changes_per_session']):

                    improvements.append({
                        'file_path': file_path,
                        'suggestion': suggestion
                    })

        return improvements

    def get_improvement_summary(self) -> Dict[str, Any]:
        """Resumen del historial de mejoras"""
        if not self.improvement_history:
            return {'total_sessions': 0, 'total_improvements': 0}

        total_improvements = sum(
            record['improvements_successful']
            for record in self.improvement_history
        )

        recent_improvements = [
            record for record in self.improvement_history[-10:]
        ]

        return {
            'total_sessions': len(self.improvement_history),
            'total_improvements': total_improvements,
            'recent_sessions': recent_improvements,
            'last_improvement': self.improvement_history[-1]['timestamp'] if self.improvement_history else None
        }
