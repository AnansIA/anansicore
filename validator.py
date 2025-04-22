from collections import defaultdict

def validate_structure(tokens):
    errores = []
    ids_vistos = set()
    block_stack = []

    block_etiquetas = {
        "F", "C", "m", "i", "l", "t", "w", "x", "z", "e"
    }

    for token in tokens:
        e = token["etiqueta"]
        i = token["id"]

        # 1. Verificar duplicado
        if i in ids_vistos:
            errores.append(f"ID duplicado: {i}")
        else:
            ids_vistos.add(i)

        # 2. Manejar apertura
        if e in block_etiquetas:
            block_stack.append((e, i))

        # 3. Cierre de bloque
        elif e == "E":
            if not block_stack:
                errores.append(f"Cierre sin bloque abierto: E.{i}")
                continue

            last_etq, last_id = block_stack.pop()

            if last_id != i:
                errores.append(f"Cierre incorrecto: E.{i} no coincide con {last_etq}.{last_id}")

    # 4. Revisar si quedan bloques abiertos
    for etq, bid in block_stack:
        errores.append(f"Falta cierre E.{bid} para {etq}.{bid}")

    return errores


