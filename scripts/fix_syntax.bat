@echo off
python -c "
# Read the file and fix the syntax error
with open('src/tui/professional_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic function and fix it
lines = content.split('\n')
fixed_lines = []
in_problem_function = False

for i, line in enumerate(lines):
    if 'async def run_professional_app():' in line:
        in_problem_function = True
        fixed_lines.append('# Función de entrada para mantener compatibilidad')
        fixed_lines.append('async def run_professional_app():')
        fixed_lines.append('    \"\"\"Ejecuta la aplicación profesional\"\"\"')
        fixed_lines.append('    app = WebScraperProfessionalApp()')
        fixed_lines.append('    await app.run_async()')
        break
    else:
        fixed_lines.append(line)

# Write back the fixed content
with open('src/tui/professional_app.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print('Fixed syntax error in professional_app.py')
"
