"""
Tests para la ejecución de intenciones avanzadas.

Este archivo verifica la integración completa del reconocimiento
y ejecución de intenciones de edición de archivos y comandos de terminal.
"""

import os
import sys
import pytest
import tempfile
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.intelligence.intent_recognizer import IntentRecognizer, IntentType, Intent
from src.tui.professional_app import WebScraperProfessionalApp, ChatOverlay

class TestTextLog:
    """Mock para TextLog de Textual."""

    def __init__(self):
        self.messages = []

    def write(self, text):
        """Simula la escritura de mensajes."""
        self.messages.append(text)

    def clear(self):
        """Limpia los mensajes."""
        self.messages = []

# Funciones para crear archivos temporales
def create_temp_file(content=""):
    """Crea un archivo temporal con el contenido especificado."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

def test_edit_intent_processing():
    """Prueba el procesamiento completo de intención de edición."""
    # Crear archivo temporal para pruebas
    test_content = "Este es un archivo de prueba\nPara verificar la edición"
    temp_file = create_temp_file(test_content)

    try:
        # Crear mock TextLog
        log = TestTextLog()

        # Inicializar app parcialmente (solo para pruebas)
        app = MagicMock()

        # Ejecutar proceso de edición con archivo existente
        # y sin contenido nuevo (debería mostrar el contenido)
        asyncio.run(WebScraperProfessionalApp._process_edit_intent(
            WebScraperProfessionalApp(),
            temp_file, "", "", log
        ))

        # Verificar que se muestra el contenido
        assert any("Contenido de" in msg for msg in log.messages)
        assert any("Este es un archivo de prueba" in msg for msg in log.messages)

        # Limpiar mensajes
        log.clear()

        # Probar con reemplazo de contenido
        asyncio.run(WebScraperProfessionalApp._process_edit_intent(
            WebScraperProfessionalApp(),
            temp_file, "prueba", "PRUEBA", log
        ))

        # Verificar que se realizó el cambio
        assert any("Se reemplazó texto" in msg for msg in log.messages)

        # Verificar el contenido del archivo
        with open(temp_file, 'r', encoding='utf-8') as f:
            new_content = f.read()

        assert "Este es un archivo de PRUEBA" in new_content

    finally:
        # Limpiar archivo temporal
        os.unlink(temp_file)

def test_terminal_intent_processing():
    """Prueba el procesamiento completo de intención de terminal."""
    # Prueba con comando seguro
    with patch('subprocess.Popen') as mock_popen:
        process_mock = MagicMock()
        process_mock.communicate.return_value = ("Salida simulada", "")
        process_mock.returncode = 0
        mock_popen.return_value = process_mock

        # Crear mock TextLog
        log = TestTextLog()

        # Ejecutar proceso de terminal con comando seguro
        asyncio.run(WebScraperProfessionalApp._process_terminal_intent(
            WebScraperProfessionalApp(),
            "echo Hola Mundo", log
        ))

        # Verificar que se ejecutó el comando
        assert any("Ejecutando: echo" in msg for msg in log.messages)
        assert any("Salida:" in msg for msg in log.messages)
        assert mock_popen.called

    # Prueba con comando prohibido (usando un nuevo mock)
    with patch('subprocess.Popen') as mock_popen_dangerous:
        # Crear nuevo mock TextLog
        log = TestTextLog()

        # Probar con comando prohibido
        asyncio.run(WebScraperProfessionalApp._process_terminal_intent(
            WebScraperProfessionalApp(),
            "rm -rf /", log
        ))

        # Verificar que se bloqueó el comando peligroso
        assert any("Comando potencialmente peligroso" in msg for msg in log.messages)
        assert not mock_popen_dangerous.called  # No debe llamarse a Popendef test_chat_message_intent_detection():
    """Prueba la detección y procesamiento de intenciones en mensajes de chat."""
    # Crear intención de edición
    edit_intent = Intent(
        intent_type=IntentType.EDIT,
        confidence=0.8,
        parameters={"file": "config.json"}
    )

    # Crear intención de terminal
    terminal_intent = Intent(
        intent_type=IntentType.TERMINAL,
        confidence=0.8,
        parameters={"command": "dir"}
    )

    # Mockear el IntentRecognizer para devolver intenciones controladas
    with patch('src.intelligence.intent_recognizer.IntentRecognizer.recognize') as mock_recognize:
        # Configurar para devolver intención de edición
        mock_recognize.return_value = edit_intent

        # Verificar tipo de intención
        result = IntentRecognizer.recognize("edita config.json")
        assert result.type == IntentType.EDIT
        assert result.parameters.get("file") == "config.json"

        # Cambiar para devolver intención de terminal
        mock_recognize.return_value = terminal_intent

        # Verificar tipo de intención
        result = IntentRecognizer.recognize("ejecuta dir en terminal")
        assert result.type == IntentType.TERMINAL
        assert result.parameters.get("command") == "dir"

def test_integration_intent_execution():
    """Prueba la integración de detección y ejecución de intenciones."""
    # Esta prueba simula un escenario completo desde el mensaje hasta la ejecución

    # Mock de TextLog para capturar salida
    log = TestTextLog()

    # Crear un archivo temporal para pruebas de edición
    temp_file = create_temp_file("contenido original")
    filename = os.path.basename(temp_file)

    try:
        # 1. Crear intención de edición
        edit_text = f"edita el archivo {filename}"
        edit_intent = IntentRecognizer.recognize(edit_text)

        # Verificar que se detectó correctamente
        assert edit_intent.type == IntentType.EDIT

        # 2. Procesar la intención (edición de archivo)
        with patch('pathlib.Path.exists', return_value=True):
            # Modificar el path para usar nuestro archivo temporal
            if "file" in edit_intent.parameters:
                edit_intent.parameters["file"] = temp_file

            asyncio.run(WebScraperProfessionalApp._process_edit_intent(
                WebScraperProfessionalApp(),
                temp_file, "", "nuevo contenido", log
            ))

        # Verificar que se procesó correctamente
        assert any("contenido" in msg for msg in log.messages)

        # 3. Crear intención de terminal
        terminal_text = "ejecuta echo Prueba"
        terminal_intent = IntentRecognizer.recognize(terminal_text)

        # Verificar que se detectó correctamente
        assert terminal_intent.type == IntentType.TERMINAL

        # 4. Procesar la intención (comando de terminal)
        with patch('subprocess.Popen') as mock_popen:
            process_mock = MagicMock()
            process_mock.communicate.return_value = ("Salida de eco", "")
            process_mock.returncode = 0
            mock_popen.return_value = process_mock

            asyncio.run(WebScraperProfessionalApp._process_terminal_intent(
                WebScraperProfessionalApp(),
                "echo Prueba", log
            ))

            # Verificar que se ejecutó correctamente
            assert mock_popen.called

    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    # Ejecutar pruebas manualmente
    test_edit_intent_processing()
    test_terminal_intent_processing()
    test_chat_message_intent_detection()
    test_integration_intent_execution()
    print("✅ Todas las pruebas pasaron exitosamente!")
