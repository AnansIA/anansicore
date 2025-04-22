import ast
from ast import unparse

def python_to_anansi(source_code):
    tree = ast.parse(source_code)
    result = []

    for top_idx, node in enumerate(tree.body):
        fid = str(top_idx + 1)

        if isinstance(node, ast.FunctionDef):
            result += serialize_function(node, fid)

        elif isinstance(node, ast.ClassDef):
            result.append(f"C.{fid}:{node.name}")
            for midx, method in enumerate(node.body):
                if isinstance(method, ast.FunctionDef):
                    result += serialize_function(method, f"{fid}.{midx + 1}", is_method=True)
            result.append(f"| E.{fid}")

    return "\n".join(result)


def serialize_function(node, fid, is_method=False):
    kind = "m" if is_method else "F"
    lines = [f"{'| ' if is_method else ''}{kind}.{fid}:{node.name}"]

    for i, arg in enumerate(node.args.args, start=1):
        lines.append(f"| p.{fid}.{i}:{arg.arg}")

    base = len(node.args.args)
    lines += nest(fid, base, node.body)
    lines.append(f"| E.{fid}")
    return lines


def nest(fid, base_id, stmts):
    lines = []
    for idx, stmt in enumerate(stmts, start=1):
        sid = f"{base_id + idx}"
        lines += parse_stmt(stmt, fid, sid)
    return lines


def parse_stmt(stmt, fid, sid):
    lines = []

    def nest_block(stmts, prefix=""):
        return [line for i, s in enumerate(stmts, start=1) for line in parse_stmt(s, fid, f"{sid}.{prefix}{i}")]

    if isinstance(stmt, ast.Return):
        expr = unparse(stmt.value) if stmt.value else ""
        lines.append(f"| r.{fid}.{sid}:[[{expr}]]")

    elif isinstance(stmt, ast.Expr):
        lines.append(f"| d.{fid}.{sid}:[[{unparse(stmt.value)}]]")

    elif isinstance(stmt, ast.Pass):
        lines.append(f"| -.{fid}.{sid}:")

    elif isinstance(stmt, ast.Break):
        lines.append(f"| b.{fid}.{sid}:")

    elif isinstance(stmt, ast.Continue):
        lines.append(f"| n.{fid}.{sid}:")

    elif isinstance(stmt, ast.Assert):
        lines.append(f"| A.{fid}.{sid}:[[{unparse(stmt.test)}]]")

    elif isinstance(stmt, ast.Raise):
        expr = unparse(stmt.exc) if stmt.exc else ""
        lines.append(f"| T.{fid}.{sid}:[[{expr}]]")

    elif isinstance(stmt, ast.Assign):
        target = unparse(stmt.targets[0])
        value = unparse(stmt.value)
        if value.startswith("lambda"):
            lines.append(f"| v.{fid}.{sid}:[[{target} = {value}]]")
        else:
            lines.append(f"| d.{fid}.{sid}:[[{target} = {value}]]")

    elif isinstance(stmt, ast.If):
        cond = unparse(stmt.test)
        lines.append(f"| i.{fid}.{sid}:[[{cond}]]")
        lines += nest_block(stmt.body)
        if stmt.orelse:
            lines.append(f"| e.{fid}.{sid}:")
            lines += nest_block(stmt.orelse, "2")
        lines.append(f"| E.{fid}.{sid}")

    elif isinstance(stmt, ast.For):
        head = f"for {unparse(stmt.target)} in {unparse(stmt.iter)}"
        lines.append(f"| l.{fid}.{sid}:[[{head}]]")
        lines += nest_block(stmt.body)
        lines.append(f"| E.{fid}.{sid}")

    elif isinstance(stmt, ast.While):
        head = f"while {unparse(stmt.test)}"
        lines.append(f"| l.{fid}.{sid}:[[{head}]]")
        lines += nest_block(stmt.body)
        lines.append(f"| E.{fid}.{sid}")

    elif isinstance(stmt, ast.With):
        lines.append(f"| w.{fid}.{sid}:[[{unparse(stmt.items[0])}]]")
        lines += nest_block(stmt.body)
        lines.append(f"| E.{fid}.{sid}")

    elif isinstance(stmt, ast.Try):
        lines.append(f"| t.{fid}.{sid}:")
        lines += nest_block(stmt.body)
        for handler in stmt.handlers:
            header = f"| x.{fid}.{sid}:[[{unparse(handler.type)}]]" if handler.type else f"| x.{fid}.{sid}:"
            lines.append(header)
            lines += nest_block(handler.body)
        if stmt.finalbody:
            lines.append(f"| z.{fid}.{sid}:")
            lines += nest_block(stmt.finalbody)
        lines.append(f"| E.{fid}.{sid}")

    return lines

