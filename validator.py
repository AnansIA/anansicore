from collections import defaultdict

def validate_structure(tokens):
    errors = []
    seen_ids = set()
    open_blocks = []
    id_tree = defaultdict(set)
    current_decorators = []
    decoradores_pendientes = []
    global_level = True
    imports = defaultdict(set)
    imports_usados = {}
    tokens_by_id = {t["id"]: t for t in tokens}
    prev_token = None

    # Paso 1: validar unicidad y jerarquía
    for token in tokens:
        etiqueta = token["etiqueta"]
        id_ = token["id"]
        if id_ in seen_ids:
            errors.append(f"ID duplicado: {id_}")
        seen_ids.add(id_)

        partes = id_.split(".")
        for i in range(1, len(partes)):
            padre = ".".join(partes[:i])
            if padre not in seen_ids:
                errors.append(f"ID huérfano: {id_} requiere {padre}")
            id_tree[padre].add(id_)

    # Paso 2: validaciones semánticas
    seen_ids.clear()
    open_blocks.clear()
    current_decorators.clear()
    decoradores_pendientes.clear()
    global_level = True
    prev_token = None

    for token in tokens:
        etiqueta = token["etiqueta"]
        id_ = token["id"]
        payload = token["payload"]

        # v0.7: Validación 9 - Assert global no permitido
        if etiqueta == "A" and global_level and not token.get("static_assert", False):
            errors.append(f"Assert global no permitido en {id_}")

        # Validación de apertura/cierre de bloques
        if etiqueta != "E":
            open_blocks.append((etiqueta, id_))
        else:
            if not open_blocks:
                errors.append(f"Cierre sin bloque abierto: {id_}")
            else:
                tipo_abierto, id_abierto = open_blocks.pop()
                if id_abierto != id_:
                    errors.append(f"Cierre incorrecto: E.{id_} no coincide con {tipo_abierto}.{id_abierto}")

        # Validación 10: Import redundante
        if etiqueta == "I":
            modulos = [m.strip() for m in payload.split(",")]
            for m in modulos:
                if m in imports_usados:
                    errors.append(f"{id_} repite import de {m} (ya usado en {imports_usados[m]})")
                else:
                    imports_usados[m] = id_

        # Validación 4: b/n deben estar dentro de loop
        if etiqueta in {"b", "n"}:
            if not any(e[0] == "l" and id_.startswith(e[1]) for e in open_blocks):
                errors.append(f"{etiqueta}.{id_} fuera de contexto de loop")

        # Validación 5: z solo luego de t/x
        if etiqueta == "z":
            if not any(e[0] == "t" and id_.startswith(e[1]) for e in open_blocks):
                errors.append(f"z.{id_} sin bloque try correspondiente")
            if not prev_token or prev_token["etiqueta"] not in {"t", "x"}:
                errors.append(f"z.{id_} no sigue directamente a t/x")

        # Validación 6: Ø no puede estar fuera de return
        if "Ø" in payload and etiqueta != "r":
            errors.append(f"Uso inválido de símbolo reservado Ø en {etiqueta}.{id_}")

        # Validación 6b: return vacío sin Ø
        if etiqueta == "r" and not payload.strip():
            errors.append(f"Return vacío sin Ø en {id_}")

        # Validación 7: payload [[ ]] mal cerrado
        if payload.strip().startswith("[[") and not payload.strip().endswith("]]"):
            errors.append(f"Payload mal cerrado con [[ ]] en {etiqueta}.{id_}")
        if "]]" in payload and not payload.strip().endswith("]]"):
            errors.append(f"Secuencia ]] inválida sin cierre correcto en {etiqueta}.{id_}")

        # Validación 8: decoradores deben ir seguidos de F/C/m
        if etiqueta == "D":
            current_decorators.append(token)
        elif etiqueta in {"F", "C", "m"}:
            current_decorators.clear()
        elif etiqueta != "E" and current_decorators:
            decor_ids = [d["id"] for d in current_decorators]
            errors.append(f"Decorador(es) {decor_ids} sin F/m/C después")
            current_decorators.clear()

        # Validación 10b: import redundante en mismo scope
        if etiqueta == "I":
            módulos = [m.strip() for m in payload.split(",")]
            padre = ".".join(id_.split(".")[:-1])
            for mod in módulos:
                if mod in imports[padre]:
                    errors.append(f"Import redundante: {mod} en {id_}")
                imports[padre].add(mod)

        # Actualizar contexto global
        if etiqueta in {"F", "C", "N"}:
            global_level = False

        prev_token = token

    for etiqueta, id_ in open_blocks:
        errors.append(f"Falta cierre E.{id_} para {etiqueta}.{id_}")

    # Validación 7b: pass no puede tener payload ni hijos
    for token in tokens:
        if token["etiqueta"] == "-":
            if token["payload"].strip():
                errors.append(f"Token '-' con contenido no permitido en {token['id']}")
            if token["id"] in id_tree and id_tree[token["id"]]:
                errors.append(f"Token '-' no puede tener hijos: {token['id']} tiene {len(id_tree[token['id']])}")

    # Validación 8 (refuerzo): decoradores huérfanos al final
    if decoradores_pendientes:
        errors.append(f"Decorador(es) {decoradores_pendientes} sin F/m/C después")

    return errors

