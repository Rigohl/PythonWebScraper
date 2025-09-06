#!/bin/bash
# ========================================
# Web Scraper PRO - Launcher Principal
# ========================================

set -e

echo
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                         WEB SCRAPER PRO v1.0                            ║"
echo "║                    Launcher Principal Unificado                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo

# Verificar directorio correcto
if [ ! -f "src/main.py" ]; then
    echo "[ERROR] No se encuentra src/main.py. Asegúrate de ejecutar desde la raíz del proyecto."
    exit 1
fi

# Activar entorno virtual si existe
if [ -f ".venv/bin/activate" ]; then
    echo "[INFO] Activando entorno virtual..."
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    echo "[INFO] Activando entorno virtual alternativo..."
    source venv/bin/activate
else
    echo "[WARNING] No se encontró entorno virtual. Usando Python del sistema..."
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python no está instalado."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Función para mostrar el menú
show_menu() {
    echo
    echo "┌─────────────────────────────────────────────────────────────────────────┐"
    echo "│                            MENÚ PRINCIPAL                               │"
    echo "├─────────────────────────────────────────────────────────────────────────┤"
    echo "│  1. Ejecutar Panel Profesional (TUI Pro)                               │"
    echo "│  2. Modo Demo (Sin Playwright)                                         │"
    echo "│  3. Crawlear URL específica                                            │"
    echo "│  4. Exportar datos a CSV                                               │"
    echo "│  5. Exportar datos a JSON                                              │"
    echo "│  6. Instalar/Actualizar dependencias                                   │"
    echo "│  7. Ejecutar tests                                                      │"
    echo "│  8. Ver estadísticas de BD                                             │"
    echo "│  9. Limpiar caché y archivos temporales                               │"
    echo "│ 10. Multi-terminal: Verificar archivos, estudiar documentos, continuar │"
    echo "│  0. Salir                                                               │"
    echo "└─────────────────────────────────────────────────────────────────────────┘"
    echo
}

# Función para ejecutar terminales en paralelo
run_multi_terminal() {
    echo
    echo "[INFO] Iniciando ejecución multi-terminal para procesar tareas en paralelo..."

    # Verificar disponibilidad de terminal
    if ! command -v gnome-terminal &> /dev/null && ! command -v konsole &> /dev/null && ! command -v xterm &> /dev/null; then
        echo "[ERROR] No se encontró ninguna terminal gráfica (gnome-terminal, konsole o xterm)."
        echo "[INFO] Ejecutando en modo secuencial como alternativa."

        echo
        echo "--- Terminal 1: Verificación de archivos ---"
        echo "[INFO] Verificando archivos del proyecto..."
        find . -type f -name "*.py" -o -name "*.md" -o -name "*.txt" | head -10
        echo

        echo "--- Terminal 2: Análisis de documentación ---"
        if [ -f "README.md" ]; then
            echo "[INFO] Analizando README.md..."
            grep "^##" README.md | sort
        else
            echo "[WARN] No se encontró README.md."
        fi
        echo

        echo "--- Terminal 3: Ejecución demo rápida ---"
        echo "[INFO] Ejecutando modo demo para validación rápida..."
        $PYTHON_CMD -m src.main --demo
        echo

        return
    fi

    # Determinar qué terminal usar
    TERMINAL_CMD=""
    if command -v gnome-terminal &> /dev/null; then
        TERMINAL_CMD="gnome-terminal"
    elif command -v konsole &> /dev/null; then
        TERMINAL_CMD="konsole"
    elif command -v xterm &> /dev/null; then
        TERMINAL_CMD="xterm"
    fi

    # Terminal 1: Verificación de archivos
    echo "[INFO] Lanzando Terminal 1: Verificación del sistema..."
    $TERMINAL_CMD -- bash -c "echo 'Terminal 1: Verificación del sistema'; echo '[INFO] Verificando archivos del proyecto...'; find . -type f -name '*.py' -o -name '*.md' -o -name '*.txt' | wc -l; echo; echo '[INFO] Mostrando estructura del proyecto:'; find . -maxdepth 1 -type d | grep -v '^\.$'; echo; read -p 'Presiona Enter para cerrar...'" &

    # Terminal 2: Análisis de documentación
    echo "[INFO] Lanzando Terminal 2: Análisis de documentación..."
    $TERMINAL_CMD -- bash -c "echo 'Terminal 2: Análisis de documentación'; echo '[INFO] Analizando documentación del proyecto...'; if [ -f 'README.md' ]; then grep '^##' README.md | sort; else echo '[WARN] No se encontró README.md.'; fi; echo; echo '[INFO] Resumen de archivos de configuración:'; find . -path './config/*.*' -o -name '*.toml' -o -name '*.yaml'; echo; read -p 'Presiona Enter para cerrar...'" &

    # Terminal 3: Ejecución demo
    echo "[INFO] Lanzando Terminal 3: Ejecución demo rápida..."
    $TERMINAL_CMD -- bash -c "echo 'Terminal 3: Ejecución demo rápida'; echo '[INFO] Ejecutando modo demo para validación rápida...'; cd '$(pwd)'; if [ -f '.venv/bin/activate' ]; then source .venv/bin/activate; elif [ -f 'venv/bin/activate' ]; then source venv/bin/activate; fi; $PYTHON_CMD -m src.main --demo; echo; read -p 'Presiona Enter para cerrar...'" &

    echo "[INFO] 3 terminales lanzados en paralelo."
    echo "[INFO] Esto permite ejecutar comandos simultáneamente para acelerar el flujo de trabajo."
    echo
}

# Loop principal
while true; do
    show_menu
    read -p "Selecciona una opción (0-10): " choice

    case $choice in
        1)
            echo
            echo "[INFO] Iniciando Panel Profesional (TUI Pro)..."
            if ! $PYTHON_CMD -m src.main --tui-pro; then
               echo "[WARN] Fallback a TUI clásica..."
               $PYTHON_CMD -m src.main --tui || echo "[ERROR] Ambas interfaces fallaron."
            fi
            echo "[INFO] Sesión TUI finalizada."
            read -p "Presiona Enter para continuar..."
            ;;
        2)
            echo
            echo "[INFO] Ejecutando en modo demo..."
            $PYTHON_CMD -m src.main --demo
            read -p "Presiona Enter para continuar..."
            ;;
        3)
            echo
            read -p "Introduce la URL a crawlear: " url
            if [ -z "$url" ]; then
                echo "[ERROR] URL no puede estar vacía."
                read -p "Presiona Enter para continuar..."
                continue
            fi
            echo "[INFO] Iniciando crawleo de $url..."
            $PYTHON_CMD -m src.main --crawl "$url"
            read -p "Presiona Enter para continuar..."
            ;;
        4)
            echo
            echo "[INFO] Exportando datos a CSV..."
            mkdir -p exports
            $PYTHON_CMD -m src.main --export-csv "exports/scrape_results_$(date +%Y-%m-%d).csv"
            echo "[INFO] Exportación completada."
            read -p "Presiona Enter para continuar..."
            ;;
        5)
            echo
            echo "[INFO] Exportando datos a JSON..."
            mkdir -p exports
            $PYTHON_CMD -m src.main --export-json "exports/scrape_results_$(date +%Y-%m-%d).json"
            echo "[INFO] Exportación completada."
            read -p "Presiona Enter para continuar..."
            ;;
        6)
            echo
            echo "[INFO] Instalando/actualizando dependencias..."
            pip install -r requirements.txt
            echo "[INFO] Instalando navegadores de Playwright..."
            $PYTHON_CMD -m playwright install
            echo "[INFO] Instalación completada."
            read -p "Presiona Enter para continuar..."
            ;;
        7)
            echo
            echo "[INFO] Ejecutando suite de tests con cobertura..."
            if [ -f "config/pytest.ini" ]; then
                $PYTHON_CMD -m pytest -c config/pytest.ini tests/ -v --cov=src --cov-report=term-missing
            else
                $PYTHON_CMD -m pytest tests/ -v --cov=src --cov-report=term-missing
            fi
            echo "[INFO] Verificando también tests de inteligencia..."
            export HYBRID_BRAIN=1  # Activar para tests de inteligencia
            export TEST_MODE=1     # Modo test para comportamiento específico
            $PYTHON_CMD -m pytest tests/test_*intelligence*.py tests/test_*brain*.py tests/test_*learning*.py -v
            read -p "Presiona Enter para continuar..."
            ;;
        8)
            echo
            echo "[INFO] Generando estadísticas de base de datos..."
            $PYTHON_CMD scripts/check_data_quality.py
            $PYTHON_CMD scripts/generate_metrics.py
            read -p "Presiona Enter para continuar..."
            ;;
        9)
            echo
            echo "[INFO] Limpiando archivos temporales y caché..."
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -name "*.pyc" -delete 2>/dev/null || true
            rm -rf .pytest_cache 2>/dev/null || true
            rm -f test_*.db* 2>/dev/null || true
            echo "[INFO] Limpieza completada."
            read -p "Presiona Enter para continuar..."
            ;;
        10)
            run_multi_terminal
            read -p "Presiona Enter para continuar..."
            ;;
        0)
            echo
            echo "[INFO] ¡Gracias por usar Web Scraper PRO!"
            exit 0
            ;;
        *)
            echo "[ERROR] Opción no válida. Inténtalo de nuevo."
            read -p "Presiona Enter para continuar..."
            ;;
    esac
done
