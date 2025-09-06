"""Self-Repair Advisor (Advisory Layer Only)

Genera sugerencias inteligentes (no auto-modifica código) basadas en la
inteligencia combinada de:
 - Brain (heurísticas ligeras de dominio)
 - AutonomousLearningBrain (patrones y estrategias aprendidas)
 - EnrichmentStore (telemetría estructural, temporal y contextual)

Objetivo: Proveer un set priorizado de acciones que aumenten resiliencia,
eficiencia y cobertura de extracción sin ejecutar cambios peligrosos.

Cada sugerencia incluye:
  {
    id: str (estable, para tracking),
    category: str,
    severity: low|medium|high|critical,
    title: str (resumen ejecutivo),
    rationale: str (explicación basada en señales),
    recommended_action: str (paso concreto),
    signals: dict (valores numéricos usados),
    confidence: float 0..1
  }

Esta capa es segura: sólo lectura y generación de texto/metadata.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class SelfRepairAdvisor:
    def __init__(
        self,
        simple_brain,
        autonomous_brain,
        enrichment,
        overrides: Optional[Dict[str, Any]] = None,
        knowledge_base=None,
    ):
        self.simple_brain = simple_brain
        self.autonomous_brain = autonomous_brain
        self.enrichment = enrichment
        self.overrides = overrides or {}
        self.knowledge_base = knowledge_base  # opcional (inyectado por HybridBrain)
        # Parámetros base (se pueden hacer override externamente)
        self.thresholds = {
            "error_rate_high": self.overrides.get("backoff_threshold", 0.5),
            "min_visits_for_backoff": self.overrides.get("min_visits_for_backoff", 5),
            "structural_drift_high": 0.45,
            "slow_response_factor": 1.8,  # > 1.8x promedio global
            "schedule_gain_min": 0.25,  # diferencia éxito bestHour vs promedio
            "healing_frequency_high": 0.25,  # healing en >25% de sesiones dominio
            "low_success_rate": 0.35,
        }

    # --------------------------- API Pública ---------------------------
    def generate(self, limit: int = 25) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []

        try:
            global_metrics = self._global_metrics()
            # Generadores especializados
            suggestions.extend(self._suggest_domain_backoff(global_metrics))
            suggestions.extend(self._suggest_speed_ups(global_metrics))
            suggestions.extend(self._suggest_structural_updates())
            suggestions.extend(self._suggest_schedule_adjustments())
            suggestions.extend(self._suggest_extraction_enrichment())
            suggestions.extend(self._suggest_healing_improvements())
            suggestions.extend(self._suggest_error_root_causes())
        except Exception:
            # Falla aislada -> devolver lo acumulado
            pass

        # Ranking simple por severity -> confidence -> timestamp
        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        suggestions = sorted(
            suggestions,
            key=lambda s: (
                severity_rank.get(s["severity"], 0),
                round(s.get("confidence", 0), 3),
            ),
            reverse=True,
        )

        # Limitar y asegurar ids únicos
        seen = set()
        filtered = []
        for s in suggestions:
            if s["id"] in seen:
                continue
            seen.add(s["id"])
            filtered.append(s)
            if len(filtered) >= limit:
                break
        # Enriquecer con referencias KB si disponible
        if self.knowledge_base:
            for s in filtered:
                s["kb_refs"] = self._kb_refs_for_category(s.get("category"))
        return filtered

    def _kb_refs_for_category(self, category: str) -> List[str]:
        mapping = {
            "stability": [
                "scraping:respect-delays",
                "antibot:fingerprint-patterns",
                "antibot:retry-strategy",
            ],
            "performance": ["perf:latency-tuning", "perf:cache-static"],
            "extraction": ["selectors:robust-css", "selectors:xpath-fallback"],
            "scheduling": ["scraping:respect-delays"],
            "resilience": ["healing:reduce-dependence", "selfrepair:advisory-loop"],
        }
        candidates = mapping.get(category, [])
        out = []
        for cid in candidates:
            if self.knowledge_base.get(cid):  # type: ignore[union-attr]
                out.append(cid)
        return out

    # --------------------------- Métricas Globales ---------------------------
    def _global_metrics(self) -> Dict[str, Any]:
        # Promedio global de tiempos y tasa éxito visible por autonomous_brain
        sessions = getattr(self.autonomous_brain, "session_history", [])
        if sessions:
            total_rt = sum(
                s.response_time for s in sessions if s.response_time is not None
            )
            count_rt = sum(1 for s in sessions if s.response_time is not None)
            avg_rt = total_rt / max(1, count_rt)
            success_rate = sum(1 for s in sessions if s.success) / len(sessions)
        else:
            avg_rt = 0.0
            success_rate = 0.0
        return {
            "avg_response_time": avg_rt,
            "success_rate": success_rate,
            "total_sessions": len(sessions),
        }

    # --------------------------- Generadores de Sugerencias ---------------------------
    def _suggest_domain_backoff(self, gm: Dict[str, Any]) -> List[Dict[str, Any]]:
        out = []
        for domain, stats in self.simple_brain.domain_stats.items():
            visits = stats.get("visits", 0)
            if visits < self.thresholds["min_visits_for_backoff"]:
                continue
            errors = stats.get("errors", 0)
            error_rate = errors / max(1, visits)
            if error_rate >= self.thresholds["error_rate_high"]:
                # Detectar spike reciente
                spike = self.simple_brain.recent_error_spike(domain)
                severity = "high" if spike else "medium"
                confidence = min(
                    1.0, 0.6 + (error_rate - self.thresholds["error_rate_high"])
                )
                out.append(
                    {
                        "id": f"backoff::{domain}",
                        "timestamp": time.time(),
                        "category": "stability",
                        "severity": severity if spike else "medium",
                        "title": f"Aplicar backoff adaptativo en {domain}",
                        "rationale": (
                            f"Error rate {error_rate:.2f} (visits={visits}, errors={errors}) supera umbral "
                            f"{self.thresholds['error_rate_high']:.2f}{' con spike reciente' if spike else ''}."
                        ),
                        "recommended_action": "Incrementar delay + reducir concurrencia temporalmente; reintentar tras ventana fría.",
                        "signals": {
                            "error_rate": error_rate,
                            "visits": visits,
                            "errors": errors,
                            "spike": spike,
                        },
                        "confidence": round(confidence, 3),
                    }
                )
        return out

    def _suggest_speed_ups(self, gm: Dict[str, Any]) -> List[Dict[str, Any]]:
        out = []
        global_avg = gm["avg_response_time"] or 0.0
        if global_avg == 0:
            return out
        for domain, intel in getattr(
            self.autonomous_brain, "domain_intelligence", {}
        ).items():
            # Dominios altamente estables + rápidos => oportunidad de agresividad
            if (
                intel.success_rate > 0.9
                and intel.avg_response_time < global_avg * 0.6
                and intel.total_attempts >= 8
            ):
                out.append(
                    {
                        "id": f"speedup::{domain}",
                        "timestamp": time.time(),
                        "category": "performance",
                        "severity": "medium",
                        "title": f"Reducir delay en dominio estable {domain}",
                        "rationale": (
                            f"Success {intel.success_rate:.2f} y RT {intel.avg_response_time:.2f}s (<60% del global)."
                        ),
                        "recommended_action": "Disminuir delay ~15% y monitorizar error rate durante 20 sesiones.",
                        "signals": {
                            "domain_success": intel.success_rate,
                            "domain_avg_rt": intel.avg_response_time,
                            "global_avg_rt": global_avg,
                        },
                        "confidence": 0.72,
                    }
                )
            # Dominios lentos -> ajuste
            if (
                intel.avg_response_time
                > global_avg * self.thresholds["slow_response_factor"]
                and intel.total_attempts >= 5
            ):
                delta = intel.avg_response_time - global_avg
                out.append(
                    {
                        "id": f"slowdomain::{domain}",
                        "timestamp": time.time(),
                        "category": "performance",
                        "severity": "high",
                        "title": f"Optimizar estrategia en dominio lento {domain}",
                        "rationale": (
                            f"Tiempo respuesta {intel.avg_response_time:.2f}s es +{delta:.2f}s vs global {global_avg:.2f}s."
                        ),
                        "recommended_action": "Aumentar delay incremental + revisar headers / compresión y activar caching selectivo.",
                        "signals": {
                            "domain_avg_rt": intel.avg_response_time,
                            "global_avg_rt": global_avg,
                            "delta": delta,
                        },
                        "confidence": 0.81,
                    }
                )
        return out

    def _suggest_structural_updates(self) -> List[Dict[str, Any]]:
        out = []
        # Recorremos dominios de enrichment para detectar drift
        for domain, data in self.enrichment.domain_index.items():
            hashes = data.get("structure_hashes", {})
            if not hashes:
                continue
            total = sum(hashes.values())
            top = max(hashes.values())
            drift_score = 1.0 - (top / max(1, total))
            if drift_score >= self.thresholds["structural_drift_high"] and total >= 5:
                out.append(
                    {
                        "id": f"structure::drift::{domain}",
                        "timestamp": time.time(),
                        "category": "extraction",
                        "severity": "high",
                        "title": f"Alto drift estructural en {domain}",
                        "rationale": f"Variación de estructura {drift_score:.2f} (total snapshots={total}).",
                        "recommended_action": "Regenerar selectores CSS/XPath robustos (usar atributos estáticos y jerarquías semánticas).",
                        "signals": {
                            "drift_score": drift_score,
                            "structure_snapshots": total,
                        },
                        "confidence": round(min(1.0, 0.6 + drift_score), 3),
                    }
                )
        return out

    def _suggest_schedule_adjustments(self) -> List[Dict[str, Any]]:
        out = []
        # Basado en hour_profile agregada
        for domain, data in self.enrichment.domain_index.items():
            hp = data.get("hour_profile", {})
            if len(hp) < 3:
                continue
            # Calcular mejor y peor hora por éxito
            rates = []
            for h, v in hp.items():
                rate = v["s"] / max(1, v["a"])
                rates.append((h, rate, v["a"]))
            if not rates:
                continue
            rates_sorted = sorted(rates, key=lambda x: x[1], reverse=True)
            best = rates_sorted[0]
            rates_sorted[-1]
            avg = sum(r[1] for r in rates) / len(rates)
            gain = best[1] - avg
            if gain >= self.thresholds["schedule_gain_min"] and best[2] >= 3:
                out.append(
                    {
                        "id": f"schedule::besthour::{domain}",
                        "timestamp": time.time(),
                        "category": "scheduling",
                        "severity": "medium",
                        "title": f"Concentrar scraping en hora óptima {best[0]:02d}h para {domain}",
                        "rationale": f"Rate mejor hora {best[1]:.2f} vs promedio {avg:.2f} (ganancia {gain:.2f}).",
                        "recommended_action": "Priorizar cola de URLs de este dominio en esa franja y reducir fuera de pico.",
                        "signals": {
                            "best_hour": best[0],
                            "best_rate": best[1],
                            "avg_rate": avg,
                            "gain": gain,
                        },
                        "confidence": 0.68,
                    }
                )
        return out

    def _suggest_extraction_enrichment(self) -> List[Dict[str, Any]]:
        out = []
        # Detectar campos potenciales (field_*) que aparecen con frecuencia pero no están en patrones comunes por dominio
        pattern_freq = self.enrichment.pattern_freq
        # Extraer top field_ patterns
        candidate_fields = [
            p for p, c in pattern_freq.items() if p.startswith("field_") and c >= 3
        ]
        # Mapear domain -> patterns comunes (autonomous intelligence)
        for domain, intel in getattr(
            self.autonomous_brain, "domain_intelligence", {}
        ).items():
            common = set(intel.common_patterns)
            missing = [f for f in candidate_fields if f not in common]
            if missing and intel.total_attempts >= 5:
                out.append(
                    {
                        "id": f"extraction::fields::{domain}",
                        "timestamp": time.time(),
                        "category": "extraction",
                        "severity": "medium",
                        "title": f"Ampliar cobertura de extracción en {domain}",
                        "rationale": f"Campos candidatos no reforzados: {', '.join(missing[:5])}...",
                        "recommended_action": "Añadir reglas de parseo / selectores para campos faltantes y validar calidad.",
                        "signals": {
                            "missing_fields": missing[:10],
                            "domain_attempts": intel.total_attempts,
                        },
                        "confidence": 0.63,
                    }
                )
        return out

    def _suggest_healing_improvements(self) -> List[Dict[str, Any]]:
        out = []
        # Frecuencia de patrones healing_applied_* vs total sesiones dominio
        for domain, data in self.enrichment.domain_index.items():
            attempts = data.get("attempts", 0)
            if attempts < 6:
                continue
            pattern_counts = data.get("patterns", {})
            healing_total = sum(
                c for p, c in pattern_counts.items() if p.startswith("healing_applied_")
            )
            ratio = healing_total / max(1, attempts)
            if ratio >= self.thresholds["healing_frequency_high"]:
                out.append(
                    {
                        "id": f"healing::excess::{domain}",
                        "timestamp": time.time(),
                        "category": "resilience",
                        "severity": "high",
                        "title": f"Alta dependencia de healing en {domain}",
                        "rationale": f"Healing aplicado en {ratio:.2f} de sesiones ({healing_total}/{attempts}).",
                        "recommended_action": "Refactorizar extractores primarios para reducir healing; añadir fallback estructural robusto.",
                        "signals": {
                            "healing_ratio": ratio,
                            "healing_events": healing_total,
                            "attempts": attempts,
                        },
                        "confidence": round(min(1.0, 0.5 + ratio), 3),
                    }
                )
        return out

    def _suggest_error_root_causes(self) -> List[Dict[str, Any]]:
        out = []
        # Requiere frecuencia de error_types y dominios afectados
        top_errors = sorted(
            self.simple_brain.error_type_freq.items(), key=lambda x: x[1], reverse=True
        )[:5]
        for err, count in top_errors:
            if count < 3:
                continue
            affected_domains = []
            for domain, stats in self.simple_brain.domain_stats.items():
                # Estimar si error afecta: buscar en eventos recientes
                dom_errors = 0
                dom_total = 0
                for ev in reversed(list(self.simple_brain.recent_events)):
                    if (
                        ev.domain or self.simple_brain._extract_domain(ev.url)
                    ) == domain:
                        if dom_total >= 40:
                            break
                        dom_total += 1
                        if ev.error_type == err:
                            dom_errors += 1
                if dom_errors >= 2:
                    affected_domains.append(domain)
            if affected_domains:
                severity = "critical" if len(affected_domains) >= 3 else "high"
                confidence = min(1.0, 0.6 + (len(affected_domains) * 0.1))
                out.append(
                    {
                        "id": f"rootcause::{err}",
                        "timestamp": time.time(),
                        "category": "stability",
                        "severity": severity,
                        "title": f"Investigar causa raíz error '{err}'",
                        "rationale": f"Error recurrente en {len(affected_domains)} dominios (count={count}).",
                        "recommended_action": "Reproducir local, capturar stack/HTML, agregar manejo específico o retry policy adaptativa.",
                        "signals": {
                            "error_type": err,
                            "domains_affected": affected_domains,
                            "global_count": count,
                        },
                        "confidence": round(confidence, 3),
                    }
                )
        return out


__all__ = ["SelfRepairAdvisor"]
