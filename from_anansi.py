from anansi_ast import AnFunction, AnReturn, AnStatement, AnIf

def tokens_to_ast(tokens):
    functions = []
    current_fn = None
    body = []
    params = []
    decorators = []

    ifs_abiertos = []
    for token in tokens:
        e, i, p = token["etiqueta"], token["id"], token["payload"]
        if e == "i":
            current_if = {"id": i, "cond": p.strip("[]"), "body": []}
            ifs_abiertos.append(current_if)

        elif e == "r" and ifs_abiertos:
            ifs_abiertos[-1]["body"].append(AnReturn(p.strip("[]")))

        elif e == "d" and ifs_abiertos:
            ifs_abiertos[-1]["body"].append(AnStatement(p.strip("[]")))

        elif e == "E" and ifs_abiertos and i.startswith(ifs_abiertos[-1]["id"]):
            cerrado = ifs_abiertos.pop()
            current_fn["body"].append(AnIf(cerrado["cond"], cerrado["body"]))

        if e == "D":
            decorators.append(p.lstrip("@"))
        elif e == "F":
            current_fn = {"name": p, "params": [], "body": [], "decorators": decorators}
            decorators = []
        elif e == "p":
            current_fn["params"].append(p)
        elif e == "r":
            if p == "Ø":
                current_fn["body"].append(AnReturn(""))
            else:
                payload = p.strip("[]")
                current_fn["body"].append(AnReturn(payload))
        elif e == "E" and current_fn:
            fn = AnFunction(
                name=current_fn["name"],
                params=current_fn["params"],
                body=current_fn["body"],
                decorators=current_fn["decorators"]
            )
            functions.append(fn)
            current_fn = None

        elif e == "d":
            payload = p.strip("[]")
            current_fn["body"].append(AnStatement(payload))
        elif e == "i":
            current_if = {"id": i, "cond": p.strip("[]"), "body": []}
        elif e == "r" and current_if:
            current_if["body"].append(AnReturn(p.strip("[]")))
        elif e == "d" and current_if:
            current_if["body"].append(AnStatement(p.strip("[]")))
        elif e == "E" and current_if and i.startswith(current_if["id"]):
            current_fn["body"].append(AnIf(current_if["cond"], current_if["body"]))
            current_if = None




    return functions

