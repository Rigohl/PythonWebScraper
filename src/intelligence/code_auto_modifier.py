"""
Code Auto-Modification System - Sistema para que la IA se auto-edite y mejore
Capacidades de creación, modificación y refactoring automático de código.
"""

import ast
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import inspect
import textwrap
import re
import json

@dataclass
class CodeChange:
    file_path: str
    change_type: str  # 'create', 'modify', 'refactor', 'optimize'
    description: str
    old_content: Optional[str] = None
    new_content: str = ""
    line_range: Optional[Tuple[int, int]] = None
    confidence: float = 0.8

@dataclass
class CodeAnalysisResult:
    file_path: str
    issues: List[str]
    suggestions: List[str]
    complexity_score: float
    quality_score: float
    dependencies: List[str]

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calcula la complejidad ciclomática del código."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With, ast.AsyncWith):
                complexity += 1

        return complexity

    def calculate_complexity(self, code: str) -> float:
        """Método público para calcular complejidad."""
        try:
            tree = ast.parse(code)
            return self._calculate_complexity(tree)
        except:
            return 0.0

class CodeAutoModifier:
    """Sistema principal para auto-modificación de código."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backups" / "auto_modifications"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Templates para diferentes tipos de código
        self.templates = self._load_templates()

        # Patrones de mejora automática
        self.improvement_patterns = self._load_improvement_patterns()

    def analyze_code_quality(self, file_path: str) -> CodeAnalysisResult:
        """Analiza la calidad del código y sugiere mejoras."""
        path = Path(file_path)

        if not path.exists() or not path.suffix == '.py':
            return CodeAnalysisResult(file_path, [], [], 0, 0, [])

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Análisis de complejidad
            complexity = self._calculate_complexity(tree)

            # Detectar issues
            issues = self._detect_code_issues(content, tree)

            # Generar sugerencias
            suggestions = self._generate_suggestions(content, tree, issues)

            # Calcular score de calidad
            quality = self._calculate_quality_score(content, tree, issues)

            # Extraer dependencias
            dependencies = self._extract_dependencies(tree)

            return CodeAnalysisResult(
                file_path=file_path,
                issues=issues,
                suggestions=suggestions,
                complexity_score=complexity,
                quality_score=quality,
                dependencies=dependencies
            )

        except Exception as e:
            return CodeAnalysisResult(
                file_path=file_path,
                issues=[f"Error analyzing file: {e}"],
                suggestions=[],
                complexity_score=0,
                quality_score=0,
                dependencies=[]
            )

    def auto_improve_file(self, file_path: str, apply_changes: bool = False) -> List[CodeChange]:
        """Mejora automáticamente un archivo de código."""
        analysis = self.analyze_code_quality(file_path)
        changes = []

        if analysis.quality_score < 0.7:
            # Aplicar mejoras automáticas
            changes.extend(self._apply_automatic_improvements(file_path, analysis))

        if apply_changes:
            for change in changes:
                if change.confidence > 0.8:
                    self._apply_code_change(change)

        return changes

    def create_scraper_module(self, domain: str, selectors: Dict[str, str],
                            config: Dict[str, Any] = None) -> str:
        """Crea automáticamente un módulo completo de scraper."""

        # Preparar datos
        class_name = self._domain_to_class_name(domain)
        module_name = domain.replace('.', '_').replace('-', '_')

        config = config or {
            'rate_limit': 1.0,
            'timeout': 30,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (compatible; ScraperBot/1.0)'
            }
        }

        # Crear estructura de directorios
        module_dir = self.project_root / 'src' / 'scrapers' / module_name
        module_dir.mkdir(parents=True, exist_ok=True)

        # Generar archivos
        files_created = []

        # 1. Scraper principal
        scraper_code = self._generate_scraper_class(domain, class_name, selectors, config)
        scraper_file = module_dir / 'scraper.py'
        scraper_file.write_text(scraper_code)
        files_created.append(str(scraper_file))

        # 2. Parser específico
        parser_code = self._generate_parser_class(class_name, selectors)
        parser_file = module_dir / 'parser.py'
        parser_file.write_text(parser_code)
        files_created.append(str(parser_file))

        # 3. Configuración
        config_file = module_dir / 'config.json'
        config_file.write_text(json.dumps(config, indent=2))
        files_created.append(str(config_file))

        # 4. Tests
        test_code = self._generate_test_class(class_name, module_name)
        test_file = self.project_root / 'tests' / f'test_{module_name}.py'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_code)
        files_created.append(str(test_file))

        # 5. __init__.py
        init_file = module_dir / '__init__.py'
        init_file.write_text(f'from .scraper import {class_name}Scraper\n')
        files_created.append(str(init_file))

        return f"Created scraper module for {domain} with {len(files_created)} files"

    def refactor_for_performance(self, file_path: str) -> List[CodeChange]:
        """Refactoriza código para mejorar performance."""
        changes = []

        with open(file_path, 'r') as f:
            content = f.read()

        tree = ast.parse(content)

        # Detectar patrones de optimización
        optimizations = self._detect_performance_optimizations(content, tree)

        for optimization in optimizations:
            change = CodeChange(
                file_path=file_path,
                change_type='optimize',
                description=optimization['description'],
                old_content=optimization['old_code'],
                new_content=optimization['new_code'],
                confidence=optimization['confidence']
            )
            changes.append(change)

        return changes

    def _generate_scraper_class(self, domain: str, class_name: str,
                              selectors: Dict[str, str], config: Dict[str, Any]) -> str:
        """Genera una clase scraper completa."""
        template = '''"""
{domain} Scraper
Auto-generated by CodeAutoModifier
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin, urlparse

from .parser import {class_name}Parser

logger = logging.getLogger(__name__)

class {class_name}Scraper:
    """Scraper automático para {domain}"""

    def __init__(self, config: Dict[str, Any] = None):
        self.domain = "{domain}"
        self.base_url = "https://{domain}"
        self.config = config or {config}
        self.parser = {class_name}Parser()

        # Rate limiting
        self.rate_limit = self.config.get('rate_limit', 1.0)
        self.last_request_time = 0

        # Session configuration
        self.timeout = aiohttp.ClientTimeout(total=self.config.get('timeout', 30))
        self.headers = self.config.get('headers', {{}})

    async def scrape_url(self, url: str, session: aiohttp.ClientSession = None) -> Dict[str, Any]:
        """Scrape a single URL."""
        should_close_session = session is None

        if session is None:
            session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers
            )

        try:
            # Rate limiting
            await self._apply_rate_limit()

            async with session.get(url) as response:
                if response.status != 200:
                    return {{'error': f'HTTP {{response.status}}', 'url': url}}

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Parse data
                data = self.parser.parse(soup)
                data['url'] = url
                data['scraped_at'] = time.time()

                logger.info(f"Successfully scraped {{url}}")
                return data

        except Exception as e:
            logger.error(f"Error scraping {{url}}: {{e}}")
            return {{'error': str(e), 'url': url}}

        finally:
            if should_close_session:
                await session.close()

    async def scrape_multiple(self, urls: List[str], max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_semaphore(session, url):
            async with semaphore:
                return await self.scrape_url(url, session)

        async with aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers
        ) as session:
            tasks = [scrape_with_semaphore(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and convert to results
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append({{'error': str(result)}})
                else:
                    processed_results.append(result)

            return processed_results

    async def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()

    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics."""
        return {{
            'domain': self.domain,
            'rate_limit': self.rate_limit,
            'timeout': self.config.get('timeout', 30),
            'headers_count': len(self.headers)
        }}
'''

        return template.format(
            domain=domain,
            class_name=class_name,
            config=repr(config)
        )

    def _generate_parser_class(self, class_name: str, selectors: Dict[str, str]) -> str:
        """Genera una clase parser específica."""
        template = '''"""
Parser for {class_name}
Auto-generated by CodeAutoModifier
"""

from typing import Dict, Any, Optional
from bs4 import BeautifulSoup, Tag
import re
import logging

logger = logging.getLogger(__name__)

class {class_name}Parser:
    """Parser específico para extraer datos estructurados."""

    def __init__(self):
        self.selectors = {selectors}
        self.fallback_selectors = {{
            # Selectores de respaldo automáticos
        }}

    def parse(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse HTML y extrae datos estructurados."""
        data = {{}}

        for field, selector in self.selectors.items():
            try:
                value = self._extract_field(soup, field, selector)
                if value:
                    data[field] = value
            except Exception as e:
                logger.warning(f"Error extracting {{field}}: {{e}}")
                # Intentar selector de respaldo
                if field in self.fallback_selectors:
                    try:
                        value = self._extract_field(soup, field, self.fallback_selectors[field])
                        if value:
                            data[field] = value
                    except:
                        pass

        # Post-processing
        data = self._post_process_data(data)

        return data

    def _extract_field(self, soup: BeautifulSoup, field: str, selector: str) -> Optional[str]:
        """Extrae un campo específico usando el selector."""
        element = soup.select_one(selector)

        if not element:
            return None

        # Estrategias de extracción específicas por tipo de campo
        if field in ['price', 'cost', 'amount']:
            return self._extract_price(element)
        elif field in ['title', 'name', 'heading']:
            return self._extract_text(element)
        elif field in ['description', 'content', 'text']:
            return self._extract_rich_text(element)
        elif field in ['url', 'link', 'href']:
            return self._extract_url(element)
        elif field in ['image', 'img', 'photo']:
            return self._extract_image_url(element)
        else:
            return self._extract_text(element)

    def _extract_text(self, element: Tag) -> str:
        """Extrae texto limpio de un elemento."""
        if not element:
            return ""

        text = element.get_text(strip=True)
        # Limpiar texto
        text = re.sub(r'\\s+', ' ', text)
        text = text.strip()

        return text

    def _extract_rich_text(self, element: Tag) -> str:
        """Extrae texto preservando algunos elementos de formato."""
        if not element:
            return ""

        # Preservar saltos de línea
        for br in element.find_all("br"):
            br.replace_with("\\n")

        text = element.get_text()
        # Normalizar espacios pero preservar saltos de línea
        lines = [line.strip() for line in text.split('\\n')]
        return '\\n'.join(line for line in lines if line)

    def _extract_price(self, element: Tag) -> Optional[float]:
        """Extrae precio como número."""
        text = self._extract_text(element)

        # Buscar patrones de precio
        price_pattern = r'[\\d,]+\\.?\\d*'
        matches = re.findall(price_pattern, text)

        if matches:
            try:
                # Tomar el primer número encontrado
                price_str = matches[0].replace(',', '')
                return float(price_str)
            except ValueError:
                pass

        return None

    def _extract_url(self, element: Tag) -> Optional[str]:
        """Extrae URL de un elemento."""
        if not element:
            return None

        # Buscar en diferentes atributos
        for attr in ['href', 'src', 'data-url', 'data-href']:
            url = element.get(attr)
            if url:
                return url.strip()

        return None

    def _extract_image_url(self, element: Tag) -> Optional[str]:
        """Extrae URL de imagen."""
        if not element:
            return None

        # Buscar en diferentes atributos de imagen
        for attr in ['src', 'data-src', 'data-original', 'data-lazy']:
            url = element.get(attr)
            if url:
                return url.strip()

        return None

    def _post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-procesa los datos extraídos."""
        processed = {{}}

        for key, value in data.items():
            if value is None:
                continue

            if isinstance(value, str):
                # Limpiar strings
                value = value.strip()
                if not value:
                    continue

            processed[key] = value

        return processed

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida que los datos extraídos sean correctos."""
        required_fields = ['title']  # Campos mínimos requeridos

        for field in required_fields:
            if field not in data or not data[field]:
                return False

        return True
'''

        return template.format(
            class_name=class_name,
            selectors=repr(selectors)
        )

    def _generate_test_class(self, class_name: str, module_name: str) -> str:
        """Genera tests automáticos."""
        template = '''"""
Tests for {class_name}Scraper
Auto-generated by CodeAutoModifier
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup

from src.scrapers.{module_name}.scraper import {class_name}Scraper
from src.scrapers.{module_name}.parser import {class_name}Parser

class Test{class_name}Scraper:

    def setup_method(self):
        """Setup para cada test."""
        self.scraper = {class_name}Scraper()

    def test_initialization(self):
        """Test inicialización básica."""
        assert self.scraper is not None
        assert self.scraper.domain
        assert self.scraper.parser is not None

    @pytest.mark.asyncio
    async def test_scrape_url_success(self):
        """Test scraping exitoso."""
        mock_html = """
        <html>
            <body>
                <h1>Test Title</h1>
                <p>Test content</p>
            </body>
        </html>
        """

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await self.scraper.scrape_url('http://example.com')

            assert 'error' not in result
            assert 'url' in result

    @pytest.mark.asyncio
    async def test_scrape_url_http_error(self):
        """Test manejo de errores HTTP."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await self.scraper.scrape_url('http://example.com')

            assert 'error' in result
            assert 'HTTP 404' in result['error']

    @pytest.mark.asyncio
    async def test_scrape_multiple_urls(self):
        """Test scraping múltiple."""
        urls = ['http://example1.com', 'http://example2.com']

        with patch.object(self.scraper, 'scrape_url') as mock_scrape:
            mock_scrape.return_value = {{'title': 'Test', 'url': 'test'}}

            results = await self.scraper.scrape_multiple(urls)

            assert len(results) == 2
            assert all('title' in result for result in results)

    def test_get_stats(self):
        """Test estadísticas del scraper."""
        stats = self.scraper.get_stats()

        assert 'domain' in stats
        assert 'rate_limit' in stats
        assert 'timeout' in stats

class Test{class_name}Parser:

    def setup_method(self):
        """Setup para cada test."""
        self.parser = {class_name}Parser()

    def test_parse_basic_html(self):
        """Test parsing básico."""
        html = """
        <html>
            <body>
                <h1>Test Title</h1>
                <p>Test description</p>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, 'html.parser')
        result = self.parser.parse(soup)

        assert isinstance(result, dict)

    def test_extract_text(self):
        """Test extracción de texto."""
        html = '<p>  Test text with spaces  </p>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('p')

        text = self.parser._extract_text(element)

        assert text == 'Test text with spaces'

    def test_extract_price(self):
        """Test extracción de precios."""
        html = '<span>$123.45</span>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('span')

        price = self.parser._extract_price(element)

        assert price == 123.45

    def test_validate_data_success(self):
        """Test validación de datos exitosa."""
        data = {{'title': 'Test Title', 'description': 'Test desc'}}

        is_valid = self.parser.validate_data(data)

        assert is_valid is True

    def test_validate_data_missing_required(self):
        """Test validación con campos requeridos faltantes."""
        data = {{'description': 'Test desc'}}  # Falta title

        is_valid = self.parser.validate_data(data)

        assert is_valid is False
'''

        return template.format(
            class_name=class_name,
            module_name=module_name
        )

    def _domain_to_class_name(self, domain: str) -> str:
        """Convierte dominio a nombre de clase válido."""
        # Remover protocolo si existe
        domain = domain.replace('http://', '').replace('https://', '')

        # Remover www si existe
        domain = domain.replace('www.', '')

        # Convertir a CamelCase
        parts = domain.replace('.', '_').replace('-', '_').split('_')
        return ''.join(word.capitalize() for word in parts if word)

    def _load_templates(self) -> Dict[str, str]:
        """Carga templates para generación de código."""
        return {
            'function': '''
def {name}({params}):
    """{docstring}"""
    {body}
''',
            'class': '''
class {name}:
    """{docstring}"""

    def __init__(self{init_params}):
        {init_body}

    {methods}
''',
            'test_function': '''
def test_{name}():
    """Test for {name}."""
    # Arrange
    {arrange}

    # Act
    {act}

    # Assert
    {assert_statements}
'''
        }

    def _load_improvement_patterns(self) -> List[Dict[str, Any]]:
        """Carga patrones de mejora automática."""
        return [
            {
                'name': 'replace_print_with_logging',
                'pattern': r'print\((.*)\)',
                'replacement': r'logger.info(\1)',
                'description': 'Replace print statements with logging'
            },
            {
                'name': 'add_type_hints',
                'pattern': r'def (\w+)\((.*)\):',
                'check': lambda content: '-> ' not in content,
                'description': 'Add return type hints to functions'
            },
            {
                'name': 'extract_long_functions',
                'check': lambda content: len(content.split('\n')) > 50,
                'description': 'Extract long functions into smaller ones'
            }
        ]

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calcula complejidad ciclomática."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With, ast.AsyncWith):
                complexity += 1

        return complexity

    def _detect_code_issues(self, content: str, tree: ast.AST) -> List[str]:
        """Detecta issues en el código."""
        issues = []

        # Funciones muy largas
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.end_lineno and node.lineno:
                    length = node.end_lineno - node.lineno
                    if length > 50:
                        issues.append(f"Function '{node.name}' is too long ({length} lines)")

        # Print statements
        if 'print(' in content:
            issues.append("Contains print statements (should use logging)")

        # Missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append(f"{node.__class__.__name__} '{node.name}' missing docstring")

        # Hardcoded values
        if re.search(r'http://|https://', content):
            issues.append("Contains hardcoded URLs")

        return issues

    def _generate_suggestions(self, content: str, tree: ast.AST, issues: List[str]) -> List[str]:
        """Genera sugerencias de mejora."""
        suggestions = []

        for issue in issues:
            if "too long" in issue:
                suggestions.append("Consider breaking long functions into smaller, focused functions")
            elif "print statements" in issue:
                suggestions.append("Replace print statements with proper logging")
            elif "missing docstring" in issue:
                suggestions.append("Add descriptive docstrings to functions and classes")
            elif "hardcoded" in issue:
                suggestions.append("Move hardcoded values to configuration files")

        return suggestions

    def _calculate_quality_score(self, content: str, tree: ast.AST, issues: List[str]) -> float:
        """Calcula score de calidad del código."""
        base_score = 1.0

        # Penalizar por issues
        penalty_per_issue = 0.1
        score = base_score - (len(issues) * penalty_per_issue)

        # Bonificar buenas prácticas
        if 'logging' in content:
            score += 0.1
        if 'typing' in content or 'Type' in content:
            score += 0.1
        if 'docstring' in content or '"""' in content:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extrae dependencias del código."""
        dependencies = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module)

        return list(dependencies)

    def _apply_automatic_improvements(self, file_path: str,
                                    analysis: CodeAnalysisResult) -> List[CodeChange]:
        """Aplica mejoras automáticas basadas en el análisis."""
        changes = []

        with open(file_path, 'r') as f:
            content = f.read()

        # Aplicar patrones de mejora
        for pattern in self.improvement_patterns:
            if pattern['name'] == 'replace_print_with_logging':
                if 'print(' in content:
                    new_content = re.sub(pattern['pattern'], pattern['replacement'], content)
                    if new_content != content:
                        changes.append(CodeChange(
                            file_path=file_path,
                            change_type='modify',
                            description=pattern['description'],
                            old_content=content,
                            new_content=new_content,
                            confidence=0.9
                        ))

        return changes

    def _detect_performance_optimizations(self, content: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detecta oportunidades de optimización de performance."""
        optimizations = []

        # Detectar loops innecesarios
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Ejemplo: detectar loops que podrían ser list comprehensions
                optimizations.append({
                    'description': 'Consider using list comprehension for better performance',
                    'old_code': 'for loop',
                    'new_code': 'list comprehension',
                    'confidence': 0.7
                })

        return optimizations

    def _apply_code_change(self, change: CodeChange):
        """Aplica un cambio de código específico."""
        # Crear backup
        backup_path = self.backup_dir / f"{Path(change.file_path).name}.backup"
        shutil.copy2(change.file_path, backup_path)

        # Aplicar cambio
        with open(change.file_path, 'w') as f:
            f.write(change.new_content)

    def get_modification_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de modificación."""
        return {
            'total_templates': len(self.templates),
            'improvement_patterns': len(self.improvement_patterns),
            'backup_dir': str(self.backup_dir),
            'backups_count': len(list(self.backup_dir.glob('*.backup')))
        }
