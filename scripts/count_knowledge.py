import re


def count_knowledge_items():
    """Cuenta el número real de elementos de conocimiento."""

    file_path = r"c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\autonomous_learning.py"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar patrones de tuplas de conocimiento
    # Formato: ("category", "topic", "content", confidence)
    pattern = r'\(\s*"[^"]+"\s*,\s*"[^"]+"\s*,\s*"[^"]+"\s*,\s*[\d.]+\s*\)'

    matches = re.findall(pattern, content)

    print(f"Elementos de conocimiento encontrados: {len(matches)}")

    # También contar las categorías diferentes
    category_pattern = r'\(\s*"([^"]+)"\s*,'
    categories = set(re.findall(category_pattern, content))

    print(f"Categorías únicas: {len(categories)}")
    print("Categorías encontradas:")
    for cat in sorted(categories):
        cat_count = len(re.findall(rf'\(\s*"{cat}"\s*,', content))
        print(f"  - {cat}: {cat_count} elementos")

    return len(matches)


if __name__ == "__main__":
    total_items = count_knowledge_items()

    if total_items >= 150:
        print("\n🎉 BASE DE CONOCIMIENTO: MASIVAMENTE EXPANDIDA")
    elif total_items >= 70:
        print("\n✅ BASE DE CONOCIMIENTO: EXPANDIDA")
    elif total_items >= 30:
        print("\n⚠️  BASE DE CONOCIMIENTO: PARCIAL")
    else:
        print("\n❌ BASE DE CONOCIMIENTO: INSUFICIENTE")
