# Guía Completa Consolidada: Gemini, Vertex AI, MCP y Librería de Prompts

**Fecha de creación:** 2025-09-08  
**Versión:** 1.0 - Consolidación completa  
**Propósito:** Archivo único que combina toda la información de Gemini, Vertex AI, Model Context Protocol, prompts, configuración del proyecto y ejemplos prácticos organizados por niveles.

---

## Índice

1. [Introducción y Configuración del Proyecto](#1-introducción-y-configuración-del-proyecto)
2. [Fundamentos Teóricos](#2-fundamentos-teóricos)
3. [Gemini para Google Cloud](#3-gemini-para-google-cloud)
4. [Gemini Code Assist](#4-gemini-code-assist)
5. [Vertex AI - Diseño de Prompts](#5-vertex-ai---diseño-de-prompts)
6. [Model Context Protocol (MCP)](#6-model-context-protocol-mcp)
7. [Ejemplos Prácticos por Niveles](#7-ejemplos-prácticos-por-niveles)
8. [Librería de Prompts Expandida](#8-librería-de-prompts-expandida)
9. [Recetas y Plantillas Técnicas](#9-recetas-y-plantillas-técnicas)
10. [Fuentes y Referencias](#10-fuentes-y-referencias)

---

## 1. Introducción y Configuración del Proyecto

### 1.1 Descripción General del Proyecto

Este proyecto es una aplicación sofisticada de web scraping en Python. Su función principal es extraer datos estructurados de diversos sitios web. La arquitectura está diseñada para ser modular, permitiendo una fácil extensión a nuevos sitios y tipos de datos.

**Funcionalidades principales:**
- Fetching asíncrono de páginas web usando `httpx` y `playwright`
- Parsing de contenido HTML con `BeautifulSoup` y `readability-lxml`
- Validación y estructuración de datos usando `pydantic`
- Almacenamiento de datos extraídos en formato estructurado usando `dataset`

### 1.2 Dependencias

#### Dependencias de Producción

- `dataset`: Para operaciones de base de datos
- `html2text`: Para convertir HTML a Markdown
- `playwright`: Para automatización de navegador y renderizado JavaScript
- `readability-lxml`: Para extraer el contenido principal de una página
- `pydantic`: Para validación de datos
- `httpx`: Para solicitudes HTTP asíncronas
- `imagehash`: Para hashing y comparación de imágenes
- `robotexclusionrulesparser`: Para respetar `robots.txt`
- `playwright-stealth`: Para evitar detección de bots
- `pydantic-settings`: Para gestión de configuraciones

#### Dependencias de Desarrollo

- `pre-commit`: Para ejecutar hooks antes de commits
- `black`: Para formateo de código
- `isort`: Para ordenar imports
- `flake8`: Para linting

### 1.3 Estilo de Código y Convenciones

El proyecto mantiene un estilo de código estricto para mantener legibilidad y consistencia. Todo el código debe adherir a los siguientes estándares, que son verificados automáticamente por hooks de pre-commit.

- **Formateador:** `black` con longitud de línea de **120 caracteres**
- **Ordenamiento de Imports:** `isort` con perfil `black`
- **Linter:** `flake8` para identificar errores potenciales y problemas de estilo

**Regla de Oro:** Siempre ejecutar `pre-commit run --all-files` antes de commits.

### 1.4 Testing

El proyecto usa `pytest` para testing unitario e integración.

- **Ubicación de Tests:** Todos los tests están en el directorio `tests/`
- **Ejecución:** Ejecutar tests usando el comando `pytest`
- **Configuración:** `pytest.ini` está configurado para descubrir y ejecutar tests automáticamente en el directorio `tests`

### 1.5 Configuración Avanzada: Servidores MCP

Esta sección está destinada a configurar conexiones a servidores Model Control Plane (MCP) personalizados. Estos podrían ser modelos privados o fine-tuned que proporcionan capacidades especializadas para extracción de datos, clasificación u otras tareas.

**Nota para Gemini:** Cuando necesites usar un modelo especializado para una tarea, consulta la configuración a continuación. Si no hay un modelo listado, usa tus capacidades predeterminadas.

#### Configuración de Ejemplo (Para ser completada por el usuario)

```yaml
# Este es un ejemplo de cómo podrías configurar servidores MCP.
# Reemplaza con tu configuración actual.
mcp_servers:
  - name: "document_summarizer"
    url: "https://api.example.com/summarize"
    api_key: "YOUR_API_KEY_HERE"
    description: "Un modelo especializado para resumir documentos largos."
  - name: "product_classifier"
    url: "https://api.example.com/classify"
    api_key: "YOUR_API_KEY_HERE"
    description: "Un modelo para clasificar productos de e-commerce en categorías."
```

### 1.6 Instrucciones para Gemini

Como asistente IA PRO para este proyecto, se espera que:

1. **Adherirse a Convenciones:** Seguir estrictamente el estilo de código y convenciones definidas en la sección 1.3
2. **Escribir Tests:** Para cualquier nueva funcionalidad o corrección de bug, debes escribir tests correspondientes en el directorio `tests/`
3. **Usar Dependencias:** Aprovechar las dependencias existentes al máximo. No introducir nuevas dependencias sin permiso explícito
4. **Ser Proactivo:** Cuando se te pida realizar una tarea, considera el alcance completo de la solicitud. Por ejemplo, si se te pide agregar un nuevo scraper, también deberías crear un archivo de test para él
5. **Mantener Modularidad:** Mantener el código modular y fácil de mantener. Crear nuevos archivos y clases cuando sea apropiado

### 1.7 Boilerplate: Nuevo Scraper

Cuando crees un nuevo scraper, usa el siguiente boilerplate como punto de partida.

```python
# src/scrapers/new_site_scraper.py

from httpx import AsyncClient
from .base_scraper import BaseScraper, ScrapeResult

class NewSiteScraper(BaseScraper):
    """
    Un scraper para new-site.com.
    """
    def __init__(self):
        super().__init__(name="new_site")

    async def scrape(self, client: AsyncClient, url: str) -> ScrapeResult:
        """
        Scrapes a single URL from new-site.com.
        """
        response = await client.get(url)
        response.raise_for_status()

        # ... lógica de parsing aquí ...

        return ScrapeResult(
            url=url,
            content="...",
            data={...}
        )
```

---

## 2. Fundamentos Teóricos

### 2.1 Arquitectura de LLMs

Los Large Language Models (LLMs) son modelos entrenados para predecir tokens. Su salida depende de:
- Arquitectura del modelo
- Pre-entrenamiento
- Fine-tuning
- Contexto proporcionado en el prompt

### 2.2 Context Window

La cantidad máxima de tokens que el modelo puede considerar; su manejo eficiente es crítico:
- Resumen de contenido largo
- Chunking de documentos
- Retrieval-Augmented Generation (RAG)

### 2.3 Hallucinations y Factualidad

**Definición:** Generación de información no verificada o inventada.

**Mitigaciones:**
- Usar RAG (retrieval)
- OutputSchema/validators
- Fuentes verificables
- Citar evidencias
- Humano en el bucle

### 2.4 Evaluación y Métricas

**Métricas Automáticas:**
- BLEU/ROUGE (limitadas para código)
- Exact-match (cuando la referencia es conocida)
- Pass@k (para código)
- Factuality metrics
- Cost-per-correct-result

**Evaluación Humana:**
- Revisión manual
- Pruebas unitarias generadas automáticamente
- Canary tests en producción

### 2.5 Seguridad, Privacidad y Gobernanza

- Minimizar datos sensibles en prompts
- Redacción y tokenización
- Retención y auditoría de prompts
- Roles y control de accesos
- Enmascaramiento de secretos

---

## 3. Gemini para Google Cloud

### 3.1 Descripción General

Gemini es un conjunto de experiencias de asistencia generativa integradas en productos y servicios de Google Cloud:
- Cloud Assist
- Gemini Code Assist
- BigQuery
- Colab Enterprise
- Looker

**Usos principales:**
- Acelerar diseño, operación y solución de problemas en la nube
- Generar y depurar código
- Analizar datos
- Asistir en consultas SQL
- Sugerir configuraciones
- Producir documentación y runbooks

### 3.2 Mejores Prácticas para Prompts

**Principios:**
- Contexto específico: describir objetivo, entorno, versiones
- Precisión y concisión: hasta ~4,000 caracteres
- Divide y vencerás: descomponer tareas complejas
- Formato explícito: JSON, CSV, tablas, pasos numerados

**Tipos de Asistencia:**
- Información y referencia
- Analítica y operativa
- Tareas guiadas
- Generativa

### 3.3 IA Responsable y Seguridad

- Los modelos pueden producir información incompleta o incorrecta
- Añadir controles de validación
- Revisar políticas de privacidad y retención

### 3.4 "Thinking" en Vertex AI

Algunos modelos pueden exponer razonamiento o pasos intermedios para depuración y auditoría.

---

## 4. Gemini Code Assist

### 4.1 Estructura de Configuración

**Ubicación:** Carpeta `.gemini/` en la raíz del repositorio

**Archivos típicos:**
- `config.yaml`
- `styleguide.md`

#### Ejemplo de config.yaml

```yaml
have_fun: false
ignore_patterns:
  - "**/*.min.js"
  - "docs/**"
code_review:
  disable: false
  comment_severity_threshold: MEDIUM
  max_review_comments: 100
  pull_request_opened:
    help: false
    summary: true
    code_review: true
    include_drafts: true
```

#### Ejemplo de styleguide.md

Convenciones de nombre, límites ciclomáticos, estándares de logging, formatos de tests.

### 4.2 Comandos y Reglas en IDEs

- VS Code / JetBrains: comandos custom como `add-comments` o `enforce-tests`
- Reglas por equipo: idioma de respuesta, formato, plantillas de salida

### 4.3 Permisos de Herramientas

- Principio del menor privilegio
- Aprobación explícita para acciones que modifican repos o infraestructura
- Registro de acciones (audit log)
- Gestión de secretos desde Secret Manager

---

## 5. Vertex AI - Diseño de Prompts

Vertex AI resume patrones efectivos: claridad, estructura, few-shot, razonamiento explícito y descomposición por pasos.

### 5.1 Plantilla de Prompt

```text
Tarea: ...
Contexto: producto, versión, región
Entradas: ...
Requisitos: ...
Formato salida: JSON/tabla/pasos
Restricciones: ...
```

### 5.2 System Instructions

Metainstrucciones que definen rol y restricciones. Mantener versionadas.

### 5.3 Few-shot y Contextual Information

- Incluir 1-3 buenos ejemplos que enseñen el formato
- Inyectar especificaciones y esquemas relevantes
- RAG/embeddings cuando aplique

### 5.4 Experimentación

- Comparar variantes A/B
- Mantener registro de métricas (precisión, costo, hallucinations)

---

## 6. Model Context Protocol (MCP)

### 6.1 ¿Qué es MCP?

Protocolo para integrar LLMs con herramientas y datos mediante clientes y servidores (JSON-RPC 2.0).

**Objetivos:**
- Seguridad
- Composición
- Discovery

**Actores:**
- Host: aplicación LLM
- Cliente: conector
- Servidor: aporta capabilities/tools y prompts

### 6.2 Tools, Invocation y OutputSchema

- **Discovery:** `tools/list`
- **Invocation:** `tools/call` con validación por JSON Schema
- **Resultados:** `structuredContent` y `unstructured`

### 6.3 Seguridad y Human-in-the-Loop

- Confirmaciones para ejecutar acciones sensibles
- Interfaz que muestre herramientas expuestas
- Registro de decisiones

### 6.4 Inspector y Servidores de Referencia

- MCP Inspector (npx) para listar y probar servidores
- Repositorio `modelcontextprotocol/servers` con ejemplos

### 6.5 Ejecutar Servidores de Ejemplo

**TypeScript:**

```bash
npx -y @modelcontextprotocol/server-memory
```

**Python:**

```bash
pip install mcp-server-git
python -m mcp_server_git
```

---

## 7. Ejemplos Prácticos por Niveles

### 7.1 Nivel Básico - Extracción Simple

**Objetivo:** Extraer título y meta description de HTML.

**Prompt:**

```text
System: Eres un extractor de metadatos. Devuelve JSON con: title, meta_description.
User: ---BEGIN HTML---
{html}
---END HTML---
```

**Python ejemplo:**

```python
import requests

def extract_meta(html, model_call):
    payload = {
        'messages': [
            {'role':'system','content':'Eres un extractor...'},
            {'role':'user','content':f'---BEGIN HTML---\n{html}\n---END HTML---'}
        ]
    }
    return model_call(payload)
```

### 7.2 Nivel Intermedio - Tablas y Normalización

**Caso:** Extraer primera tabla HTML y devolver CSV.

**Prompt:**

```text
System: Extrae la primera tabla y devuélvela como CSV con encabezados.
Input: ---BEGIN HTML---{html}---END HTML---
```

**Post-procesado:**

- Convertir CSV a Pandas DataFrame
- Normalizar nombres de columnas

### 7.3 Nivel Avanzado - Pipeline Completo

**Arquitectura:** Scraper → LLM extractor → Validator → Store

**OutputSchema ejemplo:**

```json
{
  "type":"object",
  "properties":{
    "title":{"type":"string"},
    "price":{"type":"number"},
    "sku":{"type":"string"}
  },
  "required":["title","sku"]
}
```

**Workflow:**

1. Ejecutar prompt que devuelva JSON
2. Validar con JSON Schema
3. Si falla, enviar a revisión humana

### 7.4 Nivel Pro - Orquestación con MCP

**Ejemplo:** Agente que automatice revisión de cambios y abra PRs.

**Componentes:**

- `server-git` (MCP)
- `server-memory` (MCP)
- Cliente LLM con capacidad para llamar tools

**Flujo:**

1. Consultar `server-git` por diffs
2. Generar resumen y sugerir cambios
3. Abrir PRs con checklist
4. Solicitar revisión humana

### 7.5 Nivel Hacking - Generación Masiva

**Use case:** Generar datasets sintéticos y tests unitarios.

```python
def generate_synthetic_examples(model_call, base_prompt, variations):
    results = []
    for v in variations:
        payload = base_prompt.format(**v)
        r = model_call({'messages':[{'role':'user','content':payload}]})
        results.append(r)
    return results
```

### 7.6 Nivel Teórico - Trade-offs y Métricas

- **Trade-offs:** costo vs contexto, hallucination vs recall, latencia vs throughput
- **Métricas:** exact-match, factuality scores, hallucination rates, cost-per-query

---

## 8. Librería de Prompts Expandida

### 8.1 Notas de Uso

- Reemplazar placeholders como `CODE`, `HTML`, `SCHEMA` antes de usar
- Preferir estructura `system` + `user` para llamadas a APIs de chat
- Siempre solicitar `outputSchema` cuando se espere JSON estructurado

### 8.2 Categorías de Prompts

#### 1) Generación de Código - Función Python

System: "You are a senior Python engineer. Produce clean, typed, testable functions following PEP8 and include docstrings and examples."

User:
```text
Task: Implement a function `parse_price(text: str) -> float` that accepts prices like "USD 12.34", "12,34€", "$12" and returns the price in euros as float. Assume 1 USD = 0.92 EUR. Handle thousands separators and missing currency as EUR.
Format: Return only the function source code in a single `python` fenced block.
Examples:
- "USD 12.34" -> 11.3528
- "12,34€" -> 12.34
Constraints: include type annotations, raise ValueError for unparsable inputs.
```

#### 2) Reparar Código con Tests

System: "You are a code reviewer. Given failing pytest output and code, produce a unified diff patch that fixes the bug and add a new pytest that covers the failing case."

User:
```text
Task: Repair the failing function. Input: `PASTE CODE` and `PASTE TEST OUTPUT`
Format: Return a diff (unified) and the new/modified test file content.
```

#### 3) Generar Modelos DB + Migración Alembic

System: "You are a backend engineer. Generate SQLAlchemy models and an Alembic `upgrade` and `downgrade` migration snippet for the schema change."

User:
```text
Task: Create a `Product` model with fields: id (int pk), sku (str unique), name, price (decimal), metadata (json). Provide SQLAlchemy model and Alembic migration `upgrade`/`downgrade` functions.
Format: respond with two fenced blocks: first `python` for model, second `python` for alembic revision code.
```

#### 4) Componentes Frontend (React)

System: "You are a frontend engineer producing small React components with clear props and tests (React Testing Library)."

User:
```text
Task: Implement a React component `UrlForm` that posts to `/api/extract` and shows the JSON result. Include a unit test that mocks fetch and verifies render flow.
Format: Return `jsx` for component and `javascript` for test.
```

#### 5) TUI con Textual

System: "You are a terminal UI developer. Create a small Textual app that lists items and shows details on selection."

User:
```python
Task: Provide `python` code with a small Textual app: list view + details pane.
```

#### 6) Invocación de Herramientas MCP

System: "You are an LLM that can discover and call tools via MCP. Use `tools/list` to find available tools, then call them with `tools/call` providing `outputSchema` where applicable."

User:
```json
Task: Discover available tools and extract diffs from git using the `git` tool. Provide the JSON of results and, if non-empty, summarize the top 3 diffs.
Format: Provide a JSON output matching schema: {"diffs": [{"file": str, "diff": str}], "summary": str}
```

#### 7) Llamadas a Funciones / Salida Estructurada

System: "You are an assistant that returns only JSON matching the provided schema. You must not produce any extra text."

User:
```json
Schema: `PASTE JSON SCHEMA`
Task: Produce an output that validates against the schema given the input `PASTE INPUT`
Format: strict JSON.
```

#### 8) Prompt de Evaluación (Generar Tests Unitarios)

System: "You are a test generator. Produce pytest tests that cover edge cases, happy path, and property-based checks when appropriate."

User:
```python
Task: Given function code `CODE`, produce `tests/test_<module>.py` with >= 5 tests covering typical and edge cases.
Format: single python fenced block.
```

#### 9) Infra como Código - Snippet Terraform

System: "You are an infra engineer. Produce minimal Terraform snippets with variables and outputs."

User:
```hcl
Task: Create a Terraform resource for an Azure Container App or for an AWS ECS service (choose one), include variables and a minimal output block. Assume registry credentials are provided.
```

#### 10) Optimización de Prompts / A/B Testing

System: "You are an experiment designer. Produce two prompt variations (A and B), instrumentation plan, and metrics to compare."

User:
```text
Task: For the `parse_price` generator, provide two prompt variants, measurement plan (latency, exact-match on outputs, failure rate), and expected sample size.
```

#### 11) Scraping y Extracción de Datos

System: "You are a data scraper expert. Extract structured data from HTML using selectors and return JSON."

User:
```text
Task: From the HTML, extract product names, prices, and descriptions using CSS selectors. Return JSON array of objects.
Format: [{"name": str, "price": float, "desc": str}]
Constraints: Handle missing fields gracefully.
```

#### 12) Orquestación de Pipelines

System: "You are a DevOps engineer. Design a pipeline that scrapes, processes, and stores data using queues and workers."

User:
```text
Task: Describe a Celery-based pipeline: scraper task -> LLM extractor -> validator -> DB store. Include code snippets for tasks and config.
Format: Python code blocks for each component.
```

#### 13) Evaluación de Modelos

System: "You are an ML evaluator. Compare two model outputs on accuracy, latency, and hallucinations."

User:
```text
Task: Given outputs from Model A and B on 100 samples, compute metrics: accuracy (exact match), latency (avg ms), hallucination rate (manual review needed).
Format: JSON with metrics and recommendations.
```

### 8.3 Variantes A/B y OutputSchema

#### Variantes A/B para parse_price

**Variante A (Concisa):**
```text
System: You are a precise extractor. Return only the parsed numeric value in EUR as a JSON number.
User: Parse the price from the input string and convert to EUR. Use 0.92 conversion for USD. Examples: "USD 12.34" -> 11.3528.
Output: JSON number only.
```

**Variante B (Con razonamiento):**
```text
System: You are a senior data engineer. Explain briefly the parsing rules then provide the final numeric value in EUR.
User: Given the input string, describe how you parse currency and separators, then output JSON: {"value_eur": float, "source_currency": "EUR|USD|...", "notes": "..."}.
Examples: "USD 12.34" -> {"value_eur": 11.3528, "source_currency": "USD"}
```

#### OutputSchema Ejemplo

```json
{
  "type": "object",
  "properties": {
    "value_eur": {"type": "number"},
    "source_currency": {"type": "string"},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
  },
  "required": ["value_eur", "source_currency"]
}
```

### 8.4 Plantillas MCP

#### Discovery + Call Template

```text
System: You are an assistant that must discover available MCP tools via `tools/list`, select the `git` tool if present, and call it to extract diffs. Always validate tool responses against their declared output schema.
User: Discover tools, run `tools/list`, then find a tool with id containing `git` and call it with params {"args": ["diff", "--name-only"]}. Return JSON matching: {"tool_used": str, "result": {...}}.
```

#### Function Calling Template

```json
{
  "name": "extract_price",
  "description": "Extracts price and returns structured JSON",
  "parameters": {
    "type": "object",
    "properties": {
      "text": {"type": "string"}
    },
    "required": ["text"]
  }
}
```

### 8.5 Plan de Evaluación / Instrumentación

- **Métricas:** exact-match rate, parsing failure rate, percentiles de latencia, confidence promedio
- **Diseño A/B:** ejecutar N=200 entradas por variante, comparar vía z-test
- **Logging:** almacenar input del modelo, output cruda, JSON parseado, validación pass/fail

---

## 9. Recetas y Plantillas Técnicas

### 9.1 cURL Genérico para Generative Models

```bash
curl -s -X POST "https://generativemodels.googleapis.com/v1/models/MODEL:generate" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"system","content":"You are a metadata extractor"},{"role":"user","content":"---BEGIN HTML---<html>...---END HTML---"}]}'
```

### 9.2 Python Template con Requests

```python
import os
import requests

API_ENDPOINT = os.environ.get('GM_API_ENDPOINT')
TOKEN = os.environ.get('GOOGLE_OAUTH_TOKEN')

def call_model(payload: dict):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type':'application/json'}
    r = requests.post(API_ENDPOINT, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def generate_from_html(html: str, model='MODEL'):
    payload = {
        'model': model,
        'messages':[{'role':'system','content':'You are an extractor that outputs JSON.'},
                    {'role':'user','content':f'---BEGIN HTML---\n{html}\n---END HTML---'}],
        'maxOutputTokens': 800
    }
    return call_model(payload)
```

### 9.3 Validación con JSON Schema

```python
from jsonschema import validate, ValidationError

schema = {
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "price": {"type": "number"}
  },
  "required": ["title"]
}

def validate_output(output_json):
  try:
    validate(instance=output_json, schema=schema)
    return True, None
  except ValidationError as e:
    return False, str(e)

# Uso:
# valid, err = validate_output(parsed_json)
```

### 9.4 Ejemplo Completo con Manejo Estructurado

```python
payload = {
  'messages': [
    {'role':'system','content':'Eres un extractor de metadatos que responde JSON.'},
    {'role':'user','content':'---BEGIN HTML---<html>...---END HTML---'}
  ],
  'maxOutputTokens': 800
}

resp = call_model(payload)
# Extraer contenido según la forma del API (ajustar según respuesta real)
content = resp.get('output', [{}])[0].get('content')
import json
parsed = json.loads(content)
valid, err = validate_output(parsed)
if not valid:
  # fallback / revisión humana
  print('Validation failed:', err)
```

### 9.5 MCP Quickstart

```bash
# TypeScript
npx -y @modelcontextprotocol/server-memory

# Python
pip install mcp-server-git
python -m mcp_server_git
```

### 9.6 Desarrollo Completo - Arquitectura Mini App

**Estructura propuesta:**

- `mini_app/backend/` (FastAPI)
- `mini_app/frontend/` (React + Vite)
- `mini_app/db/` (SQLAlchemy + Alembic)
- `mini_app/tui/` (Textual)

#### Backend: FastAPI + Llamada a Gemini

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from typing import Any
import requests

app = FastAPI()

GM_ENDPOINT = os.environ.get('GM_API_ENDPOINT')
GM_TOKEN = os.environ.get('GOOGLE_OAUTH_TOKEN')

class HTMLIn(BaseModel):
    url: str | None = None
    html: str | None = None

class ExtractOut(BaseModel):
    title: str | None
    meta_description: str | None

def call_gm_api(payload: dict) -> Any:
    headers = {'Authorization': f'Bearer {GM_TOKEN}', 'Content-Type':'application/json'}
    r = requests.post(GM_ENDPOINT, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

@app.post('/extract', response_model=ExtractOut)
def extract(in_data: HTMLIn):
    if not (in_data.html or in_data.url):
        raise HTTPException(status_code=400, detail='Provide html or url')
    html = in_data.html or requests.get(in_data.url).text
    payload = {'messages': [{'role':'system','content':'You are an extractor that returns JSON with title and meta_description.'},
                            {'role':'user','content':f'---BEGIN HTML---\n{html}\n---END HTML---'}],
               'maxOutputTokens':800}
    resp = call_gm_api(payload)
    # parse response (adapter depending on real API surface)
    try:
        content = resp.get('output', [{}])[0].get('content')
        import json
        parsed = json.loads(content)
        return ExtractOut(title=parsed.get('title'), meta_description=parsed.get('meta_description'))
    except Exception:
        raise HTTPException(status_code=502, detail='Invalid model response')
```

#### Base de Datos: SQLAlchemy + Alembic

```python
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PageMetadata(Base):
    __tablename__ = 'page_metadata'
    id = Column(Integer, primary_key=True)
    url = Column(String(2048), index=True)
    title = Column(String(1024))
    meta_description = Column(Text)
```

#### Frontend: React + Vite

```jsx
import { useState } from 'react'

function App(){
  const [url,setUrl] = useState('')
  const [result,setResult] = useState(null)
  async function fetchMeta(){
    const r = await fetch('/api/extract',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})})
    const j = await r.json()
    setResult(j)
  }
  return (<div style={{padding:20}}>
    <h1>Metadata Extractor</h1>
    <input value={url} onChange={e=>setUrl(e.target.value)} placeholder='https://...' style={{width:'60%'}}/>
    <button onClick={fetchMeta}>Extract</button>
    {result && <pre>{JSON.stringify(result,null,2)}</pre>}
  </div>)
}

export default App
```

#### TUI: Textual

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class MetaTUI(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static('Use the app to view recent extractions')
        yield Footer()

if __name__ == '__main__':
    MetaTUI().run()
```

---

## 10. Fuentes y Referencias

Se incluyen todas las URLs proporcionadas por el usuario (documentación oficial, codelabs, guías) y enlaces adicionales. Consulta estas páginas para detalles específicos de APIs, límites y actualizaciones.

### Documentación Oficial de Google Cloud

- [Gemini para Google Cloud](https://cloud.google.com/gemini/docs)
- [Gemini Code Assist](https://cloud.google.com/code-assist)
- [Vertex AI Prompts](https://cloud.google.com/vertex-ai/docs/generative-ai/prompt-gallery)

### Model Context Protocol

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)

### Recursos Adicionales

- Documentación de FastAPI
- SQLAlchemy Documentation
- React Documentation
- Textual Framework Documentation
- [Documentación de Textual](https://textual.textualize.io/)
- [Guía de Pydantic](https://docs.pydantic.dev/)
- [Documentación de AsyncIO](https://docs.python.org/3/library/asyncio.html)

---

**Notas Finales:**
Esta guía consolidada combina teoría, ejemplos prácticos, configuración del proyecto, prompts organizados y referencias completas. Para expansiones específicas, indica qué sección quieres profundizar.

**Archivos consolidados:**

- `docs/gemini_vertex_mcp_reference.md`
- `docs/gemini_vertex_mcp_complete_guide.md`
- `docs/gemini_vertex_mcp_master_guide.md`
- `docs/gemini_vertex_mcp_mega_guide.md`
- `docs/prompt_library.md`
- `docs/GEMINI.md`
- `GEMINI.md` (raíz del proyecto)

Todos los archivos originales han sido consolidados en este documento único para facilitar el acceso y mantenimiento.
