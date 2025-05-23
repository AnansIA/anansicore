import sys
from pathlib import Path
import difflib

BASE = Path("tests_real")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PY_DIR = BASE / "py_to_ac"
AC_DIR = BASE / "ac_back"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)

from parser import parse_tokens_by_line
from validator import validate_structure
from from_python import python_to_anansi
from from_anansi import tokens_to_ast


def normalize(text):
    lines = [line.strip().replace('"', "'") for line in text.strip().splitlines()]
    return "\n".join([line for line in lines if line])


def main():
    py_files = sorted(PY_DIR.glob("*.py"))

    for py_file in py_files:
        name = py_file.name
        print(f"\n🧪 Procesando: {name}")

        py_code = py_file.read_text(encoding="utf-8")

        try:
            anansi_code = python_to_anansi(py_code)
            print("\n🔁 Conversión a AnansiCore:")
            print(anansi_code)

            out_path = AC_DIR / (py_file.stem + ".anansi.txt")
            out_path.write_text(anansi_code, encoding="utf-8")

        except Exception as e:
            print(f"❌ Error al convertir a AnansiCore: {e}")
            continue

        try:
            # 🔧 ORDEN CORRECTO DE LÍNEAS ANTES DE PARSEAR
            lines = anansi_code.strip().splitlines()
            lines.sort(key=lambda line: line.split(":")[0].strip())
            sorted_anansi_code = "\n".join(lines)

            tokens = parse_tokens_by_line(sorted_anansi_code)
            errors = validate_structure(tokens)

            if errors:
                print("\n⚠ Errores de validación:")
                for err in errors:
                    print(" -", err)
                continue
            else:
                print("\n✅ Estructura válida.")

            ast = tokens_to_ast(tokens)
            regenerated = "\n".join(fn.to_python() for fn in ast)

            print("\n🔄 Reconstrucción desde Anansi AST:")
            print(regenerated)

            if normalize(py_code) == normalize(regenerated):
                print("\n🎉 Reconstrucción exacta.")
            else:
                print("\n❗ Diferencias entre original y reconstruido.")

        except Exception as e:
            print(f"❌ Error durante validación o reconstrucción: {e}")


if __name__ == "__main__":
    main()

