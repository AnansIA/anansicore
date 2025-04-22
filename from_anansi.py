from anansi_ast import (
    AnFunction, AnMethod, AnClass,
    AnReturn, AnStatement, AnPass, AnBreak, AnContinue,
    AnIf, AnLoop, AnAssert, AnRaise, AnWith, AnTry, AnAssign, 
    AnLambda
)

def tokens_to_ast(tokens):
    functions = []
    current_fn = None
    current_if = None
    current_else = None
    loop_stack = []
    class_stack = []
    try_stack = []
    with_stack = []

    for token in tokens:
        e, i, p = token["etiqueta"], token["id"], token["payload"]

        if e == "C":
            class_stack.append({"id": i, "name": p, "methods": []})

        elif e == "m":
            current_fn = {"name": p, "params": [], "body": [], "decorators": [], "id": i, "is_method": True}

        elif e == "F":
            current_fn = {"name": p, "params": [], "body": [], "decorators": [], "id": i, "is_method": False}

        elif e == "p" and current_fn:
            current_fn["params"].append(p)

        elif e == "r":
            stmt = AnReturn(p.strip("[]"))
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "d":
            stmt = AnStatement(p.strip("[]"))
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "v":
            stmt = AnAssign(p.strip("[]"))
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "f":  # λ‑functions
            stmt = AnLambda(p.strip("[]"))
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "-":
            stmt = AnPass()
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "b":
            stmt = AnBreak()
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "n":
            stmt = AnContinue()
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "A":
            stmt = AnAssert(p.strip("[]"))
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "T":
            stmt = AnRaise(p.strip("[]"))
            _add_stmt(current_fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack)

        elif e == "i":
            current_if = {"id": i, "cond": p.strip("[]"), "body": [], "else": []}

        elif e == "e" and current_if:
            current_else = []

        elif e == "l":
            loop_stack.append({"id": i, "header": p.strip("[]"), "body": []})

        elif e == "w":
            with_stack.append({"id": i, "header": p.strip("[]"), "body": []})

        elif e == "t":
            try_stack.append({"id": i, "body": [], "handlers": [], "final": [], "in_final": False})

        elif e == "x" and try_stack:
            try_stack[-1]["handlers"].append({"header": p.strip("[]"), "body": []})

        elif e == "z" and try_stack:
            try_stack[-1]["in_final"] = True
            try_stack[-1]["final"] = []

        elif e == "E":
            # Cierre de IF
            if current_else is not None:
                stmt = AnIf(current_if["cond"], current_if["body"], current_else)
                current_else = None
                current_if = None
                _add_stmt(current_fn, stmt, current_if, None, loop_stack, try_stack, with_stack)
            elif current_if:
                stmt = AnIf(current_if["cond"], current_if["body"])
                current_if = None
                _add_stmt(current_fn, stmt, current_if, None, loop_stack, try_stack, with_stack)

            # Cierre de LOOP
            elif loop_stack and i.startswith(loop_stack[-1]["id"]):
                loop = loop_stack.pop()
                stmt = AnLoop(loop["header"], loop["body"])
                _add_stmt(current_fn, stmt, current_if, None, loop_stack, try_stack, with_stack)

            # Cierre de WITH
            elif with_stack and i.startswith(with_stack[-1]["id"]):
                blk = with_stack.pop()
                stmt = AnWith(blk["header"], blk["body"])
                _add_stmt(current_fn, stmt, current_if, None, loop_stack, try_stack, with_stack)

            # Cierre de TRY
            elif try_stack and i.startswith(try_stack[-1]["id"]):
                tr = try_stack.pop()
                stmt = AnTry(
                    body=tr["body"],
                    except_blocks=[(h["header"], h["body"]) for h in tr["handlers"]],
                    finally_body=tr["final"]
                )
                _add_stmt(current_fn, stmt, current_if, None, loop_stack, try_stack, with_stack)

            # Cierre de FUNCIÓN
            elif current_fn and i == current_fn["id"]:
                node_class = AnMethod if current_fn.get("is_method") else AnFunction
                fn = node_class(
                    name=current_fn["name"],
                    params=current_fn["params"],
                    body=current_fn["body"],
                    decorators=current_fn["decorators"]
                )
                if class_stack:
                    class_stack[-1]["methods"].append(fn)
                else:
                    functions.append(fn)
                current_fn = None

            # Cierre de CLASE
            elif class_stack and i == class_stack[-1]["id"]:
                class_obj = AnClass(
                    name=class_stack[-1]["name"],
                    methods=class_stack[-1]["methods"]
                )
                functions.append(class_obj)
                class_stack.pop()

    if current_fn:
        node_class = AnMethod if current_fn.get("is_method") else AnFunction
        fn = node_class(
            name=current_fn["name"],
            params=current_fn["params"],
            body=current_fn["body"],
            decorators=current_fn["decorators"]
        )
        functions.append(fn)

    return functions

def _add_stmt(fn, stmt, current_if, current_else, loop_stack, try_stack, with_stack):
    if current_else is not None:
        current_else.append(stmt)
    elif current_if:
        current_if["body"].append(stmt)
    elif loop_stack:
        loop_stack[-1]["body"].append(stmt)
    elif with_stack:
        with_stack[-1]["body"].append(stmt)
    elif try_stack:
        if try_stack[-1]["in_final"]:
            try_stack[-1]["final"].append(stmt)
        elif try_stack[-1]["handlers"]:
            try_stack[-1]["handlers"][-1]["body"].append(stmt)
        else:
            try_stack[-1]["body"].append(stmt)
    elif fn:
        fn["body"].append(stmt)

