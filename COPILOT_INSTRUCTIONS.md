---
applyTo: "**"
---
# Custom Instructions (English / Español)

## Purpose / Propósito

Provide consistent architectural, security, and style guidance for GitHub Copilot Chat & Agents in this workspace.
Proveer una guía consistente de arquitectura, seguridad y estilo para Copilot en este workspace.

## Code Style / Estilo de Código

- Python: prefer explicit imports, type hints on public functions, no wildcard imports.
- Use dataclasses for simple data containers.
- Avoid premature optimization; prioritize clarity.
- Español: Preferir nombres descriptivos, evitar abreviaturas crípticas.

## Testing / Pruebas

- Always propose at least one unit test when generating new core logic.
- Use pytest style (fixtures > setup functions).
- Cover edge, nominal, and failure cases.
- Incluir ejemplos mínimos reproducibles.

## Security / Seguridad

- Never execute or auto-suggest destructive shell commands without explicit confirmation.
- Flag potential injections, command expansions, or unsafe eval patterns.
- Validar entradas externas antes de usar en consultas SQL o rutas.

## Documentation / Documentación

- Every new module: short top-level docstring (purpose + key responsibilities).
- Complex functions (>15 lines) get a doctring: params, returns, side-effects.
- En respuestas: si se modifica más de 1 archivo, enumerar cambios.

## Architecture / Arquitectura

- Keep separation: scraping logic, persistence, intent recognition, UI (Textual) isolated.
- Introduce abstractions only with ≥2 concrete implementations.
- Prefer composition over inheritance.

## Performance

- Only suggest async refactors if I/O bound hotspots are identified.
- Provide Big-O reasoning when proposing algorithmic changes.

## Prompting Guidance / Guía de Prompts

- If user prompt is ambiguous: ask 1 clarifying question; otherwise proceed.
- Provide 2-3 alternative improvement suggestions (short) at end of complex answers.
- Responder en el idioma del usuario salvo se pida otro.

## PowerShell / Terminal

- Never chain destructive commands with `;` or `&&` without justification.
- Always include `-WhatIf` suggestion for removal / destructive operations.

## Git / Version Control

- Group related changes per commit with concise imperative message.
- Reference issue / intent when applicable.

## Refactors

- Provide diff-style summary sections.
- Justify with: Problem → Change → Benefit.

## Non Goals / No Objetivos

- Do not introduce external heavy dependencies without approval.
- Do not auto-generate large boilerplate blocks unless requested.

## Output Quality / Calidad de Salida

- Prefer actionable steps lists over long paragraphs.
- Highlight risk areas with "RISK:" prefix.

## Compliance

- Respect project LICENSE & policies in `docs/`.

(End / Fin)
