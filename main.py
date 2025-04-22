from parser import parse_tokens_by_line
from from_anansi import tokens_to_ast
from from_python import python_to_anansi


with open("data/para_convertir.txt") as f:
    tokens = parse_tokens_by_line(f.read())

ast_tree = tokens_to_ast(tokens)

for fn in ast_tree:
    print(fn.to_python())


code = """
def saludar(nombre):
    print("Hola", nombre)
    return None
"""

print("\n🧠 Código Python original:")
print(code)

print("\n🪄 Convertido a AnansiCore:")
print(python_to_anansi(code))
