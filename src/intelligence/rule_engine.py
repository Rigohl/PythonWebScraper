"""Rule Engine Ligero para HybridBrain

Sistema declarativo que permite expresar lógica de decisión en formato de datos
en lugar de código hardcoded. Facilita ajuste dinámico de comportamiento.

Estructura de regla:
{
  "id": "rule_id",
  "condition": {
    "metric": "error_rate",
    "operator": "gte",
    "value": 0.5,
    "context": ["domain", "timeframe"]
  },
  "action": {
    "type": "suggest",
    "category": "stability", 
    "severity": "high",
    "template": "Aplicar backoff en {domain}: error_rate {error_rate:.2f}"
  },
  "metadata": {
    "priority": 100,
    "enabled": true,
    "description": "Detectar dominios con alta tasa de error"
  }
}

Operadores soportados: eq, ne, gt, gte, lt, lte, in, contains, pattern
"""

from __future__ import annotations

import re
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class RuleCondition:
    metric: str
    operator: str  
    value: Union[str, int, float, List[Any]]
    context: Optional[List[str]] = None

    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evalúa condición contra datos contextuales."""
        actual = self._extract_metric(data, self.metric)
        
        if actual is None:
            return False
            
        return self._apply_operator(actual, self.operator, self.value)
    
    def _extract_metric(self, data: Dict[str, Any], metric: str) -> Any:
        """Extrae valor anidado usando dot notation."""
        keys = metric.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _apply_operator(self, actual: Any, operator: str, expected: Any) -> bool:
        """Aplica operador de comparación."""
        try:
            if operator == 'eq':
                return actual == expected
            elif operator == 'ne':
                return actual != expected
            elif operator == 'gt':
                return float(actual) > float(expected)
            elif operator == 'gte':
                return float(actual) >= float(expected)
            elif operator == 'lt':
                return float(actual) < float(expected)
            elif operator == 'lte':
                return float(actual) <= float(expected)
            elif operator == 'in':
                return actual in expected
            elif operator == 'contains':
                return str(expected) in str(actual)
            elif operator == 'pattern':
                return bool(re.search(str(expected), str(actual)))
            else:
                return False
        except (ValueError, TypeError):
            return False


@dataclass
class RuleAction:
    type: str  # suggest, alert, auto_fix, etc.
    category: str
    severity: str = "medium"
    template: str = ""
    params: Optional[Dict[str, Any]] = None

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta acción usando datos de contexto."""
        result = {
            'type': self.type,
            'category': self.category,
            'severity': self.severity,
            'message': self.template.format(**data) if self.template else "",
            'data': data
        }
        if self.params:
            result.update(self.params)
        return result


@dataclass
class Rule:
    id: str
    condition: RuleCondition
    action: RuleAction
    priority: int = 50
    enabled: bool = True
    description: str = ""

    def evaluate(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evalúa regla completa y retorna acción si aplica."""
        if not self.enabled:
            return None
            
        if self.condition.evaluate(data):
            result = self.action.execute(data)
            result['rule_id'] = self.id
            result['priority'] = self.priority
            return result
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rule':
        """Crea regla desde diccionario."""
        condition_data = data['condition']
        action_data = data['action']
        metadata = data.get('metadata', {})
        
        return cls(
            id=data['id'],
            condition=RuleCondition(**condition_data),
            action=RuleAction(**action_data),
            priority=metadata.get('priority', 50),
            enabled=metadata.get('enabled', True),
            description=metadata.get('description', '')
        )


class RuleEngine:
    """Motor de reglas declarativo."""
    
    def __init__(self, rules_path: str = "data/intelligence_rules.json"):
        self.rules_path = Path(rules_path)
        self.rules: Dict[str, Rule] = {}
        self._load_default_rules()
        self._load_custom_rules()

    def _load_default_rules(self):
        """Carga reglas por defecto hardcoded."""
        default_rules = [
            {
                "id": "high_error_rate_backoff",
                "condition": {
                    "metric": "error_rate",
                    "operator": "gte", 
                    "value": 0.5
                },
                "action": {
                    "type": "suggest",
                    "category": "stability",
                    "severity": "high",
                    "template": "Aplicar backoff adaptativo en {domain}: error_rate {error_rate:.2f}"
                },
                "metadata": {
                    "priority": 90,
                    "enabled": True,
                    "description": "Detectar dominios con alta tasa de error"
                }
            },
            {
                "id": "structural_drift_high",
                "condition": {
                    "metric": "structure_drift_score",
                    "operator": "gte",
                    "value": 0.45
                },
                "action": {
                    "type": "suggest", 
                    "category": "extraction",
                    "severity": "high",
                    "template": "Alto drift estructural en {domain}: score {structure_drift_score:.2f}"
                },
                "metadata": {
                    "priority": 85,
                    "enabled": True,
                    "description": "Detectar cambios estructurales significativos"
                }
            },
            {
                "id": "slow_domain_optimization",
                "condition": {
                    "metric": "response_time_ratio",
                    "operator": "gte",
                    "value": 1.8
                },
                "action": {
                    "type": "suggest",
                    "category": "performance", 
                    "severity": "medium",
                    "template": "Optimizar dominio lento {domain}: {response_time:.2f}s vs global {global_avg:.2f}s"
                },
                "metadata": {
                    "priority": 70,
                    "enabled": True,
                    "description": "Identificar dominios con latencia elevada"
                }
            },
            {
                "id": "healing_dependency_high",
                "condition": {
                    "metric": "healing_ratio",
                    "operator": "gte",
                    "value": 0.25
                },
                "action": {
                    "type": "suggest",
                    "category": "resilience",
                    "severity": "high", 
                    "template": "Reducir dependencia de healing en {domain}: ratio {healing_ratio:.2f}"
                },
                "metadata": {
                    "priority": 80,
                    "enabled": True,
                    "description": "Detectar exceso de healing aplicado"
                }
            },
            {
                "id": "schedule_optimization_opportunity",
                "condition": {
                    "metric": "hour_success_gain",
                    "operator": "gte",
                    "value": 0.25
                },
                "action": {
                    "type": "suggest",
                    "category": "scheduling",
                    "severity": "medium",
                    "template": "Optimizar horario para {domain}: ganancia {hour_success_gain:.2f} en hora {best_hour}"
                },
                "metadata": {
                    "priority": 60,
                    "enabled": True,
                    "description": "Detectar oportunidades de optimización horaria"
                }
            }
        ]
        
        for rule_data in default_rules:
            rule = Rule.from_dict(rule_data)
            self.rules[rule.id] = rule

    def _load_custom_rules(self):
        """Carga reglas personalizadas desde archivo."""
        if not self.rules_path.exists():
            return
            
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for rule_data in data.get('rules', []):
                rule = Rule.from_dict(rule_data)
                self.rules[rule.id] = rule
                
        except Exception:
            pass

    def evaluate_all(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evalúa todas las reglas activas contra los datos."""
        results = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            result = rule.evaluate(data)
            if result:
                results.append(result)
        
        # Ordenar por prioridad
        return sorted(results, key=lambda x: x['priority'], reverse=True)

    def add_rule(self, rule: Rule):
        """Añade nueva regla."""
        self.rules[rule.id] = rule

    def remove_rule(self, rule_id: str):
        """Elimina regla."""
        self.rules.pop(rule_id, None)

    def enable_rule(self, rule_id: str, enabled: bool = True):
        """Habilita/deshabilita regla."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = enabled

    def persist_rules(self):
        """Guarda reglas personalizadas a archivo."""
        try:
            self.rules_path.parent.mkdir(exist_ok=True)
            
            # Solo guardar reglas no-default (las que no están hardcoded)
            default_ids = {
                "high_error_rate_backoff", "structural_drift_high", 
                "slow_domain_optimization", "healing_dependency_high",
                "schedule_optimization_opportunity"
            }
            
            custom_rules = []
            for rule in self.rules.values():
                if rule.id not in default_ids:
                    custom_rules.append({
                        'id': rule.id,
                        'condition': asdict(rule.condition),
                        'action': asdict(rule.action),
                        'metadata': {
                            'priority': rule.priority,
                            'enabled': rule.enabled,
                            'description': rule.description
                        }
                    })
            
            with open(self.rules_path, 'w', encoding='utf-8') as f:
                json.dump({'rules': custom_rules}, f, indent=2, ensure_ascii=False)
                
        except Exception:
            pass

    def get_rule_summary(self) -> Dict[str, Any]:
        """Retorna resumen de reglas cargadas."""
        enabled_count = sum(1 for r in self.rules.values() if r.enabled)
        categories = {}
        
        for rule in self.rules.values():
            cat = rule.action.category
            categories[cat] = categories.get(cat, 0) + 1
            
        return {
            'total_rules': len(self.rules),
            'enabled_rules': enabled_count,
            'categories': categories,
            'rule_ids': list(self.rules.keys())
        }


__all__ = ['RuleEngine', 'Rule', 'RuleCondition', 'RuleAction']