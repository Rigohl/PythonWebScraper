"""
Advanced AI Techniques for Intelligent Web Scraping
Técnicas avanzadas de IA para scraping inteligente y autónomo
"""

import numpy as np
import json
import pickle
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import time

# Machine Learning Libraries
try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import IsolationForest
    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class MLScrapingIntelligence:
    """Sistema de inteligencia ML para scraping adaptativo"""

    def __init__(self, data_path: str = "data/ml_intelligence.json"):
        self.data_path = data_path
        self.site_features = {}  # Features extraídas de cada sitio
        self.strategy_performance = {}  # Performance de estrategias por sitio
        self.ml_models = {}  # Modelos entrenados
        self.learning_history = []

        self._load_data()

    def _load_data(self):
        """Carga datos de inteligencia ML desde archivo o inicializa estructura base"""
        import os
        import json

        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.site_features = data.get('site_features', {})
                    self.strategy_performance = data.get('strategy_performance', {})
                    self.learning_history = data.get('learning_history', [])
            else:
                # Crear estructura base si no existe
                os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
                self._save_data()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error loading ML intelligence data: {e}, using defaults")
            # Usar valores por defecto en caso de error
            self.site_features = {}
            self.strategy_performance = {}
            self.learning_history = []

    def _save_data(self):
        """Guarda datos de inteligencia ML a archivo"""
        import json
        import os

        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            data = {
                'site_features': self.site_features,
                'strategy_performance': self.strategy_performance,
                'learning_history': self.learning_history
            }
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving ML intelligence data: {e}")

    def extract_site_features(self, url: str, html: str, response_time: float,
                            status_code: int) -> Dict[str, float]:
        """Extrae features ML de un sitio web"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        features = {
            # Basic metrics
            'response_time': response_time,
            'status_code': status_code,
            'html_size': len(html),

            # DOM structure
            'dom_depth': self._calculate_dom_depth(soup),
            'total_elements': len(soup.find_all()),
            'script_count': len(soup.find_all('script')),
            'link_count': len(soup.find_all('a')),
            'form_count': len(soup.find_all('form')),
            'image_count': len(soup.find_all('img')),

            # Anti-bot indicators
            'has_captcha': self._detect_captcha(soup),
            'has_cloudflare': self._detect_cloudflare(html),
            'has_dynamic_content': self._detect_dynamic_content(soup),
            'obfuscated_js': self._detect_obfuscated_js(soup),

            # Content patterns
            'text_to_html_ratio': self._calculate_text_ratio(soup),
            'external_resources': self._count_external_resources(soup),
            'css_complexity': len(soup.find_all('style')) + len(soup.find_all(class_=True)),
        }

        return features

    def _calculate_dom_depth(self, soup) -> int:
        """Calcula profundidad máxima del DOM"""
        def depth(element, current=0):
            if not element.children:
                return current
            return max(depth(child, current + 1) for child in element.children if child.name)

        try:
            return depth(soup.body or soup)
        except:
            return 0

    def _detect_captcha(self, soup) -> float:
        """Detecta presencia de CAPTCHA"""
        captcha_indicators = [
            'captcha', 'recaptcha', 'hcaptcha', 'turnstile',
            'challenge', 'verification', 'robot', 'human'
        ]

        text = soup.get_text().lower()
        classes = ' '.join([el.get('class', []) for el in soup.find_all() if el.get('class')])
        ids = ' '.join([el.get('id', '') for el in soup.find_all() if el.get('id')])

        score = 0
        for indicator in captcha_indicators:
            if indicator in text:
                score += 0.3
            if indicator in classes.lower():
                score += 0.5
            if indicator in ids.lower():
                score += 0.4

        return min(score, 1.0)

    def _detect_cloudflare(self, html: str) -> float:
        """Detecta Cloudflare protection"""
        cf_indicators = [
            'cloudflare', 'cf-ray', 'cf-browser-verification',
            'cf-challenge', 'checking your browser', 'ddos protection'
        ]

        html_lower = html.lower()
        score = sum(0.2 for indicator in cf_indicators if indicator in html_lower)
        return min(score, 1.0)

    def _detect_dynamic_content(self, soup) -> float:
        """Detecta contenido generado dinámicamente por JS"""
        js_frameworks = [
            'react', 'vue', 'angular', 'ember', 'backbone',
            'jquery', 'prototype', 'mootools'
        ]

        scripts = soup.find_all('script')
        script_text = ' '.join([script.get_text() for script in scripts]).lower()

        score = 0
        for framework in js_frameworks:
            if framework in script_text:
                score += 0.15

        # Detectar SPA patterns
        if 'single page' in script_text or 'spa' in script_text:
            score += 0.3

        # Muchos scripts = likely dynamic
        if len(scripts) > 10:
            score += 0.2

        return min(score, 1.0)

    def _detect_obfuscated_js(self, soup) -> float:
        """Detecta JavaScript ofuscado"""
        scripts = soup.find_all('script')
        score = 0

        for script in scripts:
            script_text = script.get_text()
            if len(script_text) > 100:
                # Indicadores de ofuscación
                obfuscation_indicators = [
                    len([c for c in script_text if c in '!@#$%^&*()']) / len(script_text),  # Special chars ratio
                    script_text.count('eval') + script_text.count('unescape'),  # Eval usage
                    len(script_text.split()) / len(script_text) if script_text else 0,  # Minification
                ]

                if obfuscation_indicators[0] > 0.1:  # High special char ratio
                    score += 0.3
                if obfuscation_indicators[1] > 0:  # Has eval/unescape
                    score += 0.4
                if obfuscation_indicators[2] < 0.1:  # Heavily minified
                    score += 0.2

        return min(score, 1.0)

    def _calculate_text_ratio(self, soup) -> float:
        """Calcula ratio de texto vs HTML"""
        text_length = len(soup.get_text())
        html_length = len(str(soup))
        return text_length / html_length if html_length > 0 else 0

    def _count_external_resources(self, soup) -> int:
        """Cuenta recursos externos"""
        external_count = 0

        # External scripts
        for script in soup.find_all('script', src=True):
            if 'http' in script['src']:
                external_count += 1

        # External stylesheets
        for link in soup.find_all('link', href=True):
            if 'http' in link['href']:
                external_count += 1

        return external_count

class ReinforcementLearningOptimizer:
    """Optimizador basado en Q-Learning para estrategias de scraping"""

    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.9,
                 epsilon: float = 0.1):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon  # Exploration vs exploitation

        # Q-table: state -> action -> Q-value
        self.q_table = {}

        # Action space: diferentes configuraciones de scraping
        self.actions = [
            'low_delay_no_js',     # Delay bajo, sin JS
            'medium_delay_js',     # Delay medio, con JS
            'high_delay_stealth',  # Delay alto, modo stealth
            'proxy_rotation',      # Rotación de proxies
            'session_cookies',     # Mantener sesión
            'headless_browser',    # Browser headless
            'mobile_ua',           # User agent móvil
            'slow_human_mimic'     # Imitación lenta humana
        ]

    def get_state_key(self, features: Dict[str, float]) -> str:
        """Convierte features en key de estado discreto"""
        # Discretizar features continuas
        discrete_features = {}

        discrete_features['response_time'] = 'fast' if features['response_time'] < 1 else \
                                           'medium' if features['response_time'] < 3 else 'slow'

        discrete_features['complexity'] = 'low' if features['dom_depth'] < 5 else \
                                        'medium' if features['dom_depth'] < 10 else 'high'

        discrete_features['anti_bot'] = 'low' if features.get('has_captcha', 0) < 0.3 else \
                                      'medium' if features.get('has_captcha', 0) < 0.7 else 'high'

        return f"{discrete_features['response_time']}_{discrete_features['complexity']}_{discrete_features['anti_bot']}"

    def select_action(self, state_key: str) -> str:
        """Selecciona acción usando epsilon-greedy"""
        if np.random.random() < self.epsilon:
            # Exploration: acción aleatoria
            return np.random.choice(self.actions)
        else:
            # Exploitation: mejor acción conocida
            if state_key not in self.q_table:
                return np.random.choice(self.actions)

            state_q_values = self.q_table[state_key]
            return max(state_q_values.items(), key=lambda x: x[1])[0]

    def update_q_value(self, state_key: str, action: str, reward: float,
                      next_state_key: str = None):
        """Actualiza Q-value usando Q-learning"""
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0.0 for action in self.actions}

        if action not in self.q_table[state_key]:
            self.q_table[state_key][action] = 0.0

        # Q-learning update
        current_q = self.q_table[state_key][action]

        if next_state_key and next_state_key in self.q_table:
            max_next_q = max(self.q_table[next_state_key].values())
        else:
            max_next_q = 0.0

        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[state_key][action] = new_q

    def calculate_reward(self, success: bool, response_time: float,
                        errors: int) -> float:
        """Calcula reward basado en performance"""
        reward = 0.0

        # Success reward
        if success:
            reward += 10.0
        else:
            reward -= 5.0

        # Speed bonus/penalty
        if response_time < 1.0:
            reward += 2.0
        elif response_time > 5.0:
            reward -= 1.0

        # Error penalty
        reward -= errors * 2.0

        return reward

class NeuralStrategyPredictor:
    """Red neuronal para predecir estrategia óptima"""

    def __init__(self, input_size: int = 15, hidden_size: int = 64,
                 output_size: int = 8):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        if TORCH_AVAILABLE:
            self.model = self._create_model()
            self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            self.criterion = nn.CrossEntropyLoss()
        else:
            logger.warning("PyTorch not available, neural predictor disabled")
            self.model = None

    def _create_model(self):
        """Crea modelo neural"""
        if not TORCH_AVAILABLE:
            return None

        class StrategyNet(nn.Module):
            def __init__(self, input_size, hidden_size, output_size):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size // 2, output_size),
                    nn.Softmax(dim=1)
                )

            def forward(self, x):
                return self.layers(x)

        return StrategyNet(self.input_size, self.hidden_size, self.output_size)

    def predict_strategy(self, features: Dict[str, float]) -> int:
        """Predice índice de estrategia óptima"""
        if not self.model:
            return 0

        # Convertir features a tensor
        feature_vector = self._features_to_vector(features)

        with torch.no_grad():
            prediction = self.model(feature_vector.unsqueeze(0))
            return prediction.argmax().item()

    def train_on_batch(self, features_batch: List[Dict], strategy_labels: List[int]):
        """Entrena modelo con batch de datos"""
        if not self.model:
            return

        # Convertir a tensors
        X = torch.stack([self._features_to_vector(f) for f in features_batch])
        y = torch.tensor(strategy_labels, dtype=torch.long)

        # Forward pass
        predictions = self.model(X)
        loss = self.criterion(predictions, y)

        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def _features_to_vector(self, features: Dict[str, float]) -> torch.Tensor:
        """Convierte features dict a tensor"""
        if not TORCH_AVAILABLE:
            return None

        # Lista ordenada de features esperadas
        feature_names = [
            'response_time', 'html_size', 'dom_depth', 'total_elements',
            'script_count', 'link_count', 'form_count', 'image_count',
            'has_captcha', 'has_cloudflare', 'has_dynamic_content',
            'obfuscated_js', 'text_to_html_ratio', 'external_resources',
            'css_complexity'
        ]

        vector = [features.get(name, 0.0) for name in feature_names]
        return torch.tensor(vector, dtype=torch.float32)

class PatternClusterer:
    """Clustering de sitios para identificar patrones similares"""

    def __init__(self, eps: float = 0.5, min_samples: int = 2):
        self.eps = eps
        self.min_samples = min_samples
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.clusterer = DBSCAN(eps=eps, min_samples=min_samples) if SKLEARN_AVAILABLE else None
        self.clusters = {}

    def fit_predict(self, sites_features: Dict[str, Dict[str, float]]) -> Dict[str, int]:
        """Agrupa sitios en clusters basado en features"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, clustering disabled")
            return {site: 0 for site in sites_features.keys()}

        # Preparar datos
        sites = list(sites_features.keys())
        features_matrix = np.array([list(features.values()) for features in sites_features.values()])

        # Normalizar features
        features_scaled = self.scaler.fit_transform(features_matrix)

        # Clustering
        cluster_labels = self.clusterer.fit_predict(features_scaled)

        # Mapear resultados
        site_clusters = dict(zip(sites, cluster_labels))

        # Agrupar sitios por cluster
        self.clusters = {}
        for site, cluster in site_clusters.items():
            if cluster not in self.clusters:
                self.clusters[cluster] = []
            self.clusters[cluster].append(site)

        return site_clusters

    def get_similar_sites(self, target_site: str) -> List[str]:
        """Obtiene sitios similares al target"""
        for cluster_id, sites in self.clusters.items():
            if target_site in sites:
                return [site for site in sites if site != target_site]
        return []

class AnomalyDetector:
    """Detector de anomalías en comportamiento de sitios"""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.detector = IsolationForest(contamination=contamination) if SKLEARN_AVAILABLE else None
        self.baseline_features = {}

    def fit_baseline(self, normal_features: List[Dict[str, float]]):
        """Entrena detector con datos normales"""
        if not SKLEARN_AVAILABLE:
            return

        features_matrix = np.array([list(f.values()) for f in normal_features])
        self.detector.fit(features_matrix)

        # Guardar estadísticas baseline
        self.baseline_features = {
            'mean': np.mean(features_matrix, axis=0),
            'std': np.std(features_matrix, axis=0),
            'feature_names': list(normal_features[0].keys()) if normal_features else []
        }

    def detect_anomaly(self, features: Dict[str, float]) -> Tuple[bool, float]:
        """Detecta si features son anómalas"""
        if not self.detector:
            return False, 0.0

        feature_vector = np.array([list(features.values())]).reshape(1, -1)

        # Predicción: -1 = anomalía, 1 = normal
        prediction = self.detector.predict(feature_vector)[0]

        # Score: menor valor = más anómalo
        anomaly_score = self.detector.decision_function(feature_vector)[0]

        is_anomaly = prediction == -1
        confidence = abs(anomaly_score)

        return is_anomaly, confidence

class AdvancedMLIntelligence:
    """Sistema principal que integra todas las técnicas ML"""

    def __init__(self, data_path: str = "data/advanced_ml_intelligence.pkl"):
        self.data_path = data_path

        # Componentes ML
        self.feature_extractor = MLScrapingIntelligence()
        self.rl_optimizer = ReinforcementLearningOptimizer()
        self.neural_predictor = NeuralStrategyPredictor()
        self.pattern_clusterer = PatternClusterer()
        self.anomaly_detector = AnomalyDetector()

        # Datos de entrenamiento
        self.training_data = []
        self.performance_history = {}

        self._load_models()

    def analyze_and_recommend(self, url: str, html: str, response_time: float,
                            status_code: int) -> Dict[str, Any]:
        """Análisis completo y recomendación de estrategia"""

        # 1. Extraer features
        features = self.feature_extractor.extract_site_features(
            url, html, response_time, status_code
        )

        # 2. Detección de anomalías
        is_anomaly, anomaly_confidence = self.anomaly_detector.detect_anomaly(features)

        # 3. Clustering - encontrar sitios similares
        site_clusters = self.pattern_clusterer.fit_predict({url: features})
        similar_sites = self.pattern_clusterer.get_similar_sites(url)

        # 4. RL optimization
        state_key = self.rl_optimizer.get_state_key(features)
        rl_action = self.rl_optimizer.select_action(state_key)

        # 5. Neural prediction
        neural_strategy_idx = self.neural_predictor.predict_strategy(features)

        recommendation = {
            'features': features,
            'anomaly_detected': is_anomaly,
            'anomaly_confidence': anomaly_confidence,
            'cluster_id': site_clusters.get(url, -1),
            'similar_sites': similar_sites,
            'rl_recommended_action': rl_action,
            'neural_strategy_index': neural_strategy_idx,
            'state_key': state_key,
            'confidence_score': self._calculate_confidence(features, is_anomaly)
        }

        return recommendation

    def learn_from_outcome(self, url: str, recommendation: Dict[str, Any],
                          success: bool, final_response_time: float, errors: int):
        """Aprende del resultado de la estrategia aplicada"""

        # 1. RL learning
        reward = self.rl_optimizer.calculate_reward(success, final_response_time, errors)
        self.rl_optimizer.update_q_value(
            recommendation['state_key'],
            recommendation['rl_recommended_action'],
            reward
        )

        # 2. Guardar datos para entrenamiento neural
        training_sample = {
            'features': recommendation['features'],
            'strategy_used': recommendation['neural_strategy_index'],
            'outcome': {
                'success': success,
                'response_time': final_response_time,
                'errors': errors,
                'reward': reward
            },
            'timestamp': time.time()
        }

        self.training_data.append(training_sample)

        # 3. Re-entrenar modelos periódicamente
        if len(self.training_data) % 50 == 0:
            self._retrain_models()

        # 4. Actualizar historial de performance
        if url not in self.performance_history:
            self.performance_history[url] = []

        self.performance_history[url].append({
            'timestamp': time.time(),
            'success': success,
            'response_time': final_response_time,
            'errors': errors,
            'strategy': recommendation['rl_recommended_action']
        })

        logger.info(f"ML system learned from {url}: success={success}, reward={reward:.2f}")

    def _calculate_confidence(self, features: Dict[str, float], is_anomaly: bool) -> float:
        """Calcula score de confianza en las recomendaciones"""
        base_confidence = 0.8

        # Reducir confianza si es anomalía
        if is_anomaly:
            base_confidence *= 0.6

        # Ajustar según complejidad del sitio
        complexity_score = features.get('dom_depth', 0) / 20.0  # Normalizar
        if complexity_score > 0.8:
            base_confidence *= 0.8

        # Ajustar según anti-bot presence
        anti_bot_score = features.get('has_captcha', 0) + features.get('has_cloudflare', 0)
        if anti_bot_score > 0.5:
            base_confidence *= 0.7

        return max(0.1, min(1.0, base_confidence))

    def _retrain_models(self):
        """Re-entrena modelos con nuevos datos"""
        if len(self.training_data) < 10:
            return

        # Preparar datos para entrenamiento neural
        recent_data = self.training_data[-100:]  # Últimos 100 samples

        features_batch = [sample['features'] for sample in recent_data]

        # Strategy labels basados en éxito
        strategy_labels = []
        for sample in recent_data:
            if sample['outcome']['success'] and sample['outcome']['reward'] > 5:
                strategy_labels.append(sample['strategy_used'])
            else:
                # Si falló, usar estrategia diferente
                strategy_labels.append((sample['strategy_used'] + 1) % 8)

        # Entrenar neural network
        if self.neural_predictor.model and len(strategy_labels) > 5:
            loss = self.neural_predictor.train_on_batch(features_batch, strategy_labels)
            logger.info(f"Neural model retrained, loss: {loss:.4f}")

        # Re-fit anomaly detector con datos normales
        successful_features = [
            sample['features'] for sample in recent_data
            if sample['outcome']['success']
        ]

        if len(successful_features) > 5:
            self.anomaly_detector.fit_baseline(successful_features)
            logger.info("Anomaly detector retrained")

    def _load_models(self):
        """Carga modelos persistidos"""
        try:
            with open(self.data_path, 'rb') as f:
                data = pickle.load(f)
                self.rl_optimizer.q_table = data.get('q_table', {})
                self.training_data = data.get('training_data', [])
                self.performance_history = data.get('performance_history', {})
                logger.info("ML models loaded successfully")
        except FileNotFoundError:
            logger.info("No saved models found, starting fresh")
        except Exception as e:
            logger.warning(f"Error loading ML models: {e}")

    def save_models(self):
        """Persiste modelos entrenados"""
        try:
            data = {
                'q_table': self.rl_optimizer.q_table,
                'training_data': self.training_data[-1000:],  # Últimos 1000 samples
                'performance_history': self.performance_history,
                'timestamp': time.time()
            }

            with open(self.data_path, 'wb') as f:
                pickle.dump(data, f)

            logger.info("ML models saved successfully")
        except Exception as e:
            logger.error(f"Error saving ML models: {e}")

    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Resumen del estado de inteligencia ML"""
        return {
            'total_training_samples': len(self.training_data),
            'q_table_size': len(self.rl_optimizer.q_table),
            'sites_analyzed': len(self.performance_history),
            'clusters_discovered': len(self.pattern_clusterer.clusters),
            'neural_model_available': self.neural_predictor.model is not None,
            'sklearn_available': SKLEARN_AVAILABLE,
            'torch_available': TORCH_AVAILABLE,
            'last_retrain': max([s.get('timestamp', 0) for s in self.training_data]) if self.training_data else 0
        }
