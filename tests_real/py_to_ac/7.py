def operar_archivo(nombre):
    try:
        with open(nombre) as f:
            for linea in f:
                print(linea)
    except FileNotFoundError:
        print("Archivo no encontrado")
    finally:
        print("Operación terminada")

