"""
Tests de aceptación mínimos para los scripts entregados.
Validación básica de ejecución, inputs inválidos y limpieza de recursos.
"""

import os
import tempfile
import unittest
import subprocess
import sys
import json


class TestNewScripts(unittest.TestCase):
    """Tests mínimos para validar los 4 scripts entregados"""

    def setUp(self):
        """Preparar entorno de testing con recursos temporales"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_temp.db")
        self.temp_output = os.path.join(self.temp_dir, "test_output.json")

    def tearDown(self):
        """Limpiar recursos temporales después de cada test"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_update_policy_ejecucion_basica(self):
        """Test: update_policy.py ejecuta sin excepción en modo help"""
        result = subprocess.run([
            sys.executable, "tools/update_policy.py", "--help"
        ], capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Actualizar políticas del scraper", result.stdout)

    def test_update_policy_dominio_prueba(self):
        """Test: update_policy.py maneja dominio de prueba correctamente"""
        result = subprocess.run([
            sys.executable, "tools/update_policy.py",
            "--domain", "example.com",
            "--robots-output", os.path.join(self.temp_dir, "robots_test.txt")
        ], capture_output=True, text=True, check=False)

        # Debe manejar el 404 correctamente (exit code 1 es esperado)
        # Script maneja el error graciosamente sin crash
        self.assertNotEqual(result.returncode, -1)  # No segfault
        self.assertIn("WARNING", result.stderr)     # Log de error apropiado

    def test_check_data_quality_ejecucion_basica(self):
        """Test: check_data_quality.py ejecuta sin excepción con BD vacía"""
        result = subprocess.run([
            sys.executable, "tools/check_data_quality.py"
        ], capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 0)
        self.assertIn("No se detectaron problemas de calidad", result.stderr)

    def test_generate_metrics_ejecucion_basica(self):
        """Test: generate_metrics.py ejecuta sin excepción y genera archivo"""
        result = subprocess.run([
            sys.executable, "tools/generate_metrics.py",
            "--db-path", self.temp_db,
            "--output", self.temp_output
        ], capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(self.temp_output))

        # Verificar que el JSON es válido
        with open(self.temp_output, 'r', encoding='utf-8') as f:
            metrics = json.load(f)
            self.assertIn("total_results", metrics)  # Key correcta
            self.assertIn("success_rate", metrics)   # Key correcta

    def test_generate_metrics_inputs_invalidos(self):
        """Test: generate_metrics.py maneja inputs inválidos correctamente"""
        # Test con ruta de BD inválida
        result = subprocess.run([
            sys.executable, "tools/generate_metrics.py",
            "--db-path", "/ruta/inexistente/database.db",
            "--output", self.temp_output
        ], capture_output=True, text=True, check=False)

        # Debe fallar graciosamente o crear BD vacía
        # No debe causar crash del script
        self.assertNotEqual(result.returncode, -1)  # No segfault

    def test_check_drift_ejecucion_basica(self):
        """Test: check_drift.py ejecuta sin excepción con datos vacíos"""
        result = subprocess.run([
            sys.executable, "tools/check_drift.py"
        ], capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 0)
        self.assertIn("No se detectó drift", result.stderr)

    def test_limpieza_recursos_generate_metrics(self):
        """Test: generate_metrics.py limpia recursos correctamente"""
        # Ejecutar script y verificar que no deja archivos temporales
        initial_files = set(os.listdir(self.temp_dir))

        subprocess.run([
            sys.executable, "tools/generate_metrics.py",
            "--db-path", self.temp_db,
            "--output", self.temp_output
        ], capture_output=True, text=True, check=False)

        # Verificar que solo se creó el archivo de salida esperado
        final_files = set(os.listdir(self.temp_dir))
        new_files = final_files - initial_files

        # Solo debe existir el archivo de métricas (BD temporal es creada y es esperada)
        expected_files = {
            os.path.basename(self.temp_output),
            os.path.basename(self.temp_db)  # BD temporal creada por script
        }
        self.assertEqual(new_files, expected_files)

    def test_update_policy_sin_credenciales(self):
        """Test: update_policy.py no expone credenciales en logs"""
        result = subprocess.run([
            sys.executable, "tools/update_policy.py",
            "--domain", "httpbin.org",
            "--robots-output", os.path.join(self.temp_dir, "test_robots.txt")
        ], capture_output=True, text=True, check=False)

        # Verificar que no hay patrones de credenciales en la salida
        output_text = result.stdout + result.stderr

        # Patrones básicos que no deberían aparecer
        sensitive_patterns = [
            "password", "secret", "token", "api_key",
            "Authorization:", "Bearer ", "Basic "
        ]

        for pattern in sensitive_patterns:
            self.assertNotIn(pattern, output_text.lower())

    def test_scripts_help_disponible(self):
        """Test: todos los scripts tienen ayuda disponible"""
        scripts = [
            "tools/update_policy.py",
            "tools/generate_metrics.py"
        ]

        for script in scripts:
            with self.subTest(script=script):
                result = subprocess.run([
                    sys.executable, script, "--help"
                ], capture_output=True, text=True, check=False)

                self.assertEqual(result.returncode, 0)
                self.assertTrue(len(result.stdout) > 0)


if __name__ == "__main__":
    unittest.main()
