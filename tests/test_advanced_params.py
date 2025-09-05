from src.intelligence.intent_recognizer import IntentRecognizer

# Casos de prueba avanzados para extracción de parámetros
test_cases = [
    # Edición avanzada
    'muestra las líneas 10-20 del archivo src/main.py',
    'cambia "old" por "new" en config.json con 3 líneas de contexto',
    'agrega "nueva línea" al final de logs/app.log',
    'reemplaza línea 15 por "contenido nuevo" en src/utils.py',
    'busca y reemplaza globalmente "foo" por "bar" en todo el proyecto',

    # Comandos avanzados
    'get-process | select name, id',
    'ls -la src/',
    'muestra el contenido de README.md',
    'reinicia el sistema',
    'net user administrador /add',
    'remove-item -Recurse -Force temp/',
]

print('=== PRUEBAS DE EXTRACCIÓN AVANZADA DE PARÁMETROS ===\n')

for i, case in enumerate(test_cases, 1):
    intent = IntentRecognizer.recognize(case)
    print(f'{i}. Input: "{case}"')
    print(f'   Intent: {intent.type.value}')
    print(f'   Params: {intent.parameters}')
    print()
