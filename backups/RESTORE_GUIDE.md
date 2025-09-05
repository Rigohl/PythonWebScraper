# RESTORE_GUIDE

Ubicación de los backups:

- `backups/snapshots/` : snapshots de carpetas completas, nombradas por fecha `YYYY-MM-DD_HH-MM-SS`.
- `backups/files/` : archivos sueltos de respaldo (scripts, notas, dumps).

Cómo restaurar:

1. Para restaurar una carpeta snapshot completa:
   - Copia la carpeta deseada desde `backups/snapshots/<timestamp>/` a la ubicación objetivo, por ejemplo:

     ```powershell
     Copy-Item -Path "backups\snapshots\2025-08-29_09-28-47\*" -Destination "src_backup_restore" -Recurse
     ```

2. Para restaurar un archivo suelto:
   - Copia el archivo desde `backups/files/` a la ubicación deseada.

Notas:

- Este repositorio mantiene backups dentro del árbol solo por conveniencia. Para producción, considera mover backups a almacenamiento externo (S3, Azure Blob, etc.) y mantener solo índices en el repo.
- Recomendación: verificar el contenido del backup después de restaurarlo.

Contacto:

- Si no estás seguro de qué restaurar, crea una issue o consulta al responsable del proyecto antes de sobreescribir archivos en el árbol principal.
