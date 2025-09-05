import os
import ast
import time
from typing import Dict, Any, List
from .autonomous_learning import AutonomousPatchGenerator

class SelfUpdateEngine:
    """Analiza el repositorio y genera sugerencias de mejora reales (no aplica aún)."""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.patch_generator = AutonomousPatchGenerator()

    def analyze_repository(self) -> Dict[str, Any]:
        summary = {
            'files_scanned': 0,
            'python_files': 0,
            'total_lines': 0,
            'large_files': [],
            'complex_candidates': [],
            'functions_over_threshold': [],
            'scan_time': time.time()
        }
        for base, _, files in os.walk(self.root_dir):
            if any(part.startswith('.') for part in base.split(os.sep)):
                continue
            for f in files:
                if f.endswith('.py'):
                    path = os.path.join(base, f)
                    summary['python_files'] += 1
                    try:
                        with open(path, 'r', encoding='utf-8') as fh:
                            src = fh.read()
                        lines = src.count('\n') + 1
                        summary['total_lines'] += lines
                        if lines > 800:
                            summary['large_files'].append({'path': path, 'lines': lines})
                        tree = ast.parse(src)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                f_lines = (node.body[-1].lineno - node.body[0].lineno + 1) if node.body else 1
                                if f_lines > 60:
                                    summary['functions_over_threshold'].append({'file': path, 'function': node.name, 'lines': f_lines})
                            if isinstance(node, ast.ClassDef) and len(node.body) > 40:
                                summary['complex_candidates'].append({'file': path, 'class': node.name, 'members': len(node.body)})
                    except Exception:
                        pass
                    summary['files_scanned'] += 1
        return summary

    def generate_improvement_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []
        # Large files
        for lf in analysis.get('large_files', []):
            suggestions.append({
                'type': 'refactor_split_file',
                'file': lf['path'],
                'detail': f"Archivo muy grande ({lf['lines']} líneas). Dividir en módulos lógicos.",
                'priority': 'high'
            })
        # Long functions
        for fn in analysis.get('functions_over_threshold', []):
            suggestions.append({
                'type': 'refactor_long_function',
                'file': fn['file'],
                'detail': f"Función {fn['function']} demasiado larga ({fn['lines']} líneas). Extraer helpers.",
                'priority': 'medium'
            })
        # Complex classes
        for cc in analysis.get('complex_candidates', []):
            suggestions.append({
                'type': 'refactor_large_class',
                'file': cc['file'],
                'detail': f"Clase {cc['class']} con muchos miembros ({cc['members']}). Considerar patrón modular.",
                'priority': 'medium'
            })
        if not suggestions:
            suggestions.append({
                'type': 'health_check',
                'detail': 'No se detectaron problemas estructurales significativos.',
                'priority': 'low'
            })
        return suggestions

    def generate_patch_proposals(self, knowledge_store=None) -> List[Dict[str, Any]]:
        """Generate autonomous patch proposals from improvement suggestions."""
        suggestions = self.generate_improvements()
        patch_proposals = []

        for suggestion in suggestions:
            if 'file' in suggestion:
                patch = self.patch_generator.generate_patch_proposal(
                    suggestion['file'], suggestion
                )
                if patch:
                    proposal = {
                        'suggestion': suggestion,
                        'patch': patch,
                        'timestamp': time.time(),
                        'auto_generated': True
                    }
                    patch_proposals.append(proposal)

                    # Store in knowledge store if available
                    if knowledge_store:
                        knowledge_store.add_patch_proposal(
                            suggestion['file'],
                            suggestion['type'],
                            patch['proposed_patch'] if patch['type'] == 'code_patch' else patch['guidance'],
                            patch['risk_level'],
                            patch['estimated_impact'],
                            'autonomous_generator'
                        )

        return patch_proposals
