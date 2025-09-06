"""
Este archivo contiene el código para agregar al final de professional_app.py.
"""


async def _process_edit_intent(
    self, file_path: str, old_content: str, new_content: str, log: TextLog
):
    """Procesa la intención de editar un archivo.

    Args:
        file_path: Ruta del archivo a editar
        old_content: Contenido actual que se reemplazará
        new_content: Nuevo contenido
        log: TextLog para mostrar información
    """
    import os

    if not file_path:
        log.write("[red]⛔ No se especificó un archivo para editar[/]")
        return

    # Verificar si es una ruta relativa (sin / o \)
    if not any(c in file_path for c in ["/", "\\"]):
        # Verificar en directorios comunes
        common_dirs = ["src", "docs", "config", "data", "."]
        found_path = None

        for directory in common_dirs:
            if os.path.exists(os.path.join(directory, file_path)):
                found_path = os.path.join(directory, file_path)
                break

        if found_path:
            file_path = found_path

    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        log.write(f"[red]⛔ No se encontró el archivo: {file_path}[/]")
        return

    # Por seguridad, verificar extensión
    safe_extensions = [".py", ".md", ".txt", ".html", ".css", ".json", ".csv", ".log"]
    if not any(file_path.lower().endswith(ext) for ext in safe_extensions):
        log.write(
            f"[red]⛔ Por seguridad, solo se permiten editar archivos con extensiones: {', '.join(safe_extensions)}[/]"
        )
        return

    try:
        # Leer el archivo
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if old_content and new_content:
            # Reemplazar contenido específico
            if old_content not in content:
                log.write(
                    f"[red]⛔ No se encontró el contenido a reemplazar en {file_path}[/]"
                )
                return

            new_file_content = content.replace(old_content, new_content)

            # Verificar que se hizo un cambio
            if new_file_content == content:
                log.write("[yellow]⚠️ No se realizaron cambios en el archivo[/]")
                return

            # Escribir el nuevo contenido
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_file_content)

            log.write(f"[green]✅ Se reemplazó texto en {file_path}[/]")

        elif new_content:
            # Agregar contenido al final del archivo
            with open(file_path, "a", encoding="utf-8") as f:
                f.write("\n" + new_content)

            log.write(f"[green]✅ Se agregó contenido al final de {file_path}[/]")

        else:
            # Mostrar contenido del archivo
            preview = content[:500] + "..." if len(content) > 500 else content
            log.write(f"[bold cyan]📄 Contenido de {file_path}:[/]\n{preview}")

    except Exception as e:
        log.write(f"[red]⛔ Error al editar el archivo: {e}[/]")


async def _process_terminal_intent(self, command: str, log: TextLog):
    """Procesa la intención de ejecutar un comando en terminal.

    Args:
        command: Comando a ejecutar
        log: TextLog para mostrar información
    """
    import re
    import subprocess
    import sys

    if not command:
        log.write("[red]⛔ No se especificó un comando para ejecutar[/]")
        return

    # Lista de comandos peligrosos a bloquear
    dangerous_commands = [
        "rm -rf",
        "deltree",
        "format",
        "> /dev/null",
        "del /s",
        "del /q",
        "shutdown",
        "reboot",
        ":(){:|:&};:",
        "dd",
        "chmod -R 777",
        "wipe",
        "mkfs",
        "fdisk",
        "dd if=/dev/zero",
        "overwrite",
        "fork bomb",
    ]

    # Verificar comandos peligrosos
    if any(
        re.search(re.escape(cmd), command, re.IGNORECASE) for cmd in dangerous_commands
    ):
        log.write(
            "[red]⛔ Comando potencialmente peligroso detectado. Ejecución bloqueada.[/]"
        )
        return

    # Verificar que solo se ejecuten comandos seguros o informativos
    safe_command_prefixes = [
        "echo",
        "dir",
        "ls",
        "pwd",
        "cd",
        "type",
        "cat",
        "more",
        "less",
        "find",
        "where",
        "whoami",
        "hostname",
        "ipconfig",
        "ifconfig",
        "ver",
        "python -V",
        "pip list",
        "pip freeze",
        "date",
        "time",
        "systeminfo",
        "free",
        "df",
        "du",
        "ps",
        "tasklist",
        "netstat",
        "ping",
        "tracert",
        "traceroute",
        "nslookup",
        "git status",
        "git branch",
        "python --version",
        "pip --version",
        "npm list",
        "npm --version",
        "node --version",
        "help",
    ]

    if not any(
        command.lower().startswith(prefix.lower()) for prefix in safe_command_prefixes
    ):
        log.write(
            f"[yellow]⚠️ Por seguridad, solo se permiten comandos informativos o de lectura.[/]"
        )
        log.write(f"[yellow]Comandos permitidos: {', '.join(safe_command_prefixes)}[/]")
        return

    try:
        log.write(f"[cyan]🖥️ Ejecutando: {command}[/]")

        # Determinar el shell a usar
        is_windows = sys.platform.startswith("win")
        shell_cmd = "powershell.exe" if is_windows else "/bin/bash"
        shell_param = ["-Command"] if is_windows else ["-c"]

        # Ejecutar el comando
        process = subprocess.Popen(
            [shell_cmd] + shell_param + [command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(timeout=10)

        if stdout:
            log.write(f"[green]📤 Salida:[/]\n{stdout[:1000]}")

        if stderr:
            log.write(f"[red]⚠️ Error:[/]\n{stderr[:1000]}")

        if process.returncode != 0:
            log.write(
                f"[yellow]⚠️ El comando terminó con código de salida: {process.returncode}[/]"
            )

    except subprocess.TimeoutExpired:
        log.write("[red]⛔ Tiempo de espera agotado para el comando[/]")
    except Exception as e:
        log.write(f"[red]⛔ Error al ejecutar el comando: {e}[/]")
