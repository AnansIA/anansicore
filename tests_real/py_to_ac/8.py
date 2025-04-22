class Contador:
    def contar_pares(self, lista):
        for n in lista:
            if n % 2 == 0:
                print(f"{n} es par")
            else:
                continue

