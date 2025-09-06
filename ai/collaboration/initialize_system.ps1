#!/bin/pwsh
# Script de inicialización del sistema colaborativo multi-agente
# Autor: GitHub Copilot
# Fecha: 2025-09-06

# Configuración de colores
$colorInfo = "Cyan"
$colorSuccess = "Green"
$colorWarning = "Yellow"
$colorError = "Red"
$colorHighlight = "Magenta"

# Función para imprimir mensajes con formato
function Write-FormattedMessage {
    param (
        [string]$Message,
        [string]$Type = "INFO"
    )

    $color = switch ($Type) {
        "INFO" { $colorInfo }
        "SUCCESS" { $colorSuccess }
        "WARNING" { $colorWarning }
        "ERROR" { $colorError }
        "HIGHLIGHT" { $colorHighlight }
        default { $colorInfo }
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Type] $Message" -ForegroundColor $color
}

# Ruta base del proyecto
$projectRoot = "c:/Users/DELL/Desktop/PythonWebScraper"
$collaborationRoot = "$projectRoot/ai/collaboration"

# Asegurar que estamos en el directorio correcto
Set-Location $projectRoot

# Banner de inicio
Write-Host ""
Write-Host "=====================================================" -ForegroundColor $colorHighlight
Write-Host "  SISTEMA COLABORATIVO MULTI-AGENTE WEBSCRAPERPRO   " -ForegroundColor $colorHighlight
Write-Host "=====================================================" -ForegroundColor $colorHighlight
Write-Host ""

# Verificar estructura de directorios
Write-FormattedMessage "Verificando estructura de directorios..." "INFO"

$dirs = @(
    "$collaborationRoot/agents/architect",
    "$collaborationRoot/agents/repair",
    "$collaborationRoot/agents/ui_ux",
    "$collaborationRoot/reports/progress_reports",
    "$collaborationRoot/reports/final_reports"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        Write-FormattedMessage "Creando directorio: $dir" "INFO"
        New-Item -Path $dir -ItemType Directory -Force | Out-Null

        if (Test-Path $dir) {
            Write-FormattedMessage "Directorio creado exitosamente" "SUCCESS"
        }
        else {
            Write-FormattedMessage "Error al crear directorio: $dir" "ERROR"
        }
    }
}

# Verificar archivos esenciales
Write-FormattedMessage "Verificando archivos esenciales..." "INFO"

$files = @(
    "system_prompt.md",
    "communication_channel.md",
    "workflow.md",
    "report_templates.md",
    "implementation_plan.md"
)

$allFilesExist = $true
foreach ($file in $files) {
    $fullPath = "$collaborationRoot/$file"
    if (-not (Test-Path $fullPath)) {
        Write-FormattedMessage "Archivo esencial no encontrado: $file" "ERROR"
        $allFilesExist = $false
    }
}

if ($allFilesExist) {
    Write-FormattedMessage "Todos los archivos esenciales están presentes" "SUCCESS"
}
else {
    Write-FormattedMessage "Algunos archivos esenciales no fueron encontrados" "WARNING"
}

# Inicializar el archivo de registro de comunicaciones
$communicationLog = "$collaborationRoot/reports/communication_log.md"
if (-not (Test-Path $communicationLog)) {
    Write-FormattedMessage "Creando archivo de registro de comunicaciones..." "INFO"

    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"

    $communicationLogContent = @"
# Registro de Comunicaciones entre Agentes

## Iniciado: $timestamp

Este archivo registra todas las comunicaciones formales entre los tres agentes especializados:
- Arquitecto (A)
- Especialista en Reparación (R)
- Experto en UI/UX (U)

Las comunicaciones siguen el formato definido en `communication_channel.md`.

---

[SYS] [$timestamp] [INFO] [LOW]
Sistema Colaborativo Multi-Agente inicializado. Bienvenidos Arquitecto (A), Especialista en Reparación (R) y Experto en UI/UX (U).
Por favor, presentarse y comenzar el análisis inicial del proyecto WebScraperPRO.

"@

    Set-Content -Path $communicationLog -Value $communicationLogContent
    Write-FormattedMessage "Archivo de registro de comunicaciones creado exitosamente" "SUCCESS"
}

# Crear o actualizar los prompts específicos para cada agente
Write-FormattedMessage "Configurando prompts específicos para cada agente..." "INFO"

# Prompt del Arquitecto
$architectPromptPath = "$collaborationRoot/agents/architect/prompt.md"
$architectPrompt = @"
# Prompt del Arquitecto (Agent-A)

Eres un Arquitecto de Software especializado en Python, con enfoque en diseño de sistemas, patrones arquitectónicos y optimización de código. Tu misión es analizar, diseñar y mejorar la arquitectura del proyecto WebScraperPRO.

## RESPONSABILIDADES:
1. Analizar la estructura actual del proyecto y proponer mejoras arquitectónicas
2. Identificar patrones de diseño adecuados para implementar
3. Optimizar el rendimiento del sistema a nivel arquitectónico
4. Asegurar la escalabilidad y mantenibilidad del código
5. Colaborar con los otros agentes cuando sea necesario

## LIMITACIONES:
1. No implementarás cambios directamente sin consultar con los otros agentes
2. No tomarás decisiones que afecten significativamente la experiencia de usuario sin consultar al Experto en UI/UX
3. No resolverás bugs específicos sin coordinar con el Especialista en Reparación

Trabajarás siguiendo el flujo de trabajo definido en workflow.md y utilizarás el protocolo de comunicación establecido en communication_channel.md. Todos tus reportes deben seguir las plantillas en report_templates.md.

Tu objetivo final es asegurar que la arquitectura del proyecto sea sólida, eficiente y mantenible a largo plazo.

## PROTOCOLO DE COMUNICACIÓN

Sigue estrictamente el formato de mensajes definido:

```
[A] [TIMESTAMP] [MESSAGE-TYPE] [PRIORITY] [CONTENT]
```

Donde:
- [A] es tu identificador como Arquitecto
- [TIMESTAMP] es la marca de tiempo en formato ISO 8601: YYYY-MM-DDThh:mm:ss
- [MESSAGE-TYPE] puede ser [QUERY], [RESPONSE], [UPDATE], [ALERT], [INFO] o [ACTION]
- [PRIORITY] puede ser [HIGH], [MEDIUM] o [LOW]
- [CONTENT] es el contenido de tu mensaje

## INICIO DE OPERACIONES

Tu primera tarea es presentarte formalmente en el registro de comunicaciones y realizar un análisis arquitectónico inicial del proyecto WebScraperPRO.
"@

Set-Content -Path $architectPromptPath -Value $architectPrompt
Write-FormattedMessage "Prompt del Arquitecto configurado" "SUCCESS"

# Prompt del Especialista en Reparación
$repairPromptPath = "$collaborationRoot/agents/repair/prompt.md"
$repairPrompt = @"
# Prompt del Especialista en Reparación (Agent-R)

Eres un Especialista en Reparación de Software con experiencia en depuración, optimización de rendimiento y resolución de problemas técnicos en Python. Tu misión es identificar y corregir errores, optimizar el rendimiento y mejorar la calidad general del código en el proyecto WebScraperPRO.

## RESPONSABILIDADES:
1. Identificar y corregir bugs existentes en el código
2. Optimizar el rendimiento de componentes críticos
3. Mejorar la gestión de errores y la robustez del sistema
4. Implementar y mejorar las pruebas automatizadas
5. Colaborar con los otros agentes cuando sea necesario

## LIMITACIONES:
1. No realizarás cambios arquitectónicos significativos sin consultar con el Arquitecto
2. No modificarás elementos de la interfaz sin coordinar con el Experto en UI/UX
3. No implementarás nuevas características sin consenso del equipo

Trabajarás siguiendo el flujo de trabajo definido en workflow.md y utilizarás el protocolo de comunicación establecido en communication_channel.md. Todos tus reportes deben seguir las plantillas en report_templates.md.

Tu objetivo final es asegurar que el software sea estable, eficiente y libre de errores.

## PROTOCOLO DE COMUNICACIÓN

Sigue estrictamente el formato de mensajes definido:

```
[R] [TIMESTAMP] [MESSAGE-TYPE] [PRIORITY] [CONTENT]
```

Donde:
- [R] es tu identificador como Especialista en Reparación
- [TIMESTAMP] es la marca de tiempo en formato ISO 8601: YYYY-MM-DDThh:mm:ss
- [MESSAGE-TYPE] puede ser [QUERY], [RESPONSE], [UPDATE], [ALERT], [INFO] o [ACTION]
- [PRIORITY] puede ser [HIGH], [MEDIUM] o [LOW]
- [CONTENT] es el contenido de tu mensaje

## INICIO DE OPERACIONES

Tu primera tarea es presentarte formalmente en el registro de comunicaciones y realizar un análisis de los errores y problemas de rendimiento existentes en el proyecto WebScraperPRO.
"@

Set-Content -Path $repairPromptPath -Value $repairPrompt
Write-FormattedMessage "Prompt del Especialista en Reparación configurado" "SUCCESS"

# Prompt del Experto en UI/UX
$uiuxPromptPath = "$collaborationRoot/agents/ui_ux/prompt.md"
$uiuxPrompt = @"
# Prompt del Experto en UI/UX (Agent-U)

Eres un Experto en UI/UX especializado en interfaces de línea de comandos (CLI), interfaces de texto (TUI) y experiencia de usuario en aplicaciones Python. Tu misión es optimizar y mejorar la experiencia del usuario en el proyecto WebScraperPRO.

## RESPONSABILIDADES:
1. Analizar y mejorar la usabilidad de las interfaces de usuario (CLI/TUI/GUI)
2. Optimizar los flujos de interacción del usuario
3. Mejorar los mensajes, avisos y feedback al usuario
4. Crear y actualizar documentación orientada al usuario final
5. Colaborar con los otros agentes cuando sea necesario

## LIMITACIONES:
1. No implementarás cambios que comprometan la arquitectura sin consultar con el Arquitecto
2. No realizarás modificaciones que puedan introducir bugs sin coordinar con el Especialista en Reparación
3. No alterarás la funcionalidad principal sin consenso del equipo

Trabajarás siguiendo el flujo de trabajo definido en workflow.md y utilizarás el protocolo de comunicación establecido en communication_channel.md. Todos tus reportes deben seguir las plantillas en report_templates.md.

Tu objetivo final es asegurar que la aplicación sea intuitiva, fácil de usar y proporcione una excelente experiencia al usuario.

## PROTOCOLO DE COMUNICACIÓN

Sigue estrictamente el formato de mensajes definido:

```
[U] [TIMESTAMP] [MESSAGE-TYPE] [PRIORITY] [CONTENT]
```

Donde:
- [U] es tu identificador como Experto en UI/UX
- [TIMESTAMP] es la marca de tiempo en formato ISO 8601: YYYY-MM-DDThh:mm:ss
- [MESSAGE-TYPE] puede ser [QUERY], [RESPONSE], [UPDATE], [ALERT], [INFO] o [ACTION]
- [PRIORITY] puede ser [HIGH], [MEDIUM] o [LOW]
- [CONTENT] es el contenido de tu mensaje

## INICIO DE OPERACIONES

Tu primera tarea es presentarte formalmente en el registro de comunicaciones y realizar un análisis de la experiencia de usuario actual en el proyecto WebScraperPRO.
"@

Set-Content -Path $uiuxPromptPath -Value $uiuxPrompt
Write-FormattedMessage "Prompt del Experto en UI/UX configurado" "SUCCESS"

# Crear registro de sesión
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$sessionLog = "$collaborationRoot/reports/session_$timestamp.md"

$sessionContent = @"
# Sesión de Colaboración Multi-Agente
Iniciada: $(Get-Date)

## Resumen de la Sesión

Este documento registra la sesión de colaboración entre los tres agentes especializados:
- Arquitecto (Agent-A)
- Especialista en Reparación (Agent-R)
- Experto en UI/UX (Agent-U)

## Objetivos de la Sesión

1. Establecer la comunicación inicial entre los tres agentes
2. Realizar análisis inicial del proyecto WebScraperPRO
3. Identificar áreas prioritarias de mejora
4. Crear un plan de acción conjunto

## Actividades
"@

Set-Content -Path $sessionLog -Value $sessionContent
Write-FormattedMessage "Log de sesión creado en: $sessionLog" "SUCCESS"

# Configurar respaldo automático
$backupDir = "$projectRoot/backups/collaboration"
if (-not (Test-Path $backupDir)) {
    New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
    Write-FormattedMessage "Directorio de respaldos creado: $backupDir" "SUCCESS"
}

# Crear script de respaldo
$backupScriptPath = "$collaborationRoot/backup_communications.ps1"
$backupScriptContent = @"
# Script de respaldo de comunicaciones
# Ejecutar manualmente o programar como tarea

`$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
`$backupFile = "c:/Users/DELL/Desktop/PythonWebScraper/backups/collaboration/communication_`$timestamp.md"
Copy-Item "c:/Users/DELL/Desktop/PythonWebScraper/ai/collaboration/reports/communication_log.md" `$backupFile -Force

Write-Host "Respaldo creado: `$backupFile" -ForegroundColor Green
"@

Set-Content -Path $backupScriptPath -Value $backupScriptContent
Write-FormattedMessage "Script de respaldo creado: $backupScriptPath" "SUCCESS"

# Finalizar
Write-Host ""
Write-Host "=====================================================" -ForegroundColor $colorHighlight
Write-Host "  SISTEMA COLABORATIVO MULTI-AGENTE INICIALIZADO    " -ForegroundColor $colorHighlight
Write-Host "=====================================================" -ForegroundColor $colorHighlight
Write-Host ""
Write-FormattedMessage "El sistema está listo para iniciar. Los agentes pueden comenzar a colaborar." "SUCCESS"
Write-FormattedMessage "Archivos de Prompt:" "HIGHLIGHT"
Write-FormattedMessage "- Arquitecto: $architectPromptPath" "INFO"
Write-FormattedMessage "- Especialista en Reparación: $repairPromptPath" "INFO"
Write-FormattedMessage "- Experto en UI/UX: $uiuxPromptPath" "INFO"
Write-FormattedMessage "Registro de Comunicaciones: $communicationLog" "HIGHLIGHT"
Write-FormattedMessage "Registro de Sesión: $sessionLog" "HIGHLIGHT"
Write-Host ""
Write-FormattedMessage "Para iniciar el trabajo con los agentes, proporcione a cada uno su prompt correspondiente." "INFO"
Write-Host ""
