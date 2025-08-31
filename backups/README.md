# Backups

Este directorio centraliza los backups y snapshots del proyecto.

Estructura:

- `backups/snapshots/` : snapshots de carpetas completas, nombradas por fecha `YYYY-MM-DD_HH-MM-SS`.
- `backups/files/` : archivos sueltos de respaldo (scripts, notas, dumps).

Archivos útiles:

- `RESTORE_GUIDE.md` : guía de restauración.
- `cleanup_backups.ps1` : script interactivo para eliminar backups antiguos.

Recomendaciones:

- Mover backups antiguos a almacenamiento externo (S3, Azure Blob) si se necesita conservar historial largo.
- Mantener `backups/` fuera del historial de producción si ocupa mucho espacio.
