"""
Advanced Memory System - Sistema de Memoria Episódica y Semántica

Este módulo implementa sistemas de memoria inspirados en neurociencia cognitiva:
- Memoria Episódica: eventos específicos con contexto temporal y espacial
- Memoria Semántica: conocimiento factual y conceptual organizado
- Memoria de Trabajo: buffer temporal para procesamiento activo
- Consolidación: transferencia de memoria a corto a largo plazo
- Recuperación Contextual: activación de memorias por asociación
- Interferencia y Olvido: modelos realistas de pérdida de memoria
"""

import json
import logging
import math
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
import hashlib
import pickle

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"
    PROCEDURAL = "procedural"

class ConsolidationState(Enum):
    ACTIVE = "active"           # En memoria de trabajo
    CONSOLIDATING = "consolidating"  # En proceso de consolidación
    CONSOLIDATED = "consolidated"    # En memoria a largo plazo
    FORGOTTEN = "forgotten"     # Olvidado por decay o interferencia

@dataclass
class MemoryTrace:
    """Rastro de memoria individual con metadatos neurológicos"""
    content: Dict[str, Any]
    memory_type: MemoryType
    encoding_time: float
    last_access: float
    access_count: int = 0
    consolidation_state: ConsolidationState = ConsolidationState.ACTIVE
    
    # Propiedades neurológicas
    synaptic_strength: float = 0.5
    decay_rate: float = 0.95  # Rate de olvido por día
    interference_resistance: float = 0.5
    emotional_valence: float = 0.0  # -1 (negativo) a 1 (positivo)
    arousal_level: float = 0.5      # 0 (calm) a 1 (excited)
    
    # Contexto episódico
    spatial_context: Optional[str] = None
    temporal_context: Optional[str] = None
    associated_memories: List[str] = field(default_factory=list)
    
    # Metadatos de recuperación
    retrieval_cues: Set[str] = field(default_factory=set)
    confidence_score: float = 0.8
    
    def get_memory_id(self) -> str:
        """Genera ID único para la memoria"""
        content_str = str(sorted(self.content.items()))
        return hashlib.md5(f"{content_str}_{self.encoding_time}".encode()).hexdigest()[:12]
    
    def update_access(self):
        """Actualiza metadatos cuando se accede a la memoria"""
        self.last_access = time.time()
        self.access_count += 1
        
        # Fortalecimiento por uso (simulando LTP - Long Term Potentiation)
        self.synaptic_strength = min(1.0, self.synaptic_strength + 0.1)
        
        # Reducir decay rate con accesos frecuentes
        if self.access_count > 5:
            self.decay_rate = min(0.98, self.decay_rate + 0.01)
    
    def calculate_retrieval_strength(self, current_time: float = None) -> float:
        """Calcula fuerza de recuperación basada en ACT-R theory"""
        if current_time is None:
            current_time = time.time()
            
        # Decay temporal (Ley de Potencia del Olvido)
        time_since_encoding = current_time - self.encoding_time
        time_since_access = current_time - self.last_access
        
        base_decay = math.pow(time_since_access / 3600, -0.5)  # Power law decay
        
        # Frequency effect (más accesos = más fuerte)
        frequency_boost = math.log(self.access_count + 1)
        
        # Emotional enhancement (memorias emocionales son más fuertes)
        emotional_boost = abs(self.emotional_valence) * self.arousal_level
        
        # Consolidation bonus
        consolidation_bonus = {
            ConsolidationState.ACTIVE: 0.0,
            ConsolidationState.CONSOLIDATING: 0.2,
            ConsolidationState.CONSOLIDATED: 0.5,
            ConsolidationState.FORGOTTEN: -1.0
        }[self.consolidation_state]
        
        retrieval_strength = (
            base_decay * 
            (1 + frequency_boost * 0.1) * 
            (1 + emotional_boost * 0.3) *
            self.synaptic_strength +
            consolidation_bonus
        )
        
        return max(0.0, min(1.0, retrieval_strength))
    
    def should_be_forgotten(self, forgetting_threshold: float = 0.1) -> bool:
        """Determina si la memoria debe ser olvidada"""
        return self.calculate_retrieval_strength() < forgetting_threshold

@dataclass
class Episode:
    """Episodio específico en memoria episódica"""
    event_description: str
    participants: List[str]
    location: str
    timestamp: float
    duration: float
    outcome: str
    details: Dict[str, Any]
    
    # Propiedades episódicas específicas
    vividness: float = 0.8
    perspective: str = "first_person"  # first_person, third_person
    sensory_details: Dict[str, Any] = field(default_factory=dict)
    
    def to_memory_trace(self) -> MemoryTrace:
        """Convierte episodio a rastro de memoria"""
        return MemoryTrace(
            content={
                "type": "episode",
                "description": self.event_description,
                "participants": self.participants,
                "location": self.location,
                "outcome": self.outcome,
                "details": self.details,
                "vividness": self.vividness
            },
            memory_type=MemoryType.EPISODIC,
            encoding_time=self.timestamp,
            last_access=self.timestamp,
            spatial_context=self.location,
            temporal_context=datetime.fromtimestamp(self.timestamp).isoformat(),
            retrieval_cues=set([
                self.event_description.lower(),
                self.location.lower(),
                self.outcome.lower()
            ] + [p.lower() for p in self.participants])
        )

@dataclass
class Concept:
    """Concepto en memoria semántica"""
    name: str
    definition: str
    category: str
    properties: Dict[str, Any]
    relationships: Dict[str, List[str]]  # tipo_relación -> [conceptos_relacionados]
    
    # Propiedades semánticas
    abstractness: float = 0.5  # 0 (concreto) a 1 (abstracto)
    frequency: int = 1
    typicality: float = 0.5  # Qué tan típico es dentro de su categoría
    
    def to_memory_trace(self) -> MemoryTrace:
        """Convierte concepto a rastro de memoria"""
        return MemoryTrace(
            content={
                "type": "concept",
                "name": self.name,
                "definition": self.definition,
                "category": self.category,
                "properties": self.properties,
                "relationships": self.relationships,
                "abstractness": self.abstractness,
                "typicality": self.typicality
            },
            memory_type=MemoryType.SEMANTIC,
            encoding_time=time.time(),
            last_access=time.time(),
            retrieval_cues=set([
                self.name.lower(),
                self.category.lower(),
                self.definition.lower()
            ] + list(self.properties.keys()))
        )

class WorkingMemory:
    """Memoria de trabajo con capacidad limitada (7±2 elementos)"""
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.buffer: deque = deque(maxlen=capacity)
        self.rehearsal_items: Set[str] = set()
        self.attention_weights: Dict[str, float] = {}
        
    def add_item(self, item: Dict[str, Any], priority: float = 0.5):
        """Añade item a memoria de trabajo"""
        item_id = str(hash(str(sorted(item.items()))))
        
        # Si buffer está lleno, item con menor atención es desplazado
        if len(self.buffer) >= self.capacity:
            self._remove_least_attended()
        
        self.buffer.append({
            'id': item_id,
            'content': item,
            'entry_time': time.time(),
            'priority': priority
        })
        
        self.attention_weights[item_id] = priority
    
    def _remove_least_attended(self):
        """Remueve item con menor peso atencional"""
        if not self.buffer:
            return
            
        least_attended_idx = 0
        min_attention = float('inf')
        
        for i, item in enumerate(self.buffer):
            attention = self.attention_weights.get(item['id'], 0)
            if attention < min_attention:
                min_attention = attention
                least_attended_idx = i
        
        removed_item = self.buffer[least_attended_idx]
        del self.buffer[least_attended_idx]
        self.attention_weights.pop(removed_item['id'], None)
    
    def rehearse(self, item_id: str):
        """Ensaya un item para mantenerlo activo"""
        self.rehearsal_items.add(item_id)
        if item_id in self.attention_weights:
            self.attention_weights[item_id] = min(1.0, self.attention_weights[item_id] + 0.1)
    
    def get_active_items(self) -> List[Dict[str, Any]]:
        """Obtiene items actualmente en memoria de trabajo"""
        return [item['content'] for item in self.buffer]
    
    def decay_attention(self, decay_rate: float = 0.95):
        """Aplica decay atencional a items no ensayados"""
        for item_id in list(self.attention_weights.keys()):
            if item_id not in self.rehearsal_items:
                self.attention_weights[item_id] *= decay_rate
                
                # Remover items con muy poca atención
                if self.attention_weights[item_id] < 0.1:
                    self._remove_item_by_id(item_id)
        
        # Limpiar rehearsal set
        self.rehearsal_items.clear()
    
    def _remove_item_by_id(self, item_id: str):
        """Remueve item específico por ID"""
        for i, item in enumerate(self.buffer):
            if item['id'] == item_id:
                del self.buffer[i]
                break
        self.attention_weights.pop(item_id, None)

class ConsolidationEngine:
    """Motor de consolidación de memoria"""
    
    def __init__(self):
        self.consolidation_rules = {
            # Memorias con alta valencia emocional se consolidan más rápido
            "emotional_priority": lambda trace: abs(trace.emotional_valence) > 0.7,
            
            # Memorias accedidas frecuentemente se consolidan
            "frequency_priority": lambda trace: trace.access_count > 3,
            
            # Memorias recientes con alta arousal
            "recency_arousal": lambda trace: (
                time.time() - trace.encoding_time < 3600 and trace.arousal_level > 0.8
            ),
            
            # Memorias semánticas importantes
            "semantic_importance": lambda trace: (
                trace.memory_type == MemoryType.SEMANTIC and 
                trace.synaptic_strength > 0.8
            )
        }
        
        self.consolidation_queue: List[str] = []
        
    def should_consolidate(self, memory_trace: MemoryTrace) -> bool:
        """Determina si una memoria debe ser consolidada"""
        
        # No consolidar si ya está consolidada o olvidada
        if memory_trace.consolidation_state in [ConsolidationState.CONSOLIDATED, ConsolidationState.FORGOTTEN]:
            return False
        
        # Aplicar reglas de consolidación
        for rule_name, rule_func in self.consolidation_rules.items():
            if rule_func(memory_trace):
                return True
                
        # Consolidación temporal (memorias activas por mucho tiempo)
        time_in_system = time.time() - memory_trace.encoding_time
        if time_in_system > 24 * 3600:  # 24 horas
            return True
            
        return False
    
    def consolidate_memory(self, memory_trace: MemoryTrace) -> MemoryTrace:
        """Consolida una memoria (simulando transferencia hippocampo -> cortex)"""
        
        # Aumentar resistencia a interferencia
        memory_trace.interference_resistance = min(1.0, memory_trace.interference_resistance + 0.3)
        
        # Reducir decay rate (memorias consolidadas duran más)
        memory_trace.decay_rate = min(0.99, memory_trace.decay_rate + 0.05)
        
        # Aumentar fuerza sináptica
        memory_trace.synaptic_strength = min(1.0, memory_trace.synaptic_strength + 0.2)
        
        # Cambiar estado
        memory_trace.consolidation_state = ConsolidationState.CONSOLIDATED
        
        logger.debug(f"Memory consolidated: {memory_trace.get_memory_id()}")
        
        return memory_trace

class AdvancedMemorySystem:
    """Sistema de memoria avanzado con múltiples subsistemas"""
    
    def __init__(self, persist_path: str = "data/advanced_memory.json"):
        self.persist_path = persist_path
        
        # Subsistemas de memoria
        self.episodic_memory: Dict[str, MemoryTrace] = {}
        self.semantic_memory: Dict[str, MemoryTrace] = {}
        self.working_memory = WorkingMemory()
        self.procedural_memory: Dict[str, Dict[str, Any]] = {}
        
        # Motor de consolidación
        self.consolidation_engine = ConsolidationEngine()
        
        # Índices para búsqueda eficiente
        self.cue_index: Dict[str, Set[str]] = defaultdict(set)
        self.temporal_index: Dict[str, List[str]] = defaultdict(list)
        self.category_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Métricas del sistema
        self.total_memories_encoded = 0
        self.total_memories_forgotten = 0
        self.average_retrieval_strength = 0.0
        
        # Cargar estado persistido
        self._load_persistent_state()
        
        logger.info("🧠 Advanced Memory System initialized")
    
    def encode_episode(self, episode: Episode) -> str:
        """Codifica un episodio en memoria episódica"""
        memory_trace = episode.to_memory_trace()
        memory_id = memory_trace.get_memory_id()
        
        # Determinar valencia emocional basada en outcome
        if "success" in episode.outcome.lower() or "good" in episode.outcome.lower():
            memory_trace.emotional_valence = 0.7
        elif "failure" in episode.outcome.lower() or "error" in episode.outcome.lower():
            memory_trace.emotional_valence = -0.6
        
        # Añadir a memoria episódica
        self.episodic_memory[memory_id] = memory_trace
        
        # Actualizar índices
        self._update_indices(memory_trace, memory_id)
        
        # Añadir a memoria de trabajo temporalmente
        self.working_memory.add_item(memory_trace.content, priority=0.8)
        
        self.total_memories_encoded += 1
        
        logger.debug(f"Episode encoded: {episode.event_description}")
        
        return memory_id
    
    def encode_concept(self, concept: Concept) -> str:
        """Codifica un concepto en memoria semántica"""
        memory_trace = concept.to_memory_trace()
        memory_id = memory_trace.get_memory_id()
        
        # Conceptos abstractos tienden a tener mayor fuerza sináptica inicial
        if concept.abstractness > 0.7:
            memory_trace.synaptic_strength = 0.8
        
        # Conceptos frecuentes son más resistentes a olvido
        if concept.frequency > 10:
            memory_trace.decay_rate = 0.98
            memory_trace.interference_resistance = 0.8
        
        # Añadir a memoria semántica
        self.semantic_memory[memory_id] = memory_trace
        
        # Actualizar índices
        self._update_indices(memory_trace, memory_id)
        
        # Añadir a memoria de trabajo
        self.working_memory.add_item(memory_trace.content, priority=0.6)
        
        self.total_memories_encoded += 1
        
        logger.debug(f"Concept encoded: {concept.name}")
        
        return memory_id
    
    def retrieve_by_cue(self, cue: str, memory_type: MemoryType = None, limit: int = 10) -> List[Tuple[MemoryTrace, float]]:
        """Recupera memorias usando cue de recuperación"""
        
        cue_lower = cue.lower()
        candidate_ids = self.cue_index.get(cue_lower, set())
        
        retrieved_memories = []
        
        # Seleccionar memorias candidatas basadas en tipo
        if memory_type == MemoryType.EPISODIC:
            memory_store = self.episodic_memory
        elif memory_type == MemoryType.SEMANTIC:
            memory_store = self.semantic_memory
        else:
            memory_store = {**self.episodic_memory, **self.semantic_memory}
        
        for memory_id in candidate_ids:
            if memory_id in memory_store:
                memory_trace = memory_store[memory_id]
                
                # Calcular relevancia del cue
                cue_relevance = self._calculate_cue_relevance(cue_lower, memory_trace)
                
                # Calcular fuerza de recuperación
                retrieval_strength = memory_trace.calculate_retrieval_strength()
                
                # Score combinado
                combined_score = cue_relevance * retrieval_strength
                
                if combined_score > 0.1:  # Umbral mínimo
                    retrieved_memories.append((memory_trace, combined_score))
                    
                    # Actualizar acceso
                    memory_trace.update_access()
        
        # Ordenar por score y limitar resultados
        retrieved_memories.sort(key=lambda x: x[1], reverse=True)
        
        return retrieved_memories[:limit]
    
    def retrieve_by_context(self, spatial_context: str = None, temporal_context: str = None, limit: int = 10) -> List[Tuple[MemoryTrace, float]]:
        """Recupera memorias episódicas por contexto espacial/temporal"""
        
        retrieved_memories = []
        
        for memory_id, memory_trace in self.episodic_memory.items():
            context_match = 0.0
            
            # Match espacial
            if spatial_context and memory_trace.spatial_context:
                if spatial_context.lower() in memory_trace.spatial_context.lower():
                    context_match += 0.5
            
            # Match temporal (por rango de tiempo)
            if temporal_context and memory_trace.temporal_context:
                if temporal_context in memory_trace.temporal_context:
                    context_match += 0.5
            
            if context_match > 0:
                retrieval_strength = memory_trace.calculate_retrieval_strength()
                combined_score = context_match * retrieval_strength
                
                retrieved_memories.append((memory_trace, combined_score))
                memory_trace.update_access()
        
        retrieved_memories.sort(key=lambda x: x[1], reverse=True)
        return retrieved_memories[:limit]
    
    def associative_retrieval(self, seed_memory_id: str, association_strength: float = 0.3) -> List[Tuple[MemoryTrace, float]]:
        """Recuperación asociativa basada en memoria semilla"""
        
        # Obtener memoria semilla
        seed_memory = None
        if seed_memory_id in self.episodic_memory:
            seed_memory = self.episodic_memory[seed_memory_id]
        elif seed_memory_id in self.semantic_memory:
            seed_memory = self.semantic_memory[seed_memory_id]
        
        if not seed_memory:
            return []
        
        associated_memories = []
        
        # Buscar asociaciones en memorias relacionadas
        for related_id in seed_memory.associated_memories:
            if related_id in self.episodic_memory:
                related_memory = self.episodic_memory[related_id]
            elif related_id in self.semantic_memory:
                related_memory = self.semantic_memory[related_id]
            else:
                continue
            
            # Calcular fuerza de asociación
            association_score = self._calculate_association_strength(seed_memory, related_memory)
            
            if association_score >= association_strength:
                retrieval_strength = related_memory.calculate_retrieval_strength()
                combined_score = association_score * retrieval_strength
                
                associated_memories.append((related_memory, combined_score))
                related_memory.update_access()
        
        # Buscar asociaciones por overlap de cues
        for memory_store in [self.episodic_memory, self.semantic_memory]:
            for memory_id, memory_trace in memory_store.items():
                if memory_id == seed_memory_id:
                    continue
                
                # Calcular overlap de cues de recuperación
                cue_overlap = len(seed_memory.retrieval_cues & memory_trace.retrieval_cues)
                total_cues = len(seed_memory.retrieval_cues | memory_trace.retrieval_cues)
                
                if total_cues > 0:
                    overlap_score = cue_overlap / total_cues
                    
                    if overlap_score >= association_strength:
                        retrieval_strength = memory_trace.calculate_retrieval_strength()
                        combined_score = overlap_score * retrieval_strength
                        
                        associated_memories.append((memory_trace, combined_score))
                        memory_trace.update_access()
        
        associated_memories.sort(key=lambda x: x[1], reverse=True)
        return associated_memories[:10]
    
    def consolidation_cycle(self):
        """Ejecuta un ciclo de consolidación de memorias"""
        
        consolidated_count = 0
        forgotten_count = 0
        
        # Procesar memorias episódicas
        for memory_id, memory_trace in list(self.episodic_memory.items()):
            
            # Verificar si debe ser olvidada
            if memory_trace.should_be_forgotten():
                memory_trace.consolidation_state = ConsolidationState.FORGOTTEN
                del self.episodic_memory[memory_id]
                self._remove_from_indices(memory_trace, memory_id)
                forgotten_count += 1
                continue
            
            # Verificar si debe ser consolidada
            if self.consolidation_engine.should_consolidate(memory_trace):
                self.consolidation_engine.consolidate_memory(memory_trace)
                consolidated_count += 1
        
        # Procesar memorias semánticas
        for memory_id, memory_trace in list(self.semantic_memory.items()):
            
            if memory_trace.should_be_forgotten():
                memory_trace.consolidation_state = ConsolidationState.FORGOTTEN
                del self.semantic_memory[memory_id]
                self._remove_from_indices(memory_trace, memory_id)
                forgotten_count += 1
                continue
            
            if self.consolidation_engine.should_consolidate(memory_trace):
                self.consolidation_engine.consolidate_memory(memory_trace)
                consolidated_count += 1
        
        # Decay en memoria de trabajo
        self.working_memory.decay_attention()
        
        self.total_memories_forgotten += forgotten_count
        
        if consolidated_count > 0 or forgotten_count > 0:
            logger.debug(f"Consolidation cycle: {consolidated_count} consolidated, {forgotten_count} forgotten")
    
    def _update_indices(self, memory_trace: MemoryTrace, memory_id: str):
        """Actualiza índices de búsqueda"""
        
        # Índice de cues
        for cue in memory_trace.retrieval_cues:
            self.cue_index[cue].add(memory_id)
        
        # Índice temporal
        time_key = datetime.fromtimestamp(memory_trace.encoding_time).strftime("%Y-%m-%d")
        self.temporal_index[time_key].append(memory_id)
        
        # Índice por categoría
        if memory_trace.memory_type == MemoryType.SEMANTIC:
            category = memory_trace.content.get('category', 'unknown')
            self.category_index[category].add(memory_id)
    
    def _remove_from_indices(self, memory_trace: MemoryTrace, memory_id: str):
        """Remueve memoria de todos los índices"""
        
        # Remover de índice de cues
        for cue in memory_trace.retrieval_cues:
            self.cue_index[cue].discard(memory_id)
        
        # Remover de índice temporal
        time_key = datetime.fromtimestamp(memory_trace.encoding_time).strftime("%Y-%m-%d")
        if memory_id in self.temporal_index[time_key]:
            self.temporal_index[time_key].remove(memory_id)
        
        # Remover de índice de categoría
        if memory_trace.memory_type == MemoryType.SEMANTIC:
            category = memory_trace.content.get('category', 'unknown')
            self.category_index[category].discard(memory_id)
    
    def _calculate_cue_relevance(self, cue: str, memory_trace: MemoryTrace) -> float:
        """Calcula relevancia de cue para una memoria"""
        
        if cue in memory_trace.retrieval_cues:
            return 1.0
        
        # Buscar matches parciales
        partial_matches = sum(1 for existing_cue in memory_trace.retrieval_cues 
                            if cue in existing_cue or existing_cue in cue)
        
        if partial_matches > 0:
            return 0.7 * (partial_matches / len(memory_trace.retrieval_cues))
        
        return 0.0
    
    def _calculate_association_strength(self, memory1: MemoryTrace, memory2: MemoryTrace) -> float:
        """Calcula fuerza de asociación entre dos memorias"""
        
        # Temporal proximity (memorias codificadas cerca en tiempo)
        time_diff = abs(memory1.encoding_time - memory2.encoding_time)
        temporal_similarity = math.exp(-time_diff / (24 * 3600))  # Decay in 24 hours
        
        # Semantic similarity (overlap de cues)
        cue_overlap = len(memory1.retrieval_cues & memory2.retrieval_cues)
        total_cues = len(memory1.retrieval_cues | memory2.retrieval_cues)
        semantic_similarity = cue_overlap / total_cues if total_cues > 0 else 0
        
        # Emotional similarity
        emotional_similarity = 1 - abs(memory1.emotional_valence - memory2.emotional_valence) / 2
        
        # Weighted combination
        association_strength = (
            temporal_similarity * 0.3 +
            semantic_similarity * 0.5 +
            emotional_similarity * 0.2
        )
        
        return association_strength
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de memoria"""
        
        total_episodic = len(self.episodic_memory)
        total_semantic = len(self.semantic_memory)
        total_working = len(self.working_memory.buffer)
        
        # Calcular fuerza promedio de recuperación
        all_memories = list(self.episodic_memory.values()) + list(self.semantic_memory.values())
        if all_memories:
            avg_retrieval_strength = statistics.mean([m.calculate_retrieval_strength() for m in all_memories])
        else:
            avg_retrieval_strength = 0.0
        
        # Estado de consolidación
        consolidation_stats = {
            ConsolidationState.ACTIVE: 0,
            ConsolidationState.CONSOLIDATING: 0,
            ConsolidationState.CONSOLIDATED: 0,
            ConsolidationState.FORGOTTEN: 0
        }
        
        for memory in all_memories:
            consolidation_stats[memory.consolidation_state] += 1
        
        return {
            'total_memories': total_episodic + total_semantic,
            'episodic_memories': total_episodic,
            'semantic_memories': total_semantic,
            'working_memory_items': total_working,
            'total_encoded': self.total_memories_encoded,
            'total_forgotten': self.total_memories_forgotten,
            'average_retrieval_strength': avg_retrieval_strength,
            'consolidation_state': dict(consolidation_stats),
            'cue_index_size': len(self.cue_index),
            'memory_efficiency': 1 - (self.total_memories_forgotten / max(1, self.total_memories_encoded))
        }
    
    def _load_persistent_state(self):
        """Carga estado persistido del sistema de memoria"""
        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Reconstruir memorias (simplificado)
            self.total_memories_encoded = data.get('total_encoded', 0)
            self.total_memories_forgotten = data.get('total_forgotten', 0)
            
            logger.info(f"Memory state loaded from {self.persist_path}")
            
        except FileNotFoundError:
            logger.info("No persistent memory state found, starting fresh")
        except Exception as e:
            logger.warning(f"Failed to load memory state: {e}")
    
    def save_persistent_state(self):
        """Guarda estado del sistema de memoria"""
        try:
            stats = self.get_memory_statistics()
            
            data = {
                'timestamp': time.time(),
                'total_encoded': self.total_memories_encoded,
                'total_forgotten': self.total_memories_forgotten,
                'statistics': stats
            }
            
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"Memory state saved to {self.persist_path}")
            
        except Exception as e:
            logger.error(f"Failed to save memory state: {e}")

# Función de fábrica
def create_advanced_memory_system() -> AdvancedMemorySystem:
    """Crea y configura un sistema de memoria avanzado"""
    return AdvancedMemorySystem()