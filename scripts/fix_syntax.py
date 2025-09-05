#!/usr/bin/env python3
# Read the correct ending
with open("correct_ending.txt", "r", encoding="utf-8") as f:
    correct_ending = f.read()

# Read the original file
with open("src/tui/professional_app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the line before the problematic function
cutoff_line = None
for i, line in enumerate(lines):
    if "# Función de entrada para mantener compatibilidad" in line:
        cutoff_line = i
        break

if cutoff_line is not None:
    # Keep everything before the problematic section
    with open("src/tui/professional_app.py", "w", encoding="utf-8") as f:
        for line in lines[:cutoff_line]:
            f.write(line)
        f.write("\n" + correct_ending + "\n")

    print("Fixed professional_app.py with correct ending")
else:
    print("Could not find the cutoff point")
