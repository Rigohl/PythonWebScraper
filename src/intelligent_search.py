"""
Sistema de Búsqueda Inteligente y Generación de Contenido
Permite buscar información sobre temas específicos y generar documentos
"""

import logging
import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
import hashlib

# Importaciones para scraping
try:
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
    import httpx
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

logger = logging.getLogger(__name__)

class IntelligentSearchEngine:
    """Motor de búsqueda inteligente que recopila información de múltiples fuentes"""

    def __init__(self, brain_instance=None):
        self.brain = brain_instance
        self.search_history: List[Dict[str, Any]] = []
        self.content_cache: Dict[str, Dict[str, Any]] = {}

        # Configuración de fuentes de búsqueda
        self.search_sources = {
            'wikipedia': {
                'base_url': 'https://es.wikipedia.org/wiki/',
                'search_url': 'https://es.wikipedia.org/w/api.php',
                'enabled': True,
                'priority': 1
            },
            'google_search': {
                'enabled': False,  # Requiere API key
                'priority': 2
            },
            'general_web': {
                'enabled': True,
                'priority': 3,
                'sites': [
                    'https://stackoverflow.com',
                    'https://github.com',
                    'https://docs.python.org',
                    'https://developer.mozilla.org'
                ]
            }
        }

        # Patrones de contenido
        self.content_patterns = {
            'definition': r'(es|son|significa|define|concepto|definición)',
            'tutorial': r'(cómo|tutorial|guía|paso a paso|instrucciones)',
            'examples': r'(ejemplo|ejemplos|muestra|sample|demo)',
            'code': r'(código|code|script|programa|algoritmo)',
            'comparison': r'(vs|versus|comparación|diferencia|mejor|peor)'
        }

        logger.info("🔍 Motor de búsqueda inteligente inicializado")

    async def intelligent_search(self, topic: str, max_results: int = 10,
                                content_types: List[str] = None) -> Dict[str, Any]:
        """Realiza búsqueda inteligente sobre un tema"""

        search_id = hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]

        search_session = {
            'search_id': search_id,
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'content_types': content_types or ['definition', 'examples', 'tutorial'],
            'max_results': max_results,
            'status': 'starting'
        }

        logger.info(f"🔍 Iniciando búsqueda inteligente para: {topic}")

        try:
            # Analizar tema con el cerebro si está disponible
            if self.brain:
                brain_analysis = await self._analyze_topic_with_brain(topic)
                search_session['brain_analysis'] = brain_analysis

                # Expandir términos de búsqueda basado en análisis
                search_terms = brain_analysis.get('expanded_terms', [topic])
            else:
                search_terms = [topic]

            search_session['search_terms'] = search_terms
            search_session['status'] = 'searching'

            # Realizar búsquedas en paralelo
            search_results = await self._parallel_search(search_terms, max_results)
            search_session['raw_results'] = search_results

            # Filtrar y organizar contenido
            organized_content = await self._organize_content(search_results, content_types)
            search_session['organized_content'] = organized_content

            # Generar síntesis inteligente
            synthesis = await self._synthesize_content(organized_content, topic)
            search_session['synthesis'] = synthesis

            search_session['status'] = 'completed'
            search_session['total_sources'] = len(search_results)
            search_session['completion_time'] = datetime.now().isoformat()

            # Guardar en historial
            self.search_history.append(search_session)

            logger.info(f"🔍 Búsqueda completada: {len(search_results)} fuentes, síntesis generada")

            return search_session

        except Exception as e:
            logger.error(f"Error en búsqueda inteligente: {e}")
            search_session['status'] = 'error'
            search_session['error'] = str(e)
            return search_session

    async def _analyze_topic_with_brain(self, topic: str) -> Dict[str, Any]:
        """Analiza el tema usando el cerebro híbrido"""
        try:
            analysis = self.brain.process_intelligent_query({
                'type': 'topic_analysis',
                'topic': topic,
                'purpose': 'search_expansion',
                'context': 'intelligent_search'
            })

            # Extraer términos relacionados
            expanded_terms = [topic]

            # Generar términos relacionados simples
            if 'bot' in topic.lower():
                expanded_terms.extend(['robot', 'automatización', 'inteligencia artificial'])
            elif 'python' in topic.lower():
                expanded_terms.extend(['programación', 'código', 'desarrollo'])
            elif 'scraping' in topic.lower():
                expanded_terms.extend(['web scraping', 'extracción de datos', 'crawling'])

            return {
                'original_topic': topic,
                'expanded_terms': expanded_terms,
                'analysis': analysis,
                'confidence': analysis.get('confidence', 0.7)
            }

        except Exception as e:
            logger.error(f"Error analizando tema con cerebro: {e}")
            return {
                'original_topic': topic,
                'expanded_terms': [topic],
                'error': str(e)
            }

    async def _parallel_search(self, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Realiza búsquedas en paralelo en múltiples fuentes"""

        search_tasks = []

        # Wikipedia search
        if self.search_sources['wikipedia']['enabled']:
            for term in search_terms[:3]:  # Limitar términos para Wikipedia
                search_tasks.append(self._search_wikipedia(term))

        # Web search
        if self.search_sources['general_web']['enabled']:
            for term in search_terms[:2]:  # Limitar para web general
                search_tasks.append(self._search_general_web(term, max_results))

        # Ejecutar búsquedas en paralelo
        results = []
        if search_tasks:
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

            for result in search_results:
                if isinstance(result, Exception):
                    logger.error(f"Error en búsqueda paralela: {result}")
                    continue

                if isinstance(result, list):
                    results.extend(result)
                elif isinstance(result, dict):
                    results.append(result)

        return results[:max_results]

    async def _search_wikipedia(self, term: str) -> List[Dict[str, Any]]:
        """Busca en Wikipedia"""
        try:
            # Usar API de Wikipedia para búsqueda
            search_url = self.search_sources['wikipedia']['search_url']

            async with aiohttp.ClientSession() as session:
                # Búsqueda
                search_params = {
                    'action': 'query',
                    'list': 'search',
                    'srsearch': term,
                    'format': 'json',
                    'srlimit': 3
                }

                async with session.get(search_url, params=search_params) as response:
                    search_data = await response.json()

                results = []

                if 'query' in search_data and 'search' in search_data['query']:
                    for item in search_data['query']['search']:
                        page_title = item['title']

                        # Obtener contenido de la página
                        content_params = {
                            'action': 'query',
                            'titles': page_title,
                            'prop': 'extracts',
                            'exintro': 'true',
                            'explaintext': 'true',
                            'format': 'json'
                        }

                        async with session.get(search_url, params=content_params) as content_response:
                            content_data = await content_response.json()

                        pages = content_data.get('query', {}).get('pages', {})
                        for page_id, page_data in pages.items():
                            if 'extract' in page_data:
                                results.append({
                                    'source': 'wikipedia',
                                    'title': page_title,
                                    'url': f"https://es.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                                    'content': page_data['extract'],
                                    'snippet': item.get('snippet', ''),
                                    'confidence': 0.9,
                                    'timestamp': datetime.now().isoformat(),
                                    'search_term': term
                                })

                return results

        except Exception as e:
            logger.error(f"Error buscando en Wikipedia: {e}")
            return []

    async def _search_general_web(self, term: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Búsqueda general en web (simulada por ahora)"""
        try:
            # Por ahora, generar contenido de ejemplo
            # TODO: Implementar búsqueda real con APIs o scraping

            results = []

            # Simular algunos resultados útiles
            example_results = [
                {
                    'source': 'general_web',
                    'title': f'Guía completa sobre {term}',
                    'url': f'https://example.com/{term.lower().replace(" ", "-")}',
                    'content': f'Una guía completa sobre {term} que cubre los aspectos fundamentales, '
                              f'ejemplos prácticos y mejores prácticas para trabajar con {term}.',
                    'snippet': f'Todo lo que necesitas saber sobre {term}...',
                    'confidence': 0.7,
                    'timestamp': datetime.now().isoformat(),
                    'search_term': term
                },
                {
                    'source': 'general_web',
                    'title': f'Tutorial de {term} paso a paso',
                    'url': f'https://tutorial.com/{term.lower().replace(" ", "-")}-tutorial',
                    'content': f'Tutorial paso a paso para aprender {term} desde cero. '
                              f'Incluye ejemplos prácticos, ejercicios y proyectos.',
                    'snippet': f'Aprende {term} desde cero con este tutorial...',
                    'confidence': 0.8,
                    'timestamp': datetime.now().isoformat(),
                    'search_term': term
                }
            ]

            return example_results[:max_results]

        except Exception as e:
            logger.error(f"Error en búsqueda general web: {e}")
            return []

    async def _organize_content(self, search_results: List[Dict[str, Any]],
                              content_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Organiza el contenido por tipos"""

        organized = {content_type: [] for content_type in content_types}
        organized['other'] = []

        for result in search_results:
            content = result.get('content', '').lower()
            title = result.get('title', '').lower()

            categorized = False

            for content_type in content_types:
                if content_type in self.content_patterns:
                    pattern = self.content_patterns[content_type]

                    if re.search(pattern, content) or re.search(pattern, title):
                        organized[content_type].append(result)
                        categorized = True
                        break

            if not categorized:
                organized['other'].append(result)

        return organized

    async def _synthesize_content(self, organized_content: Dict[str, List[Dict[str, Any]]],
                                topic: str) -> Dict[str, Any]:
        """Sintetiza el contenido recopilado"""

        synthesis = {
            'topic': topic,
            'summary': '',
            'key_points': [],
            'sources_count': 0,
            'content_quality': 0.0,
            'recommended_actions': []
        }

        total_sources = sum(len(content_list) for content_list in organized_content.values())
        synthesis['sources_count'] = total_sources

        if total_sources == 0:
            synthesis['summary'] = f"No se encontró información suficiente sobre {topic}."
            synthesis['content_quality'] = 0.0
            return synthesis

        # Generar resumen basado en contenido encontrado
        key_points = []

        for content_type, results in organized_content.items():
            if results and content_type != 'other':
                key_points.append(f"Se encontraron {len(results)} fuentes sobre {content_type} de {topic}")

        if organized_content.get('definition'):
            definition_result = organized_content['definition'][0]
            definition_snippet = definition_result.get('content', '')[:200] + "..."
            key_points.append(f"Definición: {definition_snippet}")

        synthesis['key_points'] = key_points

        # Generar resumen
        synthesis['summary'] = f"""
Búsqueda completada para '{topic}' con {total_sources} fuentes encontradas.

{chr(10).join(key_points)}

La información recopilada incluye definiciones, ejemplos y guías prácticas.
        """.strip()

        # Calcular calidad del contenido
        quality_score = min(total_sources / 5.0, 1.0)  # Máximo 1.0 con 5+ fuentes
        synthesis['content_quality'] = quality_score

        # Recomendar acciones
        if quality_score > 0.7:
            synthesis['recommended_actions'] = [
                'create_comprehensive_document',
                'generate_tutorial',
                'create_summary_presentation'
            ]
        elif quality_score > 0.4:
            synthesis['recommended_actions'] = [
                'create_basic_document',
                'compile_key_points'
            ]
        else:
            synthesis['recommended_actions'] = [
                'expand_search_terms',
                'try_alternative_sources'
            ]

        return synthesis

    def get_search_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de búsquedas"""
        return self.search_history

    def get_cached_content(self, topic: str) -> Optional[Dict[str, Any]]:
        """Obtiene contenido cacheado para un tema"""
        return self.content_cache.get(topic)

    def cache_content(self, topic: str, content: Dict[str, Any]):
        """Cachea contenido para un tema"""
        self.content_cache[topic] = {
            'content': content,
            'cached_at': datetime.now().isoformat(),
            'access_count': 0
        }

    async def quick_search(self, topic: str) -> str:
        """Búsqueda rápida que retorna solo un resumen"""
        search_result = await self.intelligent_search(topic, max_results=3, content_types=['definition'])

        if search_result['status'] == 'completed':
            return search_result['synthesis']['summary']
        else:
            return f"No se pudo obtener información sobre {topic}"

class SearchResultsExporter:
    """Exportador de resultados de búsqueda a diferentes formatos"""

    def __init__(self):
        self.export_formats = ['txt', 'md', 'json', 'html']

    def export_search_results(self, search_session: Dict[str, Any],
                            format_type: str = 'md',
                            output_path: str = None) -> str:
        """Exporta resultados de búsqueda al formato especificado"""

        if format_type not in self.export_formats:
            raise ValueError(f"Formato no soportado: {format_type}")

        topic = search_session.get('topic', 'unknown')
        search_id = search_session.get('search_id', 'unknown')

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"exports/search_{topic.replace(' ', '_')}_{timestamp}.{format_type}"

        # Crear directorio si no existe
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if format_type == 'md':
            content = self._generate_markdown_report(search_session)
        elif format_type == 'json':
            content = json.dumps(search_session, indent=2, ensure_ascii=False)
        elif format_type == 'txt':
            content = self._generate_text_report(search_session)
        elif format_type == 'html':
            content = self._generate_html_report(search_session)

        # Escribir archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"📄 Resultados exportados a: {output_path}")
        return output_path

    def _generate_markdown_report(self, search_session: Dict[str, Any]) -> str:
        """Genera reporte en formato Markdown"""

        topic = search_session.get('topic', 'Unknown')
        timestamp = search_session.get('timestamp', 'Unknown')
        synthesis = search_session.get('synthesis', {})
        organized_content = search_session.get('organized_content', {})

        md_content = f"""# Informe de Búsqueda Inteligente: {topic}

**Fecha:** {timestamp}
**ID de Búsqueda:** {search_session.get('search_id', 'N/A')}
**Estado:** {search_session.get('status', 'N/A')}

## 📊 Resumen Ejecutivo

{synthesis.get('summary', 'No hay resumen disponible')}

**Fuentes consultadas:** {synthesis.get('sources_count', 0)}
**Calidad del contenido:** {synthesis.get('content_quality', 0):.1%}

## 🔍 Puntos Clave

"""

        for point in synthesis.get('key_points', []):
            md_content += f"- {point}\n"

        md_content += "\n## 📚 Contenido Organizado\n\n"

        for content_type, results in organized_content.items():
            if results:
                md_content += f"### {content_type.title()}\n\n"

                for i, result in enumerate(results, 1):
                    md_content += f"**{i}. {result.get('title', 'Sin título')}**\n\n"
                    md_content += f"- **Fuente:** {result.get('source', 'N/A')}\n"
                    md_content += f"- **URL:** {result.get('url', 'N/A')}\n"
                    md_content += f"- **Confianza:** {result.get('confidence', 0):.1%}\n\n"

                    content_preview = result.get('content', '')[:300]
                    if len(content_preview) < len(result.get('content', '')):
                        content_preview += "..."

                    md_content += f"{content_preview}\n\n"
                    md_content += "---\n\n"

        # Acciones recomendadas
        recommended_actions = synthesis.get('recommended_actions', [])
        if recommended_actions:
            md_content += "## 🎯 Acciones Recomendadas\n\n"
            for action in recommended_actions:
                md_content += f"- {action.replace('_', ' ').title()}\n"

        md_content += f"\n---\n*Generado por Web Scraper PRO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return md_content

    def _generate_text_report(self, search_session: Dict[str, Any]) -> str:
        """Genera reporte en formato texto plano"""

        topic = search_session.get('topic', 'Unknown')
        synthesis = search_session.get('synthesis', {})

        content = f"""
INFORME DE BÚSQUEDA INTELIGENTE
{'='*60}

Tema: {topic}
Fecha: {search_session.get('timestamp', 'Unknown')}
ID: {search_session.get('search_id', 'N/A')}

RESUMEN
{'-'*30}
{synthesis.get('summary', 'No hay resumen disponible')}

Fuentes: {synthesis.get('sources_count', 0)}
Calidad: {synthesis.get('content_quality', 0):.1%}

PUNTOS CLAVE
{'-'*30}
"""

        for point in synthesis.get('key_points', []):
            content += f"• {point}\n"

        content += f"\nGenerado por Web Scraper PRO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return content

    def _generate_html_report(self, search_session: Dict[str, Any]) -> str:
        """Genera reporte en formato HTML"""

        topic = search_session.get('topic', 'Unknown')
        synthesis = search_session.get('synthesis', {})

        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Búsqueda: {topic}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .key-points {{ margin: 20px 0; }}
        .footer {{ margin-top: 40px; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Informe de Búsqueda Inteligente</h1>
        <h2>{topic}</h2>
        <p><strong>Fecha:</strong> {search_session.get('timestamp', 'Unknown')}</p>
        <p><strong>ID:</strong> {search_session.get('search_id', 'N/A')}</p>
    </div>

    <div class="summary">
        <h3>📊 Resumen Ejecutivo</h3>
        <p>{synthesis.get('summary', 'No hay resumen disponible')}</p>
        <p><strong>Fuentes:</strong> {synthesis.get('sources_count', 0)} |
           <strong>Calidad:</strong> {synthesis.get('content_quality', 0):.1%}</p>
    </div>

    <div class="key-points">
        <h3>🔍 Puntos Clave</h3>
        <ul>
"""

        for point in synthesis.get('key_points', []):
            html_content += f"<li>{point}</li>"

        html_content += f"""
        </ul>
    </div>

    <div class="footer">
        <p>Generado por Web Scraper PRO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""

        return html_content

# Funciones de utilidad
def create_search_engine(brain_instance=None) -> IntelligentSearchEngine:
    """Crea una instancia del motor de búsqueda"""
    return IntelligentSearchEngine(brain_instance)

async def quick_search(topic: str, brain_instance=None) -> str:
    """Búsqueda rápida que retorna un resumen"""
    engine = create_search_engine(brain_instance)
    return await engine.quick_search(topic)

# Función principal para demostración
async def main():
    """Función principal para demostración"""
    print("🔍 Iniciando Motor de Búsqueda Inteligente...")

    engine = create_search_engine()
    exporter = SearchResultsExporter()

    # Búsqueda de ejemplo
    topic = input("¿Sobre qué tema quieres buscar información? ")

    if topic.strip():
        print(f"\n🔍 Buscando información sobre: {topic}")

        search_result = await engine.intelligent_search(
            topic,
            max_results=5,
            content_types=['definition', 'examples', 'tutorial']
        )

        if search_result['status'] == 'completed':
            print("\n✅ Búsqueda completada!")
            print(f"📊 Resumen: {search_result['synthesis']['summary']}")

            # Exportar resultados
            export_path = exporter.export_search_results(search_result, 'md')
            print(f"📄 Informe guardado en: {export_path}")
        else:
            print(f"❌ Error en la búsqueda: {search_result.get('error', 'Error desconocido')}")

if __name__ == "__main__":
    asyncio.run(main())
