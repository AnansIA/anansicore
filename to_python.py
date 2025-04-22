from parser import parse_tokens_by_line
from anansicore.from_anansi import tokens_to_ast

with open("code/data/ejemplo_valido.txt") as f:
    tokens = parse_tokens_by_line(f.read())

ast_tree = tokens_to_ast(tokens)

for fn in ast_tree:
    print(fn.to_python())

