import unittest
from validator import validate_structure
from copy import deepcopy

class TestValidator(unittest.TestCase):
    # Tests existentes (se mantienen igual)
    # ...

    # Nuevos tests complejos
    def test_complex_nested_blocks(self):
        tokens = [
            {"etiqueta": "N", "id": "1", "payload": "modulo"},
            {"etiqueta": "F", "id": "1.1", "payload": "funcion_externa"},
                {"etiqueta": "l", "id": "1.1.1", "payload": "while True"},
                    {"etiqueta": "i", "id": "1.1.1.1", "payload": "condicion"},
                        {"etiqueta": "t", "id": "1.1.1.1.1", "payload": ""},
                            {"etiqueta": "d", "id": "1.1.1.1.1.1", "payload": "llamada_riesgosa()"},
                        {"etiqueta": "x", "id": "1.1.1.1.2", "payload": "Exception"},
                            {"etiqueta": "r", "id": "1.1.1.1.2.1", "payload": "None"},
                        {"etiqueta": "z", "id": "1.1.1.1.3", "payload": ""},
                            {"etiqueta": "d", "id": "1.1.1.1.3.1", "payload": "cleanup()"},
                        {"etiqueta": "E", "id": "1.1.1.1", "payload": ""},
                    {"etiqueta": "E", "id": "1.1.1", "payload": ""},
                {"etiqueta": "E", "id": "1.1", "payload": ""},
            {"etiqueta": "E", "id": "1", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertEqual(errors, [])

    def test_invalid_nested_break(self):
        tokens = [
            {"etiqueta": "i", "id": "1", "payload": "condicion"},
                {"etiqueta": "l", "id": "1.1", "payload": "while True"},
                    {"etiqueta": "b", "id": "1.1.1", "payload": ""},
                {"etiqueta": "E", "id": "1.1", "payload": ""},
                {"etiqueta": "b", "id": "1.2", "payload": ""},  # Break fuera de loop
            {"etiqueta": "E", "id": "1", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("fuera de contexto de loop" in e for e in errors))

    def test_multiple_decorators(self):
        tokens = [
            {"etiqueta": "D", "id": "1", "payload": "@decorador1"},
            {"etiqueta": "D", "id": "2", "payload": "@decorador2(arg)"},
            {"etiqueta": "F", "id": "3", "payload": "funcion_decorada"},
            {"etiqueta": "E", "id": "3", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertEqual(errors, [])

    def test_complex_try_structure(self):
        tokens = [
            {"etiqueta": "t", "id": "1", "payload": ""},
                {"etiqueta": "d", "id": "1.1", "payload": "operacion_riesgosa()"},
                {"etiqueta": "x", "id": "1.2", "payload": "ErrorTipo1"},
                    {"etiqueta": "r", "id": "1.2.1", "payload": "fallback1"},
                {"etiqueta": "x", "id": "1.3", "payload": "ErrorTipo2"},
                    {"etiqueta": "r", "id": "1.3.1", "payload": "fallback2"},
                {"etiqueta": "z", "id": "1.4", "payload": ""},
                    {"etiqueta": "d", "id": "1.4.1", "payload": "limpiar()"},
                {"etiqueta": "E", "id": "1", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertEqual(errors, [])

    def test_invalid_finally_position(self):
        tokens = [
            {"etiqueta": "t", "id": "1", "payload": ""},
                {"etiqueta": "v", "id": "1.1", "payload": "x = 1"},
                {"etiqueta": "z", "id": "1.2", "payload": ""},  # Finally antes de except
                {"etiqueta": "x", "id": "1.3", "payload": "Exception"},
            {"etiqueta": "E", "id": "1", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("no sigue directamente" in e for e in errors))

    def test_class_with_methods(self):
        tokens = [
            {"etiqueta": "C", "id": "1", "payload": "MiClase"},
                {"etiqueta": "D", "id": "1.1", "payload": "@property"},
                {"etiqueta": "m", "id": "1.2a", "payload": "metodo"},
                    {"etiqueta": "r", "id": "1.2.1", "payload": "valor"},
                {"etiqueta": "E", "id": "1.2a", "payload": ""},
                {"etiqueta": "D", "id": "1.3", "payload": "@decorador"},
                {"etiqueta": "m", "id": "1.4a", "payload": "metodo_estatico"},
                {"etiqueta": "E", "id": "1.4a", "payload": ""},
            {"etiqueta": "E", "id": "1", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertEqual(errors, [])

    def test_orphaned_id_complex(self):
        tokens = [
            {"etiqueta": "F", "id": "1", "payload": "funcion"},
                {"etiqueta": "v", "id": "1.2", "payload": "x = 1"},  # Falta 1.1
            {"etiqueta": "E", "id": "1", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("ID huérfano" in e for e in errors))

    def test_global_assert_with_flag(self):
        tokens = [
            {"etiqueta": "A", "id": "1", "payload": "condicion", "static_assert": True},
            {"etiqueta": "N", "id": "2", "payload": "modulo"},
            {"etiqueta": "E", "id": "2", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertFalse(any("Assert global" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
