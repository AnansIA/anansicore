from anansi_ast import (
    AnFunction, AnReturn, AnStatement, AnPass,
    AnBreak, AnContinue, AnIf, AnLoop
)

def tokens_to_ast(tokens):
    functions = []
    current_fn = None
    current_if = None
    current_else = None
    loop_stack = []

    for token in tokens:
        e, i, p = token["etiqueta"], token["id"], token["payload"]

        if e == "F":
            if current_fn:
                fn = AnFunction(
                    name=current_fn["name"],
                    params=current_fn["params"],
                    body=current_fn["body"],
                    decorators=current_fn["decorators"]
                )
                functions.append(fn)
            current_fn = {
                "name": p,
                "params": [],
                "body": [],
                "decorators": []
            }

        elif e == "p" and current_fn:
            current_fn["params"].append(p)

        elif e == "r":
            stmt = AnReturn(p.strip("[]"))
            _add_stmt(current_fn, current_if, current_else, loop_stack, stmt)

        elif e == "d":
            stmt = AnStatement(p.strip("[]"))
            _add_stmt(current_fn, current_if, current_else, loop_stack, stmt)

        elif e == "-":
            stmt = AnPass()
            _add_stmt(current_fn, current_if, current_else, loop_stack, stmt)

        elif e == "b":
            stmt = AnBreak()
            _add_stmt(current_fn, current_if, current_else, loop_stack, stmt)

        elif e == "n":
            stmt = AnContinue()
            _add_stmt(current_fn, current_if, current_else, loop_stack, stmt)

        elif e == "i":
            current_if = {"id": i, "cond": p.strip("[]"), "body": [], "else": []}

        elif e == "e" and current_if:
            current_else = []

        elif e == "l":
            loop_stack.append({"id": i, "header": p.strip("[]"), "body": []})

        elif e == "E":
            if current_else is not None:
                current_fn["body"].append(AnIf(
                    cond=current_if["cond"],
                    body=current_if["body"],
                    else_body=current_else
                ))
                current_if = None
                current_else = None

            elif current_if:
                current_fn["body"].append(AnIf(
                    cond=current_if["cond"],
                    body=current_if["body"]
                ))
                current_if = None

            elif loop_stack and i.startswith(loop_stack[-1]["id"]):
                loop = loop_stack.pop()
                stmt = AnLoop(loop["header"], loop["body"])
                _add_stmt(current_fn, current_if, current_else, loop_stack, stmt)

            elif current_fn and i == current_fn["name"]:
                fn = AnFunction(
                    name=current_fn["name"],
                    params=current_fn["params"],
                    body=current_fn["body"],
                    decorators=current_fn["decorators"]
                )
                functions.append(fn)
                current_fn = None

    # Si queda alguna función abierta sin cerrar
    if current_fn:
        fn = AnFunction(
            name=current_fn["name"],
            params=current_fn["params"],
            body=current_fn["body"],
            decorators=current_fn["decorators"]
        )
        functions.append(fn)

    return functions


def _add_stmt(fn, current_if, current_else, loop_stack, stmt):
    if current_else is not None:
        current_else.append(stmt)
    elif current_if:
        current_if["body"].append(stmt)
    elif loop_stack:
        loop_stack[-1]["body"].append(stmt)
    elif fn:
        fn["body"].append(stmt)

