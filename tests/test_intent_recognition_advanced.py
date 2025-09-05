"""
Tests para el reconocimiento de intenciones avanzadas.

Este archivo prueba la capacidad del IntentRecognizer
para detectar intenciones relacionadas con edición de archivos
y ejecución de comandos en terminal.
"""

import pytest
from src.intelligence.intent_recognizer import IntentRecognizer, IntentType

def test_edit_intent_recognition():
    """Prueba el reconocimiento de intenciones de edición."""

    # Casos de prueba en español
    assert IntentRecognizer.recognize("edita el archivo config.json").type == IntentType.EDIT
    assert IntentRecognizer.recognize("modifica el código en main.py").type == IntentType.EDIT
    assert IntentRecognizer.recognize("necesito cambiar este archivo").type == IntentType.EDIT
    assert IntentRecognizer.recognize("actualiza el contenido del documento").type == IntentType.EDIT

    # Casos de prueba en inglés
    assert IntentRecognizer.recognize("edit the configuration file").type == IntentType.EDIT
    assert IntentRecognizer.recognize("modify this script.py").type == IntentType.EDIT
    assert IntentRecognizer.recognize("can you update the code?").type == IntentType.EDIT
    assert IntentRecognizer.recognize("change the file content please").type == IntentType.EDIT

    # Casos con nombres de archivo
    text = "edita el archivo config.json"
    intent = IntentRecognizer.recognize(text)
    assert intent.type == IntentType.EDIT
    assert intent.parameters.get("file") == "config.json"

    # Casos con contenido a modificar
    text = "cambia 'timeout: 30' por 'timeout: 60' en config.json"
    intent = IntentRecognizer.recognize(text)
    assert intent.type == IntentType.EDIT
    assert intent.parameters.get("file") == "config.json"

def test_terminal_intent_recognition():
    """Prueba el reconocimiento de intenciones de terminal."""

    # Casos de prueba en español
    assert IntentRecognizer.recognize("ejecuta en terminal ls").type == IntentType.TERMINAL
    assert IntentRecognizer.recognize("corre el comando 'dir'").type == IntentType.TERMINAL
    assert IntentRecognizer.recognize("usa el cmd para mostrar archivos").type == IntentType.TERMINAL
    assert IntentRecognizer.recognize("lanza powershell").type == IntentType.TERMINAL

    # Casos de prueba en inglés
    assert IntentRecognizer.recognize("run in terminal ls -la").type == IntentType.TERMINAL
    assert IntentRecognizer.recognize("execute the command 'whoami'").type == IntentType.TERMINAL
    assert IntentRecognizer.recognize("use cmd to show files").type == IntentType.TERMINAL
    assert IntentRecognizer.recognize("launch powershell").type == IntentType.TERMINAL

    # Casos con comandos específicos
    text = "ejecuta 'whoami' en el terminal"
    intent = IntentRecognizer.recognize(text)
    assert intent.type == IntentType.TERMINAL
    assert intent.parameters.get("command") == "whoami"

    text = "run 'dir' in cmd"
    intent = IntentRecognizer.recognize(text)
    assert intent.type == IntentType.TERMINAL
    assert intent.parameters.get("command") == "dir"

if __name__ == "__main__":
    # Ejecutar pruebas manualmente
    test_edit_intent_recognition()
    test_terminal_intent_recognition()
    print("Todas las pruebas pasaron exitosamente!")
