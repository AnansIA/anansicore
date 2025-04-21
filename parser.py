from lark import Lark, Transformer, v_args, Tree, Token
from pathlib import Path
from validator import validate_structure
import json
import sys
from pprint import pprint

# Cargar gramática
grammar_path = Path(__file__).parent / "grammar.lark"
with open(grammar_path, encoding="utf-8") as f:
    grammar = f.read()

# Crear parser de un solo token (por línea)
parser = Lark(grammar, start="token", parser="lalr")

@v_args(inline=True)
class TokenTransformer(Transformer):
    def token(self, etiqueta, *rest):
        id_ = rest[1]
        raw_payload = rest[3] if len(rest) == 4 else ""

        if isinstance(raw_payload, Tree) and raw_payload.data == "empty":
            payload = ""
        elif isinstance(raw_payload, Tree):
            payload = "".join(str(t) for t in raw_payload.children)
        else:
            payload = str(raw_payload)

        return {
            "etiqueta": str(etiqueta),
            "id": str(id_),
            "payload": payload.strip()
        }

def parse_tokens_by_line(text):
    transformer = TokenTransformer()
    tokens = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tree = parser.parse(line)
        token = transformer.transform(tree)
        tokens.append(token)
    return tokens

def modificar_payload(tokens, etiqueta, id_target, nuevo_payload):
    cambios = 0
    for token in tokens:
        if token['etiqueta'] == etiqueta and token['id'] == id_target:
            token['payload'] = nuevo_payload
            cambios += 1
    return cambios

def token_a_linea(token):
    base = f"{token['etiqueta']}.{token['id']}"
    return f"{base}:{token['payload']}" if token['payload'] else f"{base}:"

# === CLI ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python parser.py archivo.txt [-o salida.json]")
        print("  python parser.py archivo.json --edit r.1.2 '[[nuevo_payload]]'")
        print("  python parser.py archivo.json --txt salida.txt")
        sys.exit(1)

    entrada = sys.argv[1]

    # Edición
    if "--edit" in sys.argv:
        edit_index = sys.argv.index("--edit")
        id_completo = sys.argv[edit_index + 1]
        nuevo_payload = sys.argv[edit_index + 2]

        if '.' not in id_completo:
            print("El ID debe tener formato tipo r.1.2")
            sys.exit(1)

        etiqueta, id_simple = id_completo.split(".", 1)
        with open(entrada, encoding="utf-8") as f:
            tokens = json.load(f)

        cambios = modificar_payload(tokens, etiqueta, id_simple, nuevo_payload)
        if cambios:
            with open(entrada, "w", encoding="utf-8") as f:
                json.dump(tokens, f, indent=2, ensure_ascii=False)
            print(f"✅ Editado: {cambios} token(s) con ID {id_completo}")
        else:
            print(f"⚠️ No se encontró ningún token con ID {id_completo}")
        sys.exit(0)

    # Exportar a .txt
    if "--txt" in sys.argv:
        txt_output_index = sys.argv.index("--txt")
        txt_output = sys.argv[txt_output_index + 1]
        if entrada.endswith(".json"):
            with open(entrada, encoding="utf-8") as f:
                tokens = json.load(f)
        else:
            with open(entrada, encoding="utf-8") as f:
                content = f.read()
            tokens = parse_tokens_by_line(content)

        with open(txt_output, "w", encoding="utf-8") as f:
            for t in tokens:
                f.write(f"| {token_a_linea(t)}\n")
        print(f"📄 Exportado como texto plano a {txt_output}")
        sys.exit(0)

    # Parsear y validar
    output_path = None
    if "-o" in sys.argv:
        output_index = sys.argv.index("-o")
        if output_index + 1 < len(sys.argv):
            output_path = sys.argv[output_index + 1]

    with open(entrada, encoding="utf-8") as f:
        content = f.read()

    tokens = parse_tokens_by_line(content)
    errors = validate_structure(tokens)

    if errors:
        print("❌ Errores de validación:")
        for e in errors:
            print(" -", e)
    else:
        print("✅ Estructura válida")

    pprint(tokens)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2, ensure_ascii=False)
        print(f"📦 Exportado a {output_path}")