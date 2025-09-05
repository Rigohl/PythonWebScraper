#!/usr/bin/env python3
# Read the file
with open("src/tui/professional_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the problematic function and remove everything after it
lines = content.split("\n")
clean_lines = []
for line in lines:
    if "async def run_professional_app():" in line:
        break
    clean_lines.append(line)

# Write back the clean content
with open("src/tui/professional_app.py", "w", encoding="utf-8") as f:
    f.write("\n".join(clean_lines))
    f.write("\n\n# Función de entrada para mantener compatibilidad\n")
    f.write("async def run_professional_app():\n")
    f.write('    """Ejecuta la aplicación profesional"""\n')
    f.write("    app = WebScraperProfessionalApp()\n")
    f.write("    await app.run_async()\n")

print("Completely rewrote the end of professional_app.py")
