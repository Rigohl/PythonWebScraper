Proyecto experimental: Motor QA sin IA (BM25-like)

Este directorio contiene un scaffold aislado para probar un motor de recuperación de información
sin usar modelos de IA externos. Implementa un indexador y un recuperador (retriever) simples
basados en BM25-like y una pequeña CLI para hacer consultas de ejemplo.

Estructura:
- src/qa/indexer.py  # indexador simple
- src/qa/retriever.py  # recuperador que usa el indexador
- cli.py  # script de ejemplo para consultas
- data/sample_docs.json  # documentos de ejemplo
- tests/test_retriever.py  # tests unitarios

Uso rápido:
  python experimental/qa/cli.py "tu consulta aquí"

Opcional: activar el reader de Hugging Face
-----------------------------------------

El lector extractivo (`SimpleReader`) puede usar un modelo de Hugging Face (transformers)
para responder preguntas de forma extractiva. Esto es completamente opcional y desactivado
por defecto; el código ya proporciona una alternativa de "fallback" que devuelve el
snippet más relevante sin llamar a ningún servicio externo.

Pasos para activar el reader HF (local):

1. Instala las dependencias opcionales (recomendado dentro de un virtualenv):

```bash
pip install -r experimental/qa/requirements-qa.txt
```

2. Proporciona el nombre del modelo a usar. Puedes hacerlo de dos formas:

- Desde Python llamando directamente al reader:

```py
from qa.reader import SimpleReader
reader = SimpleReader(hf_model="distilbert-base-cased-distilled-squad")
out = reader.answer("¿Cuál es la capital de Francia?", chunks)
```

- O exportando una variable de entorno y creando el pipeline manualmente (tu script puede
  leer la variable y crear `SimpleReader(os.environ.get('HF_MODEL'))`).

```bash
export HF_MODEL=distilbert-base-cased-distilled-squad
python experimental/qa/cli.py "tu consulta"
```

Notas de seguridad y privacidad:
- Antes de encolar sugerencias, el adaptador aplica una sanitización simple de PII (emails,
  teléfonos, tarjetas) al payload. Si habilitas HF asegúrate de revisar la política de datos
  local y la licencia del modelo que uses. El proyecto experimental no enviará datos fuera
  de tu máquina a menos que así lo configures explícitamente.

PowerShell (Windows) — ejemplo rápido
------------------------------------

Si usas PowerShell (pwsh) en Windows, así puedes activar un modelo HF localmente y
ejecutar la CLI:

```powershell
# en PowerShell (temporal para la sesión)
$env:HF_MODEL = 'distilbert-base-cased-distilled-squad'
# (opcional) instalar deps en el entorno activo
pip install -r experimental/qa/requirements-qa.txt

python .\experimental\qa\cli.py "¿Cuál es la capital de Francia?"
```

