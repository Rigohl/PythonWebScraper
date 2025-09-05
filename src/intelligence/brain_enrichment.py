import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

# EnrichmentStore: almacena señales avanzadas no críticas para la lógica base.
# Objetivo: nutrir el cerebro híbrido con contexto rico para decisiones futuras.
# Diseño: desacoplado, tolerante a errores, persistencia incremental.

class EnrichmentStore:
    def __init__(self, path: str = "data/brain_enrichment.json", max_sessions: int = 5000):
        self.path = Path(path)
        self.path.parent.mkdir(exist_ok=True)
        self.max_sessions = max_sessions
        self.sessions: List[Dict[str, Any]] = []  # Sesiones enriquecidas crudas
        self.domain_index: Dict[str, Dict[str, Any]] = {}  # Estadísticas agregadas por dominio
        self.pattern_freq: Dict[str, int] = {}
        self.error_signatures: Dict[str, int] = {}
        self.content_type_stats: Dict[str, int] = {}
        self.complexity_distribution: Dict[str, int] = {}
        self.hour_success: Dict[int, Dict[str, int]] = {}  # hour -> {'attempts': X, 'success': Y}
        self._loaded = False
        self._load()

    # ---------------- Persistencia -----------------
    def _load(self):
        if self.path.exists():
            try:
                data = json.load(self.path.open('r', encoding='utf-8'))
                self.sessions = data.get('sessions', [])
                self.domain_index = data.get('domain_index', {})
                self.pattern_freq = data.get('pattern_freq', {})
                self.error_signatures = data.get('error_signatures', {})
                self.content_type_stats = data.get('content_type_stats', {})
                self.complexity_distribution = data.get('complexity_distribution', {})
                self.hour_success = data.get('hour_success', {})
                self._loaded = True
            except Exception:
                # Corrupción o estructura desconocida -> ignorar
                self._loaded = False

    def save(self):
        try:
            data = {
                'sessions': self.sessions[-self.max_sessions:],
                'domain_index': self.domain_index,
                'pattern_freq': self.pattern_freq,
                'error_signatures': self.error_signatures,
                'content_type_stats': self.content_type_stats,
                'complexity_distribution': self.complexity_distribution,
                'hour_success': self.hour_success,
                'last_saved': time.time()
            }
            with self.path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # ---------------- API Principal -----------------
    def add_session(self, result, context: Optional[Dict[str, Any]] = None, patterns: Optional[List[str]] = None):
        """Añade una sesión enriquecida usando datos del ScrapeResult + contexto."""
        try:
            ctx = context or {}
            domain = self._extract_domain(getattr(result, 'url', ''))
            ts = time.time()
            patterns = patterns or []

            # Métricas estructurales
            content_html = getattr(result, 'content_html', None)
            structure_hash, tag_counts, complexity_bucket = self._analyze_structure(content_html, getattr(result, 'content_text', ''))
            access_hour = time.localtime(ts).tm_hour

            session_record = {
                't': ts,
                'domain': domain,
                'url': getattr(result, 'url', ''),
                'status': getattr(result, 'status', ''),
                'success': getattr(result, 'status', '') == 'SUCCESS',
                'response_time': ctx.get('response_time') or getattr(result, 'response_time', None),
                'crawl_duration': getattr(result, 'crawl_duration', None),
                'links_count': len(getattr(result, 'links', []) or []),
                'extracted_fields': len((getattr(result, 'extracted_data', {}) or {})),
                'healing_events': len(getattr(result, 'healing_events', []) or []),
                'retryable': getattr(result, 'retryable', False),
                'http_status_code': getattr(result, 'http_status_code', None),
                'content_type': getattr(result, 'content_type', None),
                'content_len': len((getattr(result, 'content_text', '') or '')),
                'patterns': patterns,
                'error_message': getattr(result, 'error_message', None),
                'user_agent': ctx.get('user_agent'),
                'delay_used': ctx.get('delay_used'),
                'structure_hash': structure_hash,
                'tag_counts': tag_counts,
                'complexity': complexity_bucket,
                'hour': access_hour,
            }
            self.sessions.append(session_record)
            if len(self.sessions) > self.max_sessions * 1.2:
                self.sessions = self.sessions[-self.max_sessions:]

            # Actualizar agregados
            self._update_domain_index(session_record)
            self._update_pattern_freq(patterns)
            self._update_errors(session_record)
            self._update_content_types(session_record)
            self._update_complexity(session_record)
            self._update_hour_profile(session_record)
        except Exception:
            pass

    # ---------------- Consultas / Resúmenes -----------------
    def summarize(self) -> Dict[str, Any]:
        """Resumen compacto para exponer en HybridBrain.stats."""
        total = len(self.sessions)
        success = sum(1 for s in self.sessions if s.get('success'))
        avg_rt = self._avg([s.get('response_time') for s in self.sessions if s.get('response_time')])

        top_domains = sorted(
            [
                {
                    'domain': d,
                    'attempts': v['attempts'],
                    'success_rate': round(v['success'] / max(v['attempts'], 1), 3),
                    'avg_rt': self._avg(v.get('response_times', [])),
                    'patterns_seen': len(v.get('patterns', {})),
                }
                for d, v in self.domain_index.items()
            ], key=lambda x: (x['success_rate'], x['attempts']), reverse=True
        )[:5]

        top_patterns = sorted(self.pattern_freq.items(), key=lambda x: x[1], reverse=True)[:8]
        top_errors = sorted(self.error_signatures.items(), key=lambda x: x[1], reverse=True)[:5]
        content_mix = sorted(self.content_type_stats.items(), key=lambda x: x[1], reverse=True)[:6]
        complexity_mix = sorted(self.complexity_distribution.items(), key=lambda x: x[1], reverse=True)
        hour_distribution = self._hour_summary()

        return {
            'total_enriched_sessions': total,
            'success_rate': round(success / max(total, 1), 3),
            'avg_response_time': avg_rt,
            'top_domains': top_domains,
            'top_patterns': top_patterns,
            'top_errors': top_errors,
            'content_type_distribution': content_mix,
            'complexity_distribution': complexity_mix,
            'hour_success_distribution': hour_distribution,
        }

    def domain_insight(self, domain: str) -> Dict[str, Any]:
        data = self.domain_index.get(domain)
        if not data:
            return {}
        # Calcular drift estructural: proporción de hash dominante sobre total
        hashes = data.get('structure_hashes', {})
        drift_score = 0.0
        if hashes:
            total = sum(hashes.values())
            top = max(hashes.values())
            # Si top representa poca proporción => alta variabilidad (drift alto)
            stability = top / max(total, 1)
            drift_score = round(1.0 - stability, 3)

        # Perfil horario
        hour_profile = []
        for h, hs in data.get('hour_profile', {}).items():
            rate = hs['s'] / max(hs['a'], 1)
            hour_profile.append({'hour': h, 'attempts': hs['a'], 'success_rate': round(rate, 3)})
        hour_profile = sorted(hour_profile, key=lambda x: x['success_rate'], reverse=True)[:6]

        return {
            'attempts': data['attempts'],
            'success': data['success'],
            'success_rate': round(data['success'] / max(data['attempts'], 1), 3),
            'avg_response_time': self._avg(data.get('response_times', [])),
            'patterns': sorted(data.get('patterns', {}).items(), key=lambda x: x[1], reverse=True)[:10],
            'errors': sorted(data.get('errors', {}).items(), key=lambda x: x[1], reverse=True)[:5],
            'content_types': data.get('content_types', {}),
            'complexity_mix': data.get('complexity', {}),
            'structure_drift_score': drift_score,
            'best_hours': hour_profile,
        }

    # ---------------- Internos -----------------
    def _update_domain_index(self, s: Dict[str, Any]):
        d = s['domain'] or 'unknown'
        di = self.domain_index.setdefault(d, {
            'attempts': 0,
            'success': 0,
            'response_times': [],
            'patterns': {},
            'errors': {},
            'content_types': {},
            'complexity': {},  # bucket -> count
            'structure_hashes': {},  # hash -> count
            'hour_profile': {},  # hour -> {'a': attempts, 's': success}
        })
        di['attempts'] += 1
        if s.get('success'):
            di['success'] += 1
        if s.get('response_time') is not None:
            di['response_times'].append(s['response_time'])
            if len(di['response_times']) > 200:
                di['response_times'] = di['response_times'][-200:]
        for p in s.get('patterns', []) or []:
            di['patterns'][p] = di['patterns'].get(p, 0) + 1
        err = s.get('error_message')
        if err:
            di['errors'][err] = di['errors'].get(err, 0) + 1
        ct = s.get('content_type')
        if ct:
            di['content_types'][ct] = di['content_types'].get(ct, 0) + 1
        # Complejidad
        bucket = s.get('complexity')
        if bucket:
            di['complexity'][bucket] = di['complexity'].get(bucket, 0) + 1
        # Estructura
        sh = s.get('structure_hash')
        if sh:
            di['structure_hashes'][sh] = di['structure_hashes'].get(sh, 0) + 1
        # Perfil horario
        hour = s.get('hour')
        if isinstance(hour, int):
            hp = di['hour_profile'].setdefault(hour, {'a': 0, 's': 0})
            hp['a'] += 1
            if s.get('success'):
                hp['s'] += 1

    def _update_pattern_freq(self, patterns: List[str]):
        for p in patterns or []:
            self.pattern_freq[p] = self.pattern_freq.get(p, 0) + 1

    def _update_errors(self, s: Dict[str, Any]):
        if s.get('error_message'):
            key = self._stable_sig(s.get('error_message'))
            self.error_signatures[key] = self.error_signatures.get(key, 0) + 1

    def _update_content_types(self, s: Dict[str, Any]):
        ct = s.get('content_type')
        if ct:
            self.content_type_stats[ct] = self.content_type_stats.get(ct, 0) + 1

    def _update_complexity(self, s: Dict[str, Any]):
        bucket = s.get('complexity')
        if bucket:
            self.complexity_distribution[bucket] = self.complexity_distribution.get(bucket, 0) + 1

    def _update_hour_profile(self, s: Dict[str, Any]):
        hour = s.get('hour')
        if isinstance(hour, int):
            info = self.hour_success.setdefault(hour, {'attempts': 0, 'success': 0})
            info['attempts'] += 1
            if s.get('success'):
                info['success'] += 1

    def _analyze_structure(self, html: Optional[str], text: str):
        if not html:
            return '', {}, 'unknown'
        try:
            # Conteo simple de tags comunes
            tags = ['div', 'span', 'a', 'p', 'li', 'ul', 'section', 'article', 'table', 'tr', 'td', 'form', 'script']
            counts = {}
            lower = html.lower()
            total_tags = 0
            for t in tags:
                c = lower.count(f'<{t}')
                if c:
                    counts[t] = c
                    total_tags += c

            # Hash estructural basado en orden de aparición de tags significativos
            signature_parts = []
            for t in ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']:
                if f'<{t}' in lower:
                    signature_parts.append(t)
            signature_parts.extend(sorted(counts.keys()))
            signature_str = '|'.join(signature_parts)
            structure_hash = hashlib.sha1(signature_str.encode('utf-8')).hexdigest()[:12]

            # Métrica de complejidad (heurística)
            text_len = len(text or '')
            score = total_tags + (text_len / 500.0)
            if score < 50:
                bucket = 'very_low'
            elif score < 120:
                bucket = 'low'
            elif score < 300:
                bucket = 'medium'
            elif score < 800:
                bucket = 'high'
            else:
                bucket = 'very_high'
            return structure_hash, counts, bucket
        except Exception:
            return '', {}, 'unknown'

    def _hour_summary(self):
        summary = []
        for h, info in self.hour_success.items():
            rate = info['success'] / max(info['attempts'], 1)
            summary.append({'hour': h, 'attempts': info['attempts'], 'success_rate': round(rate, 3)})
        return sorted(summary, key=lambda x: x['success_rate'], reverse=True)[:8]

    def _extract_domain(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except Exception:
            return ''

    def _stable_sig(self, text: str) -> str:
        h = hashlib.md5(text.encode('utf-8')).hexdigest()[:10]
        return h

    def _avg(self, seq: List[Optional[float]]):
        vals = [v for v in seq if isinstance(v, (int, float))]
        return round(sum(vals)/len(vals), 3) if vals else 0.0
