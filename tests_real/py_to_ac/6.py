class Calculadora:
    def __init__(self):
        self.memoria = 0

    def sumar(self, x, y):
        if x == 0:
            return y
        else:
            return x + y

    def contar(self, n):
        for i in range(n):
            print(i)

