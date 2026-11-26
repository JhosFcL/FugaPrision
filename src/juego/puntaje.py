"""Control encapsulado del puntaje de la campaña."""


class Puntaje:
    def __init__(self):
        self.__valor = 0

    def get_valor(self):
        return self.__valor

    def sumar(self, cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 0:
            raise ValueError("La cantidad a sumar debe ser un entero no negativo.")
        self.__valor += cantidad

    def restaurar(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ValueError("El puntaje restaurado debe ser un entero no negativo.")
        self.__valor = valor

    def reiniciar(self):
        self.__valor = 0
