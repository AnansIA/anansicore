from collections import defaultdict

def validate_structure(tokens):
    errors = []
    seen_ids = set()
    open_blocks = []
    id_tree = defaultdict(set)
    current_decorators = []
    global_level = True
    imports = defaultdict(set)
    prev_token = None

    # Paso 1: validar unicidad y jerarquía
    for token in tokens:
        etiqueta = token['etiqueta']
        id_ = token['id']
        if id_ in seen_ids:
            errors.append(f"ID duplicado: {id_}")
        seen_ids.add(id_)

        partes = id_.split(".")
        for i in range(1, len(partes)):
            padre = ".".join(partes[:i])
            if padre not in seen_ids:
                errors.append(f"ID huérfano: {id_} requiere {padre}")
            id_tree[padre].add(id_)

    # Paso 2: validar estructura y semántica
    seen_ids.clear()
    current_decorators = []
    open_blocks = []
    prev_token = None
    global_level = True

    for token in tokens:
        etiqueta = token['etiqueta']
        id_ = token['id']
        payload = token['payload']

        seen_ids.add(id_)

        if etiqueta not in {"E"}:
            open_blocks.append((etiqueta, id_))
        else:
            if not open_blocks:
                errors.append(f"Cierre sin bloque abierto: {id_}")
            else:
                tipo_abierto, id_abierto = open_blocks.pop()
                if id_abierto != id_:
                    errors.append(f"Cierre incorrecto: E.{id_} no coincide con {tipo_abierto}.{id_abierto}")

        if etiqueta in {"b", "n"}:
            if not any(e[0] == "l" and id_.startswith(e[1]) for e in open_blocks):
                errors.append(f"{etiqueta}.{id_} fuera de contexto de loop")

        if etiqueta == "z":
            if not any(e[0] == "t" and id_.startswith(e[1]) for e in open_blocks):
                errors.append(f"z.{id_} sin bloque try correspondiente")
            if not prev_token or prev_token['etiqueta'] not in {"t", "x"}:
                errors.append(f"z.{id_} no sigue directamente a t/x")

        if "Ø" in payload and etiqueta != "r":
            errors.append(f"Uso inválido de símbolo reservado Ø en {etiqueta}.{id_}")

        if etiqueta == "D":
            current_decorators.append(token)
        elif etiqueta in {"F", "m", "C"}:
            current_decorators = []
        elif etiqueta != "E" and current_decorators:
            decor_ids = [d['id'] for d in current_decorators]
            errors.append(f"Decorador(es) {decor_ids} sin F/m/C después")
            current_decorators = []

        if etiqueta == "A" and global_level and not token.get("static_assert", False):
            errors.append(f"Assert global no permitido: {id_}")

        if etiqueta == "I":
            módulos = [m.strip() for m in payload.split(',')]
            padre = ".".join(id_.split('.')[:-1])
            for mod in módulos:
                if mod in imports[padre]:
                    errors.append(f"Import redundante: {mod} en {id_}")
                imports[padre].add(mod)

        if etiqueta in {"F", "C", "N"}:
            global_level = False

        prev_token = token

    for etiqueta, id_ in open_blocks:
        errors.append(f"Falta cierre E.{id_} para {etiqueta}.{id_}")

    return errors

