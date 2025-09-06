"""
ADAPTADOR DEL CEREBRO PARA MÚLTIPLES BASES DE DATOS
==================================================

Este módulo integra el conocimiento de múltiples bases de datos con el cerebro artificial,
permitiendo que tome decisiones inteligentes sobre qué tipo de base de datos usar
para diferentes tipos de datos y consultas.
"""

from typing import Any, Dict, List, Optional

from .knowledge_store import KnowledgeStore, MultiDatabaseManager


class DatabaseBrainAdapter:
    """Adaptador que conecta el cerebro con múltiples sistemas de bases de datos."""

    def __init__(self, knowledge_store: KnowledgeStore):
        self.knowledge_store = knowledge_store
        self.db_manager = MultiDatabaseManager()
        self.database_configs = {}

        # Configuraciones predeterminadas para diferentes tipos de datos
        self.data_type_recommendations = {
            "web_scraping_results": {
                "primary": "mongodb",
                "backup": "postgresql",
                "reason": "Document structure with flexible schema",
            },
            "user_sessions": {
                "primary": "redis",
                "backup": "postgresql",
                "reason": "Fast access and expiration capabilities",
            },
            "search_content": {
                "primary": "elasticsearch",
                "backup": "postgresql",
                "reason": "Full-text search and analytics",
            },
            "time_series_metrics": {
                "primary": "influxdb",
                "backup": "postgresql",
                "reason": "Optimized for time-series data",
            },
            "graph_relationships": {
                "primary": "neo4j",
                "backup": "postgresql",
                "reason": "Native graph operations",
            },
            "configuration_data": {
                "primary": "postgresql",
                "backup": "sqlite",
                "reason": "ACID compliance and structured data",
            },
            "cache_data": {
                "primary": "redis",
                "backup": "memcached",
                "reason": "In-memory performance",
            },
            "analytics_data": {
                "primary": "clickhouse",
                "backup": "postgresql",
                "reason": "Column-oriented for analytics",
            },
        }

    def analyze_data_requirements(
        self, data_description: str, data_sample: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Analiza los requisitos de datos y recomienda la mejor base de datos."""

        # Analizar características de los datos
        characteristics = self._extract_data_characteristics(
            data_description, data_sample
        )

        # Obtener conocimiento de bases de datos del cerebro
        db_knowledge = self._get_database_knowledge()

        # Calcular puntuaciones para cada tipo de base de datos
        scores = self._calculate_database_scores(characteristics, db_knowledge)

        # Generar recomendación
        recommendation = self._generate_recommendation(scores, characteristics)

        return {
            "characteristics": characteristics,
            "recommendation": recommendation,
            "scores": scores,
            "reasoning": self._explain_recommendation(recommendation, characteristics),
        }

    def _extract_data_characteristics(
        self, description: str, sample: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Extrae características de los datos basándose en la descripción y muestra."""

        characteristics = {
            "structure": "unknown",
            "size_estimate": "medium",
            "query_patterns": [],
            "consistency_requirements": "eventual",
            "scalability_needs": "moderate",
            "real_time_requirements": False,
            "search_requirements": False,
            "analytics_requirements": False,
        }

        description_lower = description.lower()

        # Detectar estructura
        if any(
            word in description_lower
            for word in ["json", "document", "nested", "flexible"]
        ):
            characteristics["structure"] = "document"
        elif any(
            word in description_lower
            for word in ["table", "relational", "structured", "normalized"]
        ):
            characteristics["structure"] = "relational"
        elif any(
            word in description_lower
            for word in ["key-value", "cache", "session", "temporary"]
        ):
            characteristics["structure"] = "key_value"
        elif any(
            word in description_lower
            for word in ["graph", "relationship", "network", "connected"]
        ):
            characteristics["structure"] = "graph"
        elif any(
            word in description_lower
            for word in ["time-series", "metrics", "logs", "events"]
        ):
            characteristics["structure"] = "time_series"

        # Detectar tamaño
        if any(
            word in description_lower
            for word in ["big", "large", "massive", "petabyte", "terabyte"]
        ):
            characteristics["size_estimate"] = "large"
        elif any(
            word in description_lower
            for word in ["small", "tiny", "minimal", "kilobyte"]
        ):
            characteristics["size_estimate"] = "small"

        # Detectar patrones de consulta
        if any(
            word in description_lower for word in ["search", "text search", "full-text"]
        ):
            characteristics["search_requirements"] = True
            characteristics["query_patterns"].append("full_text_search")

        if any(
            word in description_lower
            for word in ["analytics", "reporting", "aggregation", "olap"]
        ):
            characteristics["analytics_requirements"] = True
            characteristics["query_patterns"].append("analytics")

        if any(
            word in description_lower for word in ["real-time", "live", "streaming"]
        ):
            characteristics["real_time_requirements"] = True

        # Detectar requisitos de consistencia
        if any(
            word in description_lower
            for word in ["acid", "transaction", "consistency", "critical"]
        ):
            characteristics["consistency_requirements"] = "strong"

        # Analizar muestra si está disponible
        if sample:
            characteristics.update(self._analyze_sample_data(sample))

        return characteristics

    def _analyze_sample_data(self, sample: Dict) -> Dict[str, Any]:
        """Analiza una muestra de datos para determinar características."""

        analysis = {}

        # Calcular profundidad de anidamiento
        max_depth = self._calculate_nesting_depth(sample)
        if max_depth > 3:
            analysis["structure"] = "document"
        elif max_depth <= 1:
            analysis["structure"] = "relational"

        # Detectar tipos de datos
        field_types = self._analyze_field_types(sample)
        if "datetime" in field_types:
            analysis["has_temporal_data"] = True
        if "text" in field_types and len([f for f in field_types if f == "text"]) > 2:
            analysis["text_heavy"] = True

        return analysis

    def _calculate_nesting_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calcula la profundidad máxima de anidamiento en un objeto."""

        if not isinstance(obj, (dict, list)):
            return current_depth

        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(
                self._calculate_nesting_depth(v, current_depth + 1)
                for v in obj.values()
            )

        if isinstance(obj, list):
            if not obj:
                return current_depth
            return max(
                self._calculate_nesting_depth(item, current_depth + 1) for item in obj
            )

        return current_depth

    def _analyze_field_types(self, obj: Dict) -> List[str]:
        """Analiza los tipos de campos en un objeto."""

        types = []

        def extract_types(item):
            if isinstance(item, dict):
                for value in item.values():
                    extract_types(value)
            elif isinstance(item, list):
                for value in item:
                    extract_types(value)
            elif isinstance(item, str):
                if len(item) > 50:
                    types.append("text")
                elif any(char in item for char in ["-", ":", "T"]):
                    types.append("datetime")
                else:
                    types.append("string")
            elif isinstance(item, (int, float)):
                types.append("number")
            elif isinstance(item, bool):
                types.append("boolean")

        extract_types(obj)
        return types

    def _get_database_knowledge(self) -> Dict[str, Any]:
        """Obtiene conocimiento sobre bases de datos del cerebro."""

        try:
            # Buscar conocimiento de bases de datos
            knowledge = self.knowledge_store.search_knowledge("databases", limit=50)

            db_knowledge = {}
            for item in knowledge:
                category = item.get("category", "")
                topic = item.get("topic", "")
                content = item.get("content", "")
                confidence = item.get("confidence", 0.5)

                if category == "databases":
                    if topic not in db_knowledge:
                        db_knowledge[topic] = {
                            "content": content,
                            "confidence": confidence,
                            "capabilities": self._extract_capabilities(content),
                        }

            return db_knowledge

        except Exception as e:
            print(f"Error getting database knowledge: {e}")
            return {}

    def _extract_capabilities(self, content: str) -> List[str]:
        """Extrae capacidades de la descripción de una base de datos."""

        capabilities = []
        content_lower = content.lower()

        capability_keywords = {
            "document_store": ["document", "json", "flexible schema"],
            "full_text_search": ["search", "full-text", "text search"],
            "analytics": ["analytics", "aggregation", "olap"],
            "real_time": ["real-time", "streaming", "live"],
            "scalability": ["scalable", "distributed", "clustering"],
            "acid_compliance": ["acid", "transactions", "consistency"],
            "in_memory": ["in-memory", "cache", "fast"],
            "time_series": ["time-series", "metrics", "temporal"],
            "graph": ["graph", "relationships", "cypher"],
            "replication": ["replication", "backup", "redundancy"],
        }

        for capability, keywords in capability_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                capabilities.append(capability)

        return capabilities

    def _calculate_database_scores(
        self, characteristics: Dict[str, Any], db_knowledge: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calcula puntuaciones para cada tipo de base de datos."""

        scores = {}

        for db_type, info in db_knowledge.items():
            score = 0.0
            capabilities = info.get("capabilities", [])
            confidence = info.get("confidence", 0.5)

            # Puntuación base por confianza
            score += confidence * 0.3

            # Puntuación por estructura de datos
            structure = characteristics.get("structure", "unknown")
            if structure == "document" and "document_store" in capabilities:
                score += 0.4
            elif structure == "relational" and any(
                cap in capabilities for cap in ["acid_compliance"]
            ):
                score += 0.4
            elif structure == "key_value" and "in_memory" in capabilities:
                score += 0.4
            elif structure == "graph" and "graph" in capabilities:
                score += 0.4
            elif structure == "time_series" and "time_series" in capabilities:
                score += 0.4

            # Puntuación por requisitos específicos
            if (
                characteristics.get("search_requirements")
                and "full_text_search" in capabilities
            ):
                score += 0.3

            if (
                characteristics.get("analytics_requirements")
                and "analytics" in capabilities
            ):
                score += 0.3

            if (
                characteristics.get("real_time_requirements")
                and "real_time" in capabilities
            ):
                score += 0.2

            if (
                characteristics.get("consistency_requirements") == "strong"
                and "acid_compliance" in capabilities
            ):
                score += 0.2

            # Penalización por limitaciones
            size = characteristics.get("size_estimate", "medium")
            if size == "large" and "scalability" not in capabilities:
                score -= 0.2

            scores[db_type] = min(1.0, max(0.0, score))

        return scores

    def _generate_recommendation(
        self, scores: Dict[str, float], characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera recomendación basada en las puntuaciones."""

        if not scores:
            return {
                "primary": "sqlite",
                "alternatives": ["postgresql"],
                "confidence": 0.5,
            }

        # Ordenar por puntuación
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        primary = sorted_scores[0][0]
        primary_score = sorted_scores[0][1]

        alternatives = [db for db, score in sorted_scores[1:4] if score > 0.3]

        return {
            "primary": primary,
            "alternatives": alternatives,
            "confidence": primary_score,
            "all_scores": dict(sorted_scores),
        }

    def _explain_recommendation(
        self, recommendation: Dict[str, Any], characteristics: Dict[str, Any]
    ) -> str:
        """Explica el razonamiento detrás de la recomendación."""

        primary = recommendation.get("primary", "unknown")
        confidence = recommendation.get("confidence", 0.0)
        structure = characteristics.get("structure", "unknown")

        explanation = f"Recomendación: {primary} (confianza: {confidence:.2f})\n\n"

        explanation += f"Razones principales:\n"
        explanation += f"- Estructura de datos: {structure}\n"

        if characteristics.get("search_requirements"):
            explanation += "- Requiere búsqueda de texto completo\n"

        if characteristics.get("analytics_requirements"):
            explanation += "- Requiere capacidades analíticas\n"

        if characteristics.get("real_time_requirements"):
            explanation += "- Requiere procesamiento en tiempo real\n"

        consistency = characteristics.get("consistency_requirements", "eventual")
        explanation += f"- Requisitos de consistencia: {consistency}\n"

        size = characteristics.get("size_estimate", "medium")
        explanation += f"- Tamaño estimado de datos: {size}\n"

        alternatives = recommendation.get("alternatives", [])
        if alternatives:
            explanation += f"\nAlternativas viables: {', '.join(alternatives)}"

        return explanation

    def get_database_recommendations_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de las recomendaciones de bases de datos."""

        return {
            "supported_types": list(self.db_manager.get_database_types()),
            "data_type_recommendations": self.data_type_recommendations,
            "active_connections": list(self.db_manager.connectors.keys()),
            "knowledge_base_status": {
                "database_knowledge_count": len(self._get_database_knowledge()),
                "last_updated": "dynamic",
            },
        }

    def suggest_database_for_scraping_target(
        self, target_url: str, expected_data_structure: str
    ) -> Dict[str, Any]:
        """Sugiere la mejor base de datos para un objetivo de scraping específico."""

        # Analizar el tipo de sitio web
        domain_analysis = self._analyze_domain_type(target_url)

        # Combinar con estructura esperada
        data_description = f"Web scraping from {target_url}: {expected_data_structure}. {domain_analysis['description']}"

        recommendation = self.analyze_data_requirements(data_description)

        return {
            "url": target_url,
            "domain_analysis": domain_analysis,
            "database_recommendation": recommendation,
            "integration_notes": self._generate_integration_notes(
                recommendation, target_url
            ),
        }

    def _analyze_domain_type(self, url: str) -> Dict[str, Any]:
        """Analiza el tipo de dominio para mejores recomendaciones."""

        domain_types = {
            "ecommerce": ["shop", "store", "buy", "amazon", "ebay"],
            "news": ["news", "times", "post", "journal", "media"],
            "social": ["social", "facebook", "twitter", "linkedin"],
            "academic": ["edu", "scholar", "research", "university"],
            "government": ["gov", "government", "official"],
            "api": ["api", "rest", "graphql", "endpoint"],
        }

        url_lower = url.lower()
        detected_type = "general"

        for domain_type, keywords in domain_types.items():
            if any(keyword in url_lower for keyword in keywords):
                detected_type = domain_type
                break

        descriptions = {
            "ecommerce": "Product catalogs with structured data, prices, reviews",
            "news": "Text-heavy content with temporal data, articles, comments",
            "social": "User-generated content, relationships, real-time updates",
            "academic": "Research papers, citations, structured metadata",
            "government": "Official documents, reports, regulatory data",
            "api": "Structured JSON/XML responses, high volume",
            "general": "Mixed content types, flexible schema needed",
        }

        return {"type": detected_type, "description": descriptions[detected_type]}

    def _generate_integration_notes(
        self, recommendation: Dict[str, Any], url: str
    ) -> List[str]:
        """Genera notas de integración específicas."""

        notes = []
        primary_db = recommendation.get("recommendation", {}).get("primary", "")

        notes.append(f"Configurar {primary_db} para datos de {url}")

        if primary_db in ["mongodb", "couchdb"]:
            notes.append("Configurar índices para búsquedas frecuentes")
            notes.append("Implementar validación de esquema flexible")

        elif primary_db in ["postgresql", "mysql"]:
            notes.append("Diseñar esquema normalizado")
            notes.append("Configurar índices de texto completo si es necesario")

        elif primary_db == "elasticsearch":
            notes.append("Configurar mapeos de campos")
            notes.append("Implementar pipeline de ingesta")

        elif primary_db == "redis":
            notes.append("Configurar expiración de claves")
            notes.append("Implementar estrategia de persistencia")

        notes.append("Configurar backup automático")
        notes.append("Implementar monitoreo de rendimiento")

        return notes
