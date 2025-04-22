import ast
from ast import unparse

def python_to_anansi(source_code):
    tree = ast.parse(source_code)
    result = []

    for top_idx, node in enumerate(tree.body):
        if isinstance(node, ast.FunctionDef):
            result += serialize_function(node, fid=str(top_idx + 1))

        elif isinstance(node, ast.ClassDef):
            cid = str(top_idx + 1)
            result.append(f"C.{cid}:{node.name}")
            for midx, method in enumerate(node.body):
                if isinstance(method, ast.FunctionDef):
                    result += serialize_function(method, fid=f"{cid}.{midx + 1}", is_method=True)
            result.append(f"| E.{cid}")

    return "\n".join(result)


def serialize_function(node, fid, is_method=False):
    lines = []
    kind = "m" if is_method else "F"
    lines.append(f"{'| ' if is_method else ''}{kind}.{fid}:{node.name}")

    for i, arg in enumerate(node.args.args):
        lines.append(f"| p.{fid}.{i+1}:{arg.arg}")

    counter = [len(node.args.args) + 1]  # mutable counter

    for stmt in node.body:
        lines += parse_stmt(stmt, fid, counter)

    if counter[0] == len(node.args.args) + 1:
        lines.append(f"| -.{fid}.{counter[0]}:")
        counter[0] += 1

    lines.append(f"| E.{fid}")
    return lines


def parse_stmt(stmt, fid, counter, sid=None):
    lines = []

    def next_id():
        val = counter[0]
        counter[0] += 1
        return f"{val}"

    def line(op, value=None, _sid=None):
        _sid = _sid or next_id()
        if value is None:
            lines.append(f"| {op}.{fid}.{_sid}:")
        else:
            lines.append(f"| {op}.{fid}.{_sid}:[[{value}]]")
        return _sid

    if isinstance(stmt, ast.Return):
        expr = unparse(stmt.value) if stmt.value else "Ø"
        line("r", expr, sid)

    elif isinstance(stmt, ast.Expr):
        line("d", unparse(stmt.value), sid)

    elif isinstance(stmt, ast.Assign):
        line("v", unparse(stmt), sid)

    elif isinstance(stmt, ast.Pass):
        line("-", None, sid)

    elif isinstance(stmt, ast.Break):
        line("b", None, sid)

    elif isinstance(stmt, ast.Continue):
        line("n", None, sid)

    elif isinstance(stmt, ast.Assert):
        line("A", unparse(stmt.test), sid)

    elif isinstance(stmt, ast.Raise):
        value = unparse(stmt.exc) if stmt.exc else ""
        line("T", value, sid)

    elif isinstance(stmt, ast.With):
        sid_local = line("w", unparse(stmt.items[0]), sid)
        for sub in stmt.body:
            lines += parse_stmt(sub, fid, counter, sid=f"{sid_local}.{next_id()}")
        lines.append(f"| E.{fid}.{sid_local}")

    elif isinstance(stmt, ast.Try):
        sid_local = line("t", None, sid)
        for sub in stmt.body:
            lines += parse_stmt(sub, fid, counter, sid=f"{sid_local}.{next_id()}")

        for handler in stmt.handlers:
            name = handler.name or ""
            if handler.type:
                header = f"{unparse(handler.type)} as {name}" if name else unparse(handler.type)
            else:
                header = "Exception"
            x_id = line("x", header, sid=f"{sid_local}.{next_id()}")
            for sub in handler.body:
                lines += parse_stmt(sub, fid, counter, sid=f"{x_id}.{next_id()}")

        if stmt.finalbody:
            z_id = line("z", None, sid=f"{sid_local}.{next_id()}")
            for sub in stmt.finalbody:
                lines += parse_stmt(sub, fid, counter, sid=f"{z_id}.{next_id()}")

        lines.append(f"| E.{fid}.{sid_local}")

    elif isinstance(stmt, ast.If):
        sid_local = line("i", unparse(stmt.test), sid)
        for sub in stmt.body:
            lines += parse_stmt(sub, fid, counter, sid=f"{sid_local}.{next_id()}")

        if stmt.orelse:
            e_id = line("e", None, sid=sid_local)
            for sub in stmt.orelse:
                lines += parse_stmt(sub, fid, counter, sid=f"{sid_local}.{next_id()}")

        lines.append(f"| E.{fid}.{sid_local}")

    elif isinstance(stmt, ast.For):
        header = f"for {unparse(stmt.target)} in {unparse(stmt.iter)}"
        sid_local = line("l", header, sid)
        for sub in stmt.body:
            lines += parse_stmt(sub, fid, counter, sid=f"{sid_local}.{next_id()}")
        lines.append(f"| E.{fid}.{sid_local}")

    elif isinstance(stmt, ast.While):
        sid_local = line("l", f"while {unparse(stmt.test)}", sid)
        for sub in stmt.body:
            lines += parse_stmt(sub, fid, counter, sid=f"{sid_local}.{next_id()}")
        lines.append(f"| E.{fid}.{sid_local}")

    return lines

