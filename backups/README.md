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

Cambios realizados (2025-08-31):

- Se reubicaron snapshots y backups sueltos desde la raíz del repositorio a esta carpeta `backups/snapshots/` y `backups/files/`.
- Se añadieron `RESTORE_GUIDE.md` y `cleanup_backups.ps1` para restauración y limpieza segura.
- Scripts legacy en la raíz fueron movidos y renombrados a `backups/files/backup_*`.

Próximos pasos recomendados:

- Decidir si `backups/` debe permanecer en el repo o añadirse a `.gitignore` y mover los snapshots a un almacenamiento externo.
- Si se elige externalizar, crear un script de migración para subir snapshots a S3/Azure y limpiar localmente.
