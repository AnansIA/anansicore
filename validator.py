from collections import defaultdict

def validate_structure(tokens):
    errors = []
    seen_ids = set()
    open_blocks = []

    # Etiquetas que abren un bloque y requieren cierre con E.X
    block_etiquetas = {"F", "C", "m", "i", "l", "t", "w", "x", "z", "e"}

    for token in tokens:
        etiqueta = token["etiqueta"]
        id_ = token["id"]
        payload = token.get("payload", "")

        # 1. Detectar duplicados exactos
        full_id = f"{etiqueta}.{id_}"
        if full_id in seen_ids:
            errors.append(f"ID duplicado: {id_}")
        seen_ids.add(full_id)

        # 2. Abertura de bloque
        if etiqueta in block_etiquetas:
            open_blocks.append((etiqueta, id_))

        # 3. Cierre de bloque
        elif etiqueta == "E":
            if not open_blocks:
                errors.append(f"Cierre sin bloque abierto: {id_}")
                continue

            match = None
            # buscar bloque a cerrar, permitiendo cierres fuera de orden inmediato
            for i in reversed(range(len(open_blocks))):
                _, opened_id = open_blocks[i]
                if opened_id == id_:
                    match = i
                    break

            if match is not None:
                open_blocks.pop(match)
            else:
                tipo_esperado, id_esperado = open_blocks[-1]
                errors.append(f"Cierre incorrecto: E.{id_} no coincide con {tipo_esperado}.{id_esperado}")

        # 4. Casos especiales
        if etiqueta == "r" and payload.strip() == "":
            errors.append(f"Return vacío sin Ø en {id_}")
        if etiqueta == "-" and payload.strip():
            errors.append(f"Token '-' con contenido no permitido en {id_}")
        if etiqueta == "-" and any(t["id"].startswith(id_ + ".") for t in tokens):
            errors.append(f"Token '-' no puede tener hijos: {id_} tiene hijos")

        # 5. Validación de payload (chequeo mínimo)
        if "[[" in payload and "]]" not in payload:
            errors.append(f"Payload mal cerrado con [[ ]] en {etiqueta}.{id_}")
        if "]]" in payload and "[[" not in payload:
            errors.append(f"Payload mal cerrado con [[ ]] en {etiqueta}.{id_}")

    # 6. Bloques abiertos que nunca se cerraron
    for tipo, id_abierto in open_blocks:
        errors.append(f"Falta cierre E.{id_abierto} para {tipo}.{id_abierto}")

    return errors

