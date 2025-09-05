# Robots & Ethical Crawling Policy (Draft)

## 1. Objetivo

Definir pautas mínimas para un crawling responsable y configurable.

## 2. Robots.txt

- Flag runtime: `settings.ROBOTS_ENABLED` (default: False para desarrollo).
- Cuando se active: descargar `robots.txt`, cachear en memoria y respetar `Disallow`/`Allow` para `settings.USER_AGENT`.
- Fallback: si timeout o error => tratar como permitido pero registrar advertencia.

## 3. Meta Etiquetas y Directivas HTTP (Pendiente)

- Detectar `<meta name="robots" content="noindex,nofollow">` para marcar página como NO-INDEX (metadato en DB futuro).
- Responder a cabeceras `X-Robots-Tag`.

## 4. Límites de Frecuencia

- Backoff adaptativo por dominio ya presente (anomaly detection / RL). Añadir hard‑limit configurable (REQ).

## 5. Exclusiones Éticas Placeholder

- Heurística actual: evita rutas con `/login`, `/logout`, `/admin`, `/account`.
- Evolución: lista configurable + clasificación ML sensible a formularios / paneles privados.

## 6. Protección de Datos / PII

- Sin extracción activa de PII. Añadir futura fase de clasificación y redacción (redaction) antes de export público.

## 7. Uso de LLM

- `OFFLINE_MODE=True` evita salida de datos hacia APIs externas.
- Al activar modo online: sólo enviar fragmentos de contenido principal, nunca cookies, ni identificadores personales.

## 8. Registro y Transparencia

- Loggear decisiones de bloqueo (robots, ética) a nivel WARNING para auditoría.

## 9. Futuras Extensiones

| Tema | Descripción | Prioridad |
|------|-------------|-----------|
| Rate Limit Persistente | Persistir último fetch por dominio y calcular next allowed | Media |
| Política de Redacción | Identificar y enmascarar PII | Alta |
| Consent Tracking | Registrar aceptación de términos si existiera | Baja |
| Cache robots.txt | Almacenar TTL y respetar expiración | Media |
