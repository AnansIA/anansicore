import ast
from ast import unparse

def python_to_anansi(source_code):
    tree = ast.parse(source_code)
    result = []

    for fn_idx, node in enumerate(tree.body):
        if not isinstance(node, ast.FunctionDef):
            continue

        fid = f"{fn_idx + 1}"
        result.append(f"F.{fid}:{node.name}")

        for i, arg in enumerate(node.args.args):
            result.append(f"| p.{fid}.{i+1}:{arg.arg}")

        # Contador para líneas internas
        stmt_id = len(node.args.args) + 1

        for stmt in node.body:
            result += parse_stmt(stmt, fid, str(stmt_id))
            stmt_id += 1

        result.append(f"| E.{fid}")
    return "\n".join(result)


def parse_stmt(stmt, fid, sid):
    lines = []

    if isinstance(stmt, ast.Return):
        expr = unparse(stmt.value) if stmt.value else ""
        lines.append(f"| r.{fid}.{sid}:[[{expr}]]")

    elif isinstance(stmt, ast.Expr):
        expr = unparse(stmt.value)
        lines.append(f"| d.{fid}.{sid}:[[{expr}]]")

    elif isinstance(stmt, ast.Pass):
        lines.append(f"| -.{fid}.{sid}:")

    elif isinstance(stmt, ast.Break):
        lines.append(f"| b.{fid}.{sid}:")

    elif isinstance(stmt, ast.Continue):
        lines.append(f"| n.{fid}.{sid}:")

    elif isinstance(stmt, ast.If):
        cond = unparse(stmt.test)
        lines.append(f"| i.{fid}.{sid}:[[{cond}]]")
        for j, sub in enumerate(stmt.body):
            sub_id = f"{sid}.{j+1}"
            lines += parse_stmt(sub, fid, sub_id)

        if stmt.orelse:
            lines.append(f"| e.{fid}.{sid}:")
            for k, sub in enumerate(stmt.orelse):
                sub_id = f"{sid}.e{k+1}"
                lines += parse_stmt(sub, fid, sub_id)

        lines.append(f"| E.{fid}.{sid}")

    elif isinstance(stmt, ast.For):
        header = f"for {unparse(stmt.target)} in {unparse(stmt.iter)}"
        lines.append(f"| l.{fid}.{sid}:[[{header}]]")
        for j, sub in enumerate(stmt.body):
            sub_id = f"{sid}.{j+1}"
            lines += parse_stmt(sub, fid, sub_id)
        lines.append(f"| E.{fid}.{sid}")

    elif isinstance(stmt, ast.While):
        cond = unparse(stmt.test)
        lines.append(f"| l.{fid}.{sid}:[[while {cond}]]")
        for j, sub in enumerate(stmt.body):
            sub_id = f"{sid}.{j+1}"
            lines += parse_stmt(sub, fid, sub_id)
        lines.append(f"| E.{fid}.{sid}")

    return lines

