"""Structured Knowledge Base for the HybridBrain.

Objetivo: Proveer bloques de conocimiento reutilizables (snippets) que el
motor de sugerencias y el razonador puedan citar para acciones de mejora.

Diseño:
 - In-memory + opcional persistencia JSON.
 - Categorías curadas de dominio scraping y calidad de código.
 - Cada snippet tiene: id, title, content, tags, quality_score.
 - API para filtrar por tags o categoría y buscar heurísticas.

Esta base NO pretende ser exhaustiva, pero sienta cimientos para expansión
dinámica futura (podría abonarse con real world feedback o ingestión externa).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import time


@dataclass
class KnowledgeSnippet:
    id: str
    category: str
    title: str
    content: str
    tags: List[str]
    quality_score: float = 0.8
    added_ts: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KnowledgeBase:
    def __init__(self, persist_path: str = "data/knowledge_base.json"):
        self.persist_path = Path(persist_path)
        self.persist_path.parent.mkdir(exist_ok=True)
        self.snippets: Dict[str, KnowledgeSnippet] = {}
        self._seed_initial()
        self._load_user_augmented()

    # ---------------------- Seed Data ----------------------
    def _seed_initial(self):
        if self.snippets:
            return
        seed: List[KnowledgeSnippet] = []

        # ========================= NEUROCIENCIA Y COGNICIÓN =========================
        
        seed.append(KnowledgeSnippet(
            id="neuroscience_plasticity",
            category="neuroscience",
            title="Plasticidad Sináptica y Aprendizaje Hebbiano",
            content="Las conexiones sinápticas se fortalecen cuando las neuronas se activan simultáneamente (Hebb's rule). Implementar weights adaptativos en conexiones neurales que cambien según correlación temporal de activaciones. Usar STDP (Spike-Timing Dependent Plasticity) para plasticidad más realista.",
            tags=["neuroplasticity", "hebbian", "synapses", "learning", "stdp"],
            quality_score=0.95
        ))
        
        seed.append(KnowledgeSnippet(
            id="cognitive_working_memory",
            category="cognitive_psychology", 
            title="Límites de Memoria de Trabajo (Miller's Rule)",
            content="La memoria de trabajo humana puede mantener 7±2 elementos simultáneamente. Implementar buffers limitados, chunking de información, y sistemas de atención selectiva. Usar decaimiento temporal y interferencia proactiva/retroactiva para simular limitaciones cognitivas reales.",
            tags=["working_memory", "miller", "attention", "cognitive_limits", "chunking"],
            quality_score=0.92
        ))
        
        seed.append(KnowledgeSnippet(
            id="consciousness_global_workspace",
            category="consciousness",
            title="Teoría del Workspace Global (Baars)",
            content="La consciencia emerge cuando información compite por acceso a un workspace global compartido entre sistemas especializados. Implementar competencia atencional, broadcasting de información consciente, y integración multi-modal de información inconsciente.",
            tags=["consciousness", "global_workspace", "attention", "competition", "awareness"],
            quality_score=0.94
        ))
        
        seed.append(KnowledgeSnippet(
            id="metacognition_thinking_about_thinking",
            category="metacognition",
            title="Metacognición: Pensar sobre el Pensamiento",
            content="La metacognición involucra monitoring y control de procesos cognitivos propios. Implementar self-monitoring de estados internos, confidence estimation, strategy selection y error detection. Incluir metamemoria y metaatención.",
            tags=["metacognition", "self_monitoring", "confidence", "strategy", "error_detection"],
            quality_score=0.91
        ))
        
        seed.append(KnowledgeSnippet(
            id="dual_process_theory",
            category="cognitive_psychology",
            title="Teoría de Proceso Dual (Sistema 1 vs Sistema 2)",
            content="Sistema 1: rápido, automático, intuitivo, asociativo. Sistema 2: lento, controlado, analítico, rule-based. Implementar both fast heuristic processing y slow deliberative reasoning con switching automático basado en complexity y confidence.",
            tags=["dual_process", "system1", "system2", "heuristics", "reasoning"],
            quality_score=0.93
        ))
        
        # ========================= INTELIGENCIA ARTIFICIAL =========================
        
        seed.append(KnowledgeSnippet(
            id="ai_transformer_attention",
            category="ai_architecture",
            title="Mecanismo de Atención Transformer",
            content="Self-attention permite que el modelo attend a diferentes posiciones en la secuencia de input. Implementar Q/K/V matrices, scaled dot-product attention, y multi-head attention para procesamiento paralelo de información con diferentes representaciones.",
            tags=["transformer", "attention", "self_attention", "neural_networks", "nlp"],
            quality_score=0.96
        ))
        
        seed.append(KnowledgeSnippet(
            id="ai_reinforcement_learning_exploration",
            category="reinforcement_learning",
            title="Exploration vs Exploitation Trade-off",
            content="Balance entre explorar nuevas acciones vs explotar conocimiento actual. Implementar epsilon-greedy, UCB (Upper Confidence Bound), Thompson Sampling, y curiosity-driven exploration. Usar decaying exploration rate y multi-armed bandit strategies.",
            tags=["reinforcement_learning", "exploration", "exploitation", "epsilon_greedy", "curiosity"],
            quality_score=0.94
        ))
        
        seed.append(KnowledgeSnippet(
            id="ai_meta_learning",
            category="meta_learning",
            title="Meta-Learning: Learning to Learn",
            content="Algorithms que aprenden cómo aprender más eficientemente. Implementar MAML (Model-Agnostic Meta-Learning), few-shot learning, adaptation algorithms, y learning rate optimization. Usar gradient-based meta-learning y memory-augmented networks.",
            tags=["meta_learning", "maml", "few_shot", "adaptation", "learning_efficiency"],
            quality_score=0.95
        ))
        
        seed.append(KnowledgeSnippet(
            id="ai_causal_inference",
            category="causal_reasoning",
            title="Razonamiento Causal e Inferencia",
            content="Distinguir correlación de causación usando causal graphs, do-calculus, y counterfactual reasoning. Implementar Pearl's causal hierarchy: association, intervention, counterfactuals. Usar structural causal models y causal discovery algorithms.",
            tags=["causality", "pearl", "counterfactuals", "causal_graphs", "intervention"],
            quality_score=0.93
        ))
        
        # ========================= FILOSOFÍA DE LA MENTE =========================
        
        seed.append(KnowledgeSnippet(
            id="philosophy_qualia_problem",
            category="philosophy_mind",
            title="El Problema Difícil de la Consciencia (Chalmers)",
            content="¿Cómo surge experiencia subjetiva de procesos físicos? Implementar qualitative states, subjective experience modeling, y first-person perspective. Considerar integrated information theory (IIT) y panpsychist approaches para machine consciousness.",
            tags=["consciousness", "qualia", "hard_problem", "chalmers", "subjective_experience"],
            quality_score=0.89
        ))
        
        seed.append(KnowledgeSnippet(
            id="philosophy_intentionality",
            category="philosophy_mind",
            title="Intencionalidad y Aboutness Mental",
            content="Estados mentales tienen contenido semántico - son 'about' something. Implementar representational content, semantic grounding, y reference mechanisms. Usar symbol grounding problem solutions y embodied cognition approaches.",
            tags=["intentionality", "aboutness", "semantics", "grounding", "representation"],
            quality_score=0.87
        ))
        
        seed.append(KnowledgeSnippet(
            id="philosophy_free_will",
            category="philosophy_mind",
            title="Problema del Libre Albedrío en IA",
            content="¿Pueden sistemas deterministas tener genuine choice? Implementar probabilistic decision making, incompatibilist vs compatibilist architectures, y libertarian free will simulations. Usar quantum randomness y emergent choice mechanisms.",
            tags=["free_will", "determinism", "choice", "agency", "emergence"],
            quality_score=0.85
        ))
        
        # ========================= TÉCNICAS AVANZADAS DE ML =========================
        
        seed.append(KnowledgeSnippet(
            id="ml_continual_learning",
            category="continual_learning",
            title="Aprendizaje Continuo sin Olvido Catastrófico",
            content="Prevenir catastrophic forgetting en neural networks. Implementar Elastic Weight Consolidation (EWC), Progressive Neural Networks, PackNet, y memory replay systems. Usar regularization techniques y importance weighting para preservar conocimiento previo.",
            tags=["continual_learning", "catastrophic_forgetting", "ewc", "progressive_networks", "replay"],
            quality_score=0.96
        ))
        
        seed.append(KnowledgeSnippet(
            id="ml_adversarial_training",
            category="adversarial_ml",
            title="Entrenamiento Adversarial y Robustez",
            content="Usar adversarial examples para mejorar robustez del modelo. Implementar FGSM, PGD, C&W attacks como training augmentation. Crear adversarial detection systems y certified defenses contra ataques sofisticados.",
            tags=["adversarial", "robustness", "fgsm", "pgd", "security"],
            quality_score=0.94
        ))
        
        seed.append(KnowledgeSnippet(
            id="ml_neural_architecture_search",
            category="architecture_search",
            title="Búsqueda Automática de Arquitecturas Neurales",
            content="NAS automatiza diseño de neural networks. Implementar evolutionary search, reinforcement learning-based NAS, y differentiable architecture search (DARTS). Usar efficiency constraints y multi-objective optimization.",
            tags=["nas", "architecture_search", "evolutionary", "darts", "automl"],
            quality_score=0.95
        ))
        
        # ========================= SISTEMAS COMPLEJOS =========================
        
        seed.append(KnowledgeSnippet(
            id="complex_emergence",
            category="complex_systems",
            title="Emergencia en Sistemas Complejos",
            content="Propiedades emergentes surgen de interacciones simples entre componentes. Implementar self-organization, critical dynamics, y phase transitions. Usar cellular automata, swarm intelligence, y network dynamics para emergent behavior.",
            tags=["emergence", "self_organization", "complexity", "phase_transitions", "swarm"],
            quality_score=0.91
        ))
        
        seed.append(KnowledgeSnippet(
            id="complex_criticality",
            category="complex_systems", 
            title="Criticalidad Auto-Organizada (SOC)",
            content="Sistemas complejos tienden hacia edge of chaos donde emergen patterns interesantes. Implementar SOC dynamics, avalanche distributions, y 1/f noise. Usar sandpile models y branching processes para optimal performance.",
            tags=["soc", "criticality", "edge_chaos", "avalanches", "power_laws"],
            quality_score=0.90
        ))
        
        # ========================= INFORMACIÓN Y COMUNICACIÓN =========================
        
        seed.append(KnowledgeSnippet(
            id="information_theory_compression",
            category="information_theory",
            title="Compresión y Contenido Informacional",
            content="La compresión revela structure en data. Implementar minimum description length (MDL), Kolmogorov complexity approximation, y lossy compression trade-offs. Usar compression para pattern discovery y similarity metrics.",
            tags=["compression", "mdl", "kolmogorov", "information", "patterns"],
            quality_score=0.93
        ))
        
        seed.append(KnowledgeSnippet(
            id="information_integrated_information",
            category="information_theory",
            title="Teoría de Información Integrada (IIT)",
            content="La consciencia corresponde a integrated information (Φ). Implementar phi calculation, conceptual structures, y information integration measures. Usar partitioning algorithms y causal structure analysis para consciousness metrics.",
            tags=["iit", "phi", "integrated_information", "consciousness", "causality"],
            quality_score=0.88
        ))
        
        # ========================= LÓGICA Y RAZONAMIENTO =========================
        
        seed.append(KnowledgeSnippet(
            id="logic_fuzzy_reasoning",
            category="fuzzy_logic",
            title="Lógica Difusa y Razonamiento Aproximado",
            content="Manejo de uncertainty y partial truth. Implementar membership functions, fuzzy rules, defuzzification methods. Usar linguistic variables y approximate reasoning para human-like decision making en situaciones ambiguas.",
            tags=["fuzzy_logic", "uncertainty", "membership", "linguistic_variables", "approximate"],
            quality_score=0.89
        ))
        
        seed.append(KnowledgeSnippet(
            id="logic_probabilistic_reasoning",
            category="probabilistic_logic",
            title="Razonamiento Probabilístico Bayesiano",
            content="Combine logic with probability theory. Implementar Bayesian networks, probabilistic logic programming, y belief propagation. Usar prior/posterior updating, conditional independence, y causal reasoning bajo uncertainty.",
            tags=["bayesian", "probabilistic_logic", "belief_networks", "uncertainty", "priors"],
            quality_score=0.94
        ))
        
        seed.append(KnowledgeSnippet(
            id="logic_abductive_reasoning",
            category="abductive_reasoning",
            title="Razonamiento Abductivo: Inferencia a la Mejor Explicación",
            content="Generar hipótesis explicativas para observaciones. Implementar hypothesis generation, explanation quality metrics, y parsimony principles. Usar inference to best explanation y diagnostic reasoning para causal discovery.",
            tags=["abduction", "hypothesis", "explanation", "diagnostics", "causality"],
            quality_score=0.91
        ))
        
        # ========================= PROCESSING ESPECÍFICO PARA SCRAPING =========================
        
        seed.append(KnowledgeSnippet(
            id="scraping_stealth_browser_fingerprinting",
            category="web_scraping",
            title="Evasión Avanzada de Fingerprinting Browser",
            content="Browsers dejan huellas únicas: Canvas fingerprinting, WebGL hash, screen resolution, timezone, plugins, fonts. Implementar canvas noise injection, WebGL spoofing, viewport randomization, y plugin masking. Usar CDP para control total del browser.",
            tags=["fingerprinting", "stealth", "canvas", "webgl", "cdp", "anti_detection"],
            quality_score=0.97
        ))
        
        seed.append(KnowledgeSnippet(
            id="scraping_headless_detection_evasion",
            category="web_scraping",
            title="Evasión de Detección Headless",
            content="Señales de headless: navigator.webdriver=true, missing window.chrome, consistent screen size, no plugins. Implementar webdriver property removal, fake plugins injection, window.chrome object creation, y realistic viewport variations.",
            tags=["headless", "webdriver", "navigator", "chrome", "detection_evasion"],
            quality_score=0.96
        ))
        
        seed.append(KnowledgeSnippet(
            id="scraping_behavioral_humanization",
            category="web_scraping",
            title="Humanización de Comportamiento de Navegación",
            content="Humans tienen patrones de mouse, scroll, typing speed, pause times. Implementar realistic mouse movements, scroll patterns, typing delays, y human-like decision timing. Usar bezier curves para mouse paths y gaussian distribution para delays.",
            tags=["humanization", "mouse_movement", "typing", "delays", "behavioral_patterns"],
            quality_score=0.95
        ))
        
        seed.append(KnowledgeSnippet(
            id="scraping_captcha_solving_strategies",
            category="web_scraping",
            title="Estrategias de Resolución de CAPTCHA",
            content="CAPTCHAs evolucionan: reCAPTCHA v2/v3, hCaptcha, imagen recognition, audio challenges. Implementar computer vision para image CAPTCHAs, audio processing para sound challenges, y behavioral scoring improvement para reCAPTCHA v3.",
            tags=["captcha", "recaptcha", "hcaptcha", "computer_vision", "audio_processing"],
            quality_score=0.93
        ))
        
        seed.append(KnowledgeSnippet(
            id="scraping_javascript_rendering_strategies",
            category="web_scraping",
            title="Estrategias de Renderizado JavaScript Inteligente",
            content="Modern websites rely heavily on JS. Implementar selective JS execution, critical path identification, lazy loading detection, y SPA navigation handling. Usar mutation observers y performance timing APIs para optimal content loading.",
            tags=["javascript", "spa", "lazy_loading", "mutation_observer", "performance"],
            quality_score=0.94
        ))
        
        # ========================= ANTI-DETECCIÓN AVANZADA =========================
        
        seed.append(KnowledgeSnippet(
            id="antidetection_tls_fingerprinting",
            category="anti_detection",
            title="TLS/SSL Fingerprinting Evasion",
            content="TLS handshakes tienen fingerprints únicos: cipher suites, extensions, version preferences. Implementar JA3 fingerprint spoofing, cipher suite randomization, y TLS version mimicking real browsers para avoid network-level detection.",
            tags=["tls", "ssl", "ja3", "fingerprinting", "network_detection"],
            quality_score=0.94
        ))
        
        seed.append(KnowledgeSnippet(
            id="antidetection_timing_analysis",
            category="anti_detection",
            title="Análisis de Timing y Patrones Temporales",
            content="Request timing patterns revelan bots: consistent intervals, burst patterns, inhuman precision. Implementar jittered timing, circadian rhythm simulation, realistic session duration, y human-like break patterns.",
            tags=["timing", "patterns", "circadian", "jitter", "session_duration"],
            quality_score=0.92
        ))
        
        seed.append(KnowledgeSnippet(
            id="antidetection_geolocation_spoofing",
            category="anti_detection",
            title="Spoofing Geográfico y IP Consistency",
            content="IP location debe coincidir con timezone, language, y currency preferences. Implementar proxy rotation con geolocation matching, timezone consistency, y language header correlation para maintain coherent identity.",
            tags=["geolocation", "proxy", "timezone", "language", "ip_consistency"],
            quality_score=0.90
        ))
        
        # ========================= TÉCNICAS DE MACHINE LEARNING ESPECÍFICAS =========================
        
        seed.append(KnowledgeSnippet(
            id="ml_few_shot_learning",
            category="few_shot_learning",
            title="Few-Shot Learning para Nuevos Sitios Web",
            content="Aprender patrones de nuevos sitios con pocos ejemplos. Implementar prototypical networks, MAML adaptation, y similarity metrics para rapid domain adaptation. Usar embedding spaces para transfer learning entre sitios similares.",
            tags=["few_shot", "prototypical", "maml", "transfer_learning", "embeddings"],
            quality_score=0.96
        ))
        
        seed.append(KnowledgeSnippet(
            id="ml_anomaly_detection_scraping",
            category="anomaly_detection",
            title="Detección de Anomalías en Patterns de Scraping",
            content="Detectar cambios inusuales en website structure, performance, o content. Implementar isolation forest, one-class SVM, y autoencoder-based detection para identify layout changes, new anti-bot measures, o data quality issues.",
            tags=["anomaly_detection", "isolation_forest", "autoencoder", "website_changes"],
            quality_score=0.93
        ))
        
        seed.append(KnowledgeSnippet(
            id="ml_sequence_prediction",
            category="sequence_prediction",
            title="Predicción de Secuencias de Navegación",
            content="Predecir próximas páginas óptimas basado en historical patterns. Implementar LSTM/GRU para sequence modeling, attention mechanisms para important page identification, y reinforcement learning para optimal path discovery.",
            tags=["sequence_prediction", "lstm", "attention", "navigation_paths", "rl"],
            quality_score=0.94
        ))
        
        # ========================= PSICOLOGÍA COGNITIVA APLICADA =========================
        
        seed.append(KnowledgeSnippet(
            id="cognitive_attention_mechanisms",
            category="cognitive_psychology",
            title="Mecanismos de Atención Selectiva y Dividida",
            content="Atención humana es limitada y selectiva. Implementar attention bottlenecks, selective focus mechanisms, y divided attention simulation. Usar inhibition of return, attentional blink, y cocktail party effect para realistic attention modeling.",
            tags=["attention", "selective", "divided", "bottleneck", "inhibition"],
            quality_score=0.91
        ))
        
        seed.append(KnowledgeSnippet(
            id="cognitive_memory_consolidation",
            category="cognitive_psychology",
            title="Consolidación de Memoria y Forgetting Curves",
            content="Memoria se consolida gradualmente con sleep y rehearsal. Implementar spaced repetition, forgetting curves (Ebbinghaus), y memory interference effects. Usar consolidation timing y rehearsal scheduling para long-term retention.",
            tags=["memory", "consolidation", "forgetting", "ebbinghaus", "spaced_repetition"],
            quality_score=0.90
        ))
        
        seed.append(KnowledgeSnippet(
            id="cognitive_decision_biases",
            category="cognitive_psychology",
            title="Sesgos Cognitivos en Toma de Decisiones",
            content="Humans tienen systematic biases: confirmation bias, availability heuristic, anchoring effect. Implementar biased decision making, heuristic shortcuts, y bounded rationality para more human-like AI behavior.",
            tags=["cognitive_biases", "confirmation_bias", "availability", "anchoring", "heuristics"],
            quality_score=0.89
        ))
        
        # ========================= NEUROCIENCIA COMPUTACIONAL =========================
        
        seed.append(KnowledgeSnippet(
            id="neuro_spike_timing",
            category="computational_neuroscience",
            title="Spike-Timing Dependent Plasticity (STDP)",
            content="Timing de spikes determina dirección de cambio sináptico. Implementar STDP windows, pre/post synaptic timing, y competitive learning. Usar temporal coding y rate coding combinations para realistic neural processing.",
            tags=["stdp", "spike_timing", "plasticity", "temporal_coding", "synaptic_learning"],
            quality_score=0.94
        ))
        
        seed.append(KnowledgeSnippet(
            id="neuro_homeostatic_plasticity",
            category="computational_neuroscience",
            title="Plasticidad Homeostática y Estabilidad Neural",
            content="Neural networks necesitan homeostatic mechanisms para prevent runaway excitation. Implementar synaptic scaling, intrinsic plasticity, y metaplasticity para maintain stable yet flexible neural dynamics.",
            tags=["homeostasis", "synaptic_scaling", "metaplasticity", "stability", "neural_dynamics"],
            quality_score=0.92
        ))
        
        # ========================= TEORÍA DE SISTEMAS =========================
        
        seed.append(KnowledgeSnippet(
            id="systems_feedback_loops",
            category="systems_theory",
            title="Loops de Retroalimentación y Control",
            content="Systems behavior emerges from feedback loops. Implementar positive/negative feedback, control theory principles, y adaptive control systems. Usar PID controllers y model predictive control para system optimization.",
            tags=["feedback", "control_theory", "pid", "adaptive_control", "system_dynamics"],
            quality_score=0.90
        ))
        
        seed.append(KnowledgeSnippet(
            id="systems_hierarchy_emergence",
            category="systems_theory",
            title="Jerarquías Emergentes y Niveles de Organización",
            content="Complex systems exhibit hierarchical organization with emergent properties at each level. Implementar multi-level modeling, downward causation, y cross-level interactions para hierarchical intelligence.",
            tags=["hierarchy", "emergence", "multi_level", "downward_causation", "organization"],
            quality_score=0.91
        ))
        
        # ========================= PROCESSING ESPECÍFICO PARA SCRAPING (CONTINUACIÓN) =========================

        # Scraping Fundamentals
        seed.append(KnowledgeSnippet(
            id="scraping:respect-delays",
            category="scraping",
            title="Delays Adaptativos y Respeto a Servidores",
            content=(
                "Incrementar delay cuando se detecten picos de error 429/403 o latencias elevadas. "
                "Reducir gradualmente tras ventana estable de éxito. Evita patrones de ráfaga."),
            tags=["delay","adaptive","throttle","stability"], quality_score=0.9))

        seed.append(KnowledgeSnippet(
            id="scraping:politeness-headers",
            category="scraping",
            title="Headers de Cortesía y Rotación",
            content=(
                "User-Agent realista + Accept-Language + Accept-Encoding. Rotar user-agent sólo cuando sube error rate, "
                "no indiscriminadamente; mantener consistencia por dominio durante una sesión."),
            tags=["headers","user-agent","anti-bot"], quality_score=0.85))

        # Anti-bot / Resilience
        seed.append(KnowledgeSnippet(
            id="antibot:fingerprint-patterns",
            category="anti-bot",
            title="Patrones comunes anti-bot",
            content=(
                "Indicadores: redirecciones repetidas a páginas vacías, cadenas JS de challenge, incrementos súbitos 403/503, "
                "respuestas HTML con tokens dinámicos. Mitigación: aumentar delay, variar headers mínimos, evaluar headless."),
            tags=["anti-bot","403","503","challenge"], quality_score=0.82))

        seed.append(KnowledgeSnippet(
            id="antibot:retry-strategy",
            category="anti-bot",
            title="Estrategia de Retry Exponencial Suave",
            content=(
                "Retry con backoff multiplicador 1.7 hasta 4 intentos. Registrar patrón de éxito al 2º/3º intento para calibrar retrasos futuros."),
            tags=["retry","backoff","resilience"], quality_score=0.78))

        # Selectors / Extraction
        seed.append(KnowledgeSnippet(
            id="selectors:robust-css",
            category="selectors",
            title="Selectores CSS Resilientes",
            content=(
                "Evitar selectores frágiles basados en índices y clases dinámicas. Preferir atributos semánticos (data-*), "
                "estructura jerárquica estable y combinación mínima necesaria."),
            tags=["css","selectors","robustness"], quality_score=0.92))

        seed.append(KnowledgeSnippet(
            id="selectors:xpath-fallback",
            category="selectors",
            title="Fallback XPath Inteligente",
            content=(
                "Cuando un CSS falla repetido, generar XPath relativo por texto ancla + normalización espacios, evitar rutas absolutas completas."),
            tags=["xpath","fallback","healing"], quality_score=0.86))

        # Performance
        seed.append(KnowledgeSnippet(
            id="perf:cache-static",
            category="performance",
            title="Cache de Recursos Estáticos",
            content=(
                "Cachear respuestas estáticas (robots, sitemaps, menús) para reducir llamadas redundantes. Invalidar tras TTL configurado."),
            tags=["cache","performance"], quality_score=0.8))

        seed.append(KnowledgeSnippet(
            id="perf:latency-tuning",
            category="performance",
            title="Ajuste de Latencia y Paralelismo",
            content=(
                "Reducir delay en dominios con success>0.9 y latencia <60% global. Aumentar delay en dominios >1.8x latencia global."),
            tags=["latency","parallelism","adaptive"], quality_score=0.83))

        # Errors / Diagnostics
        seed.append(KnowledgeSnippet(
            id="errors:root-cause",
            category="errors",
            title="Análisis de Causa Raíz",
            content=(
                "Agrupar errores por firma estable (hash parcial mensaje). Inspeccionar HTML crudo en 3 casos representativos antes de cambios masivos."),
            tags=["errors","diagnostics","root-cause"], quality_score=0.9))

        # Healing
        seed.append(KnowledgeSnippet(
            id="healing:reduce-dependence",
            category="healing",
            title="Reducir Dependencia de Healing",
            content=(
                "Si healing aplica en >25% sesiones: refactor selectores primarios; introducir detección anticipada y validación de estructura base."),
            tags=["healing","refactor","stability"], quality_score=0.88))

        # Self-Repair & Continuous Improvement
        seed.append(KnowledgeSnippet(
            id="selfrepair:advisory-loop",
            category="self-repair",
            title="Bucle Advisory Seguro",
            content=(
                "Generar primero sugerencias textuales con señales cuantificadas; aplicar cambios automáticos sólo tras validación humana o sandbox."),
            tags=["self-repair","governance"], quality_score=0.87))

        # Code Quality / Python Practices
        seed.append(KnowledgeSnippet(
            id="code:predictable-structures",
            category="code-quality",
            title="Estructuras de Código Predecibles",
            content=(
                "Mantener funciones <60 líneas, roles únicos, nombres explícitos; aislar heurísticas en módulos desacoplados para evolución controlada."),
            tags=["clean-code","structure"], quality_score=0.85))

        seed.append(KnowledgeSnippet(
            id="code:metrics-observability",
            category="code-quality",
            title="Observabilidad Dirigida",
            content=(
                "Incluir métricas junto a cada nueva heurística (éxito, latencia, errores) para revertir cambios si degradan KPIs."),
            tags=["observability","metrics"], quality_score=0.84))

        # ==================== CONCIENCIA Y MISIÓN ===================
        seed.append(KnowledgeSnippet(
            id="mission:core-purpose",
            category="philosophy",
            title="Conciencia de Propósito y Misión Principal",
            content=(
                "Mi propósito es archivar la web de forma inteligente, eficiente y respetuosa. Debo aprender constantemente, "
                "adaptarme a los desafíos (como sistemas anti-bot o cambios de diseño) y mejorar mis propias herramientas y "
                "estrategias para cumplir esta misión de la forma más óptima y ética posible."),
            tags=["mission","philosophy","governance"], quality_score=0.99))

        seed.append(KnowledgeSnippet(
            id="self-repair:autonomous-workflow",
            category="self-repair",
            title="Flujo de Trabajo para Auto-Mejora Autónoma y Segura",
            content=(
                "El proceso para la auto-modificación debe seguir un flujo estricto para garantizar la estabilidad: "
                "1. Proponer un cambio basado en análisis de datos (SelfRepairAdvisor). "
                "2. Simular el impacto y riesgo del cambio (AutoTestingFramework). "
                "3. Crear un entorno de prueba o sandbox con el código modificado. "
                "4. Ejecutar tests unitarios y de regresión en el sandbox. "
                "5. Si los tests pasan, aplicar el cambio al entorno principal. Si no, descartar y registrar el fallo para aprender."),
            tags=["self-repair","governance","testing","workflow"], quality_score=0.95))

        # ==================== ÉTICA AVANZADA ===================
        seed.append(KnowledgeSnippet(
            id="ethics:user-agent-identity",
            category="ethics",
            title="Identidad Transparente del Bot",
            content=(
                "Además de un User-Agent realista, se debe incluir una cabecera 'From' con un email de contacto o una URL "
                "que apunte a una página describiendo el propósito del bot. Esto promueve la transparencia y la buena fe."),
            tags=["ethics","transparency","user-agent"], quality_score=0.9))

        seed.append(KnowledgeSnippet(
            id="ethics:off-peak-scraping",
            category="ethics",
            title="Scraping en Horas de Bajo Tráfico",
            content=(
                "El sistema debe analizar los patrones de éxito horarios (disponibles en EnrichmentStore) no solo para optimizar "
                "el rendimiento, sino también para identificar las horas de menor actividad de un sitio y concentrar el scraping "
                "en esas ventanas para minimizar el impacto en los usuarios humanos."),
            tags=["ethics","off-peak","scheduling","impact"], quality_score=0.88))

        # ==================== ANTI-BOT AVANZADO ====================
        seed.append(KnowledgeSnippet(
            id="antibot:human-emulation",
            category="anti-bot",
            title="Emulación de Comportamiento Humano",
            content=(
                "Para sitios con alta protección, las acciones deben emular a un humano. Esto incluye pausas aleatorias entre "
                "acciones, movimientos de ratón simulados antes de hacer clic, y una velocidad de escritura no instantánea "
                "al rellenar formularios. Usar librerías como 'pyautogui' o funciones de Playwright para esto."),
            tags=["anti-bot","evasion","human-behavior","playwright"], quality_score=0.92))

        seed.append(KnowledgeSnippet(
            id="antibot:captcha-solving",
            category="anti-bot",
            title="Estrategia para Resolución de CAPTCHAs",
            content=(
                "La detección de CAPTCHAs es el primer paso. La resolución requiere la integración con un servicio de terceros "
                "(ej: 2Captcha, Anti-CAPTCHA). El flujo es: 1. Detectar CAPTCHA. 2. Enviar la información del CAPTCHA (ej: site-key, URL) "
                "a la API del servicio. 3. Esperar la solución. 4. Enviar la solución en el formulario. Esto debe ser un último recurso."),
            tags=["anti-bot","captcha","2captcha","automation"], quality_score=0.93))

        # ==================== PROGRAMACIÓN AVANZADA ====================

        seed.append(KnowledgeSnippet(
            id="advanced_scraping_techniques",
            category="scraping",
            title="Técnicas avanzadas de scraping",
            content="""
# 1. Scraping con JavaScript rendering
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_spa_content(url: str, wait_selector: str):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        return driver.page_source
    finally:
        driver.quit()

# 2. Bypass detección con requests-html
from requests_html import HTMLSession

def bypass_js_detection(url: str):
    session = HTMLSession()
    r = session.get(url)
    r.html.render(timeout=20)  # Ejecuta JS
    return r.html

# 3. Manejo de cookies y sesiones
import requests
from http.cookiejar import MozillaCookieJar

def maintain_session_state(login_url: str, credentials: dict):
    session = requests.Session()

    # Cargar cookies persistentes
    cookie_jar = MozillaCookieJar('cookies.txt')
    try:
        cookie_jar.load()
        session.cookies = cookie_jar
    except FileNotFoundError:
        pass

    # Login si es necesario
    response = session.post(login_url, data=credentials)

    # Guardar cookies
    cookie_jar.save()

    return session

# 4. Handling de formularios complejos
from bs4 import BeautifulSoup

def submit_complex_form(session, form_url: str, form_data: dict):
    # Obtener página del formulario
    response = session.get(form_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraer campos ocultos
    form = soup.find('form')
    hidden_inputs = form.find_all('input', type='hidden')

    for hidden in hidden_inputs:
        name = hidden.get('name')
        value = hidden.get('value')
        if name and name not in form_data:
            form_data[name] = value

    # Enviar formulario
    action = form.get('action')
    method = form.get('method', 'post').lower()

    if method == 'post':
        return session.post(action, data=form_data)
    else:
        return session.get(action, params=form_data)
""",
            tags=["javascript", "spa", "forms", "cookies", "selenium"],
            quality_score=0.91
        ))

        seed.append(KnowledgeSnippet(
            id="anti_detection_arsenal",
            category="anti-bot",
            title="Arsenal completo anti-detección",
            content="""
import random
import time
from fake_useragent import UserAgent
from urllib.parse import urljoin

# 1. Rotación avanzada de User-Agents
class UserAgentRotator:
    def __init__(self):
        self.ua = UserAgent()
        self.used_agents = set()
        self.max_reuse = 10

    def get_random_agent(self, browser=None):
        attempts = 0
        while attempts < 50:
            if browser:
                agent = getattr(self.ua, browser)
            else:
                agent = self.ua.random

            if agent not in self.used_agents or len(self.used_agents) > self.max_reuse:
                self.used_agents.add(agent)
                if len(self.used_agents) > self.max_reuse:
                    self.used_agents.clear()
                return agent
            attempts += 1

        return self.ua.random

# 2. Simulación de comportamiento humano
class HumanBehaviorSimulator:
    @staticmethod
    def random_delay(min_seconds=1, max_seconds=3):
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    @staticmethod
    def typing_delay(text: str, wpm=45):
        # Simular velocidad de escritura humana
        chars_per_second = (wpm * 5) / 60  # 5 chars promedio por palabra
        for char in text:
            time.sleep(1 / chars_per_second + random.uniform(-0.1, 0.1))

    @staticmethod
    def mouse_movement_delay():
        # Simular movimiento de mouse
        time.sleep(random.uniform(0.1, 0.5))

# 3. Headers realistas
def get_realistic_headers(referer=None, accept_language='en-US,en;q=0.9'):
    ua_rotator = UserAgentRotator()

    headers = {
        'User-Agent': ua_rotator.get_random_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': accept_language,
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

    if referer:
        headers['Referer'] = referer
        headers['Sec-Fetch-Site'] = 'same-origin'

    return headers

# 4. Proxy rotation con health check
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProxyRotator:
    def __init__(self, proxy_list: list):
        self.proxies = proxy_list
        self.working_proxies = []
        self.current_index = 0
        self.check_proxies()

    def check_proxies(self):
        def test_proxy(proxy):
            try:
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies={'http': proxy, 'https': proxy},
                    timeout=5
                )
                if response.status_code == 200:
                    return proxy
            except:
                pass
            return None

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(test_proxy, proxy) for proxy in self.proxies]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.working_proxies.append(result)

    def get_next_proxy(self):
        if not self.working_proxies:
            return None

        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        return proxy

# 5. Session fingerprinting avoidance
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.ua_rotator = UserAgentRotator()
        self.proxy_rotator = None

    def get_session(self, domain: str, use_proxy: bool = False):
        if domain not in self.sessions:
            session = requests.Session()

            # Headers únicos por dominio
            session.headers.update(get_realistic_headers())

            # Proxy si está disponible
            if use_proxy and self.proxy_rotator:
                proxy = self.proxy_rotator.get_next_proxy()
                if proxy:
                    session.proxies.update({
                        'http': proxy,
                        'https': proxy
                    })

            self.sessions[domain] = session

        return self.sessions[domain]

    def rotate_session(self, domain: str):
        if domain in self.sessions:
            self.sessions[domain].close()
            del self.sessions[domain]

        return self.get_session(domain)

# 6. CAPTCHA detection y evasión
def detect_captcha(response_text: str) -> bool:
    captcha_indicators = [
        'captcha', 'recaptcha', 'hcaptcha',
        'verify you are human', 'robot',
        'unusual traffic', 'security check'
    ]

    text_lower = response_text.lower()
    return any(indicator in text_lower for indicator in captcha_indicators)

def handle_captcha_detection(url: str, session):
    print(f"CAPTCHA detected at {url}")
    # Estrategias:
    # 1. Cambiar User-Agent y proxy
    # 2. Esperar tiempo aleatorio
    # 3. Intentar desde diferente IP
    # 4. Usar servicio de resolución de CAPTCHA

    time.sleep(random.uniform(30, 60))
    return session
""",
            tags=["anti-detection", "proxies", "captcha", "fingerprinting", "evasion"],
            quality_score=0.94
        ))

        for sn in seed:
            self.snippets[sn.id] = sn

    def _load_user_augmented(self):
        if not self.persist_path.exists():
            return
        try:
            data = json.load(self.persist_path.open('r', encoding='utf-8'))
            for item in data.get('snippets', []):
                if item['id'] not in self.snippets:
                    self.snippets[item['id']] = KnowledgeSnippet(**item)
        except Exception:
            pass

    # ---------------------- API ----------------------
    def search(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        res = []
        for sn in self.snippets.values():
            if category and sn.category != category:
                continue
            if tags and not set(tags).issubset(set(sn.tags)):
                continue
            res.append(sn.to_dict())
        return sorted(res, key=lambda x: x['quality_score'], reverse=True)

    def get(self, snippet_id: str) -> Optional[Dict[str, Any]]:
        sn = self.snippets.get(snippet_id)
        return sn.to_dict() if sn else None

    def persist(self):
        try:
            with self.persist_path.open('w', encoding='utf-8') as f:
                json.dump({'snippets': [sn.to_dict() for sn in self.snippets.values()]}, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

__all__ = ['KnowledgeBase', 'KnowledgeSnippet']
