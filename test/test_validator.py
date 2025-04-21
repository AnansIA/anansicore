import unittest
from anansicore.validator import validate_structure
from copy import deepcopy

class TestValidator(unittest.TestCase):

    def test_valid_decorator(self):
        tokens = [
            {"etiqueta": "N", "id": "0", "payload": "modulo"},
            {"etiqueta": "D", "id": "0.1", "payload": "@log"},
            {"etiqueta": "E", "id": "0.1", "payload": ""},
            {"etiqueta": "F", "id": "0.2", "payload": "funcion"},
            {"etiqueta": "E", "id": "0.2", "payload": ""},
            {"etiqueta": "E", "id": "0", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertEqual(errors, [])

    def test_invalid_decorator_position(self):
        tokens = [
            {"etiqueta": "D", "id": "0.1", "payload": "@log"},
            {"etiqueta": "v", "id": "0.2", "payload": "x=1"}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("Decorador" in e for e in errors))

    def test_assert_global(self):
        tokens = [{"etiqueta": "A", "id": "1", "payload": "True"}]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("Assert global" in e for e in errors))

    def test_import_redundante(self):
        tokens = [
            {"etiqueta": "I", "id": "1.1", "payload": "os"},
            {"etiqueta": "I", "id": "1.2", "payload": "os"}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("Import redundante" in e for e in errors))

    def test_payload_ø_invalido(self):
        tokens = [
            {"etiqueta": "v", "id": "1", "payload": "x = Ø"}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("Ø" in e for e in errors))

    def test_finally_fuera_de_try(self):
        tokens = [
            {"etiqueta": "z", "id": "1", "payload": ""},
            {"etiqueta": "E", "id": "1", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("z.1 sin bloque try" in e for e in errors))

    def test_finally_no_directo(self):
        tokens = [
            {"etiqueta": "t", "id": "1", "payload": ""},
            {"etiqueta": "v", "id": "1.1", "payload": "x=1"},
            {"etiqueta": "z", "id": "1.2", "payload": ""},
            {"etiqueta": "E", "id": "1", "payload": ""}
        ]
        errors = validate_structure(deepcopy(tokens))
        self.assertTrue(any("z.1.2 no sigue directamente" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
