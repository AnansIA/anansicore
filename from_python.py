import ast 

def python_to_anansi(source_code):
    tree = ast.parse(source_code)

    result = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            fid = "1"
            result.append(f"F.{fid}:{node.name}")
            for i, arg in enumerate(node.args.args):
                result.append(f"| p.{fid}.{i+1}:{arg.arg}")
            for j, stmt in enumerate(node.body):
                line_id = len(node.args.args) + j + 1
                if isinstance(stmt, ast.Return):
                    expr = ast.unparse(stmt.value)
                    result.append(f"| r.{fid}.{line_id}:[[{expr}]]")
                elif isinstance(stmt, ast.Expr):
                    expr = ast.unparse(stmt.value)
                    result.append(f"| d.{fid}.{line_id}:[[{expr}]]")
                elif isinstance(stmt, ast.If):
                    cond = ast.unparse(stmt.test)
                    block_id = f"{fid}.{line_id}"
                    result.append(f"| i.{block_id}:[[{cond}]]")
                    for k, inner_stmt in enumerate(stmt.body):
                        sub_line = f"{block_id}.{k+1}"
                        if isinstance(inner_stmt, ast.Return):
                            inner_expr = ast.unparse(inner_stmt.value)
                            result.append(f"| r.{sub_line}:[[{inner_expr}]]")
                        elif isinstance(inner_stmt, ast.Expr):
                            expr = ast.unparse(inner_stmt.value)
                            result.append(f"| d.{sub_line}:[[{expr}]]")
                    result.append(f"| E.{block_id}")
            result.append(f"| E.{fid}")
    return "\n".join(result)
