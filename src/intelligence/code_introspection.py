import ast
import os


class CodeIntrospectionEngine:
    """
    Engine para introspección del propio código: analiza la estructura de archivos,
    módulos, clases, funciones e imports para dotar de autoconciencia al cerebro.
    """

    def __init__(self, code_dir: str):
        self.code_dir = code_dir
        self.structure = {}

    def parse_directory(self) -> dict:
        """
        Recorre recursivamente el directorio de código y analiza cada .py.
        """
        for root, dirs, files in os.walk(self.code_dir):
            for filename in files:
                if filename.endswith(".py"):
                    path = os.path.join(root, filename)
                    parsed = self._parse_file(path)
                    if parsed is not None:
                        self.structure[path] = parsed
        return self.structure

    def _parse_file(self, path: str) -> dict:
        """
        Parse a single Python file y extrae nombres de clases, funciones e imports.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=path)
        except Exception:
            return None

        classes = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        functions = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        return {
            "classes": classes,
            "functions": functions,
            "imports": list(set(imports)),
        }
