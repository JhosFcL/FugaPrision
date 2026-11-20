"""Representa las paredes de un escenario a partir de un plano de texto."""
from pygame import Rect


TAMANO_CELDA = 40


class Mapa:
    def __init__(self, plano):
        if not plano or not plano[0]:
            raise ValueError("El plano no puede estar vacío.")

        columnas = len(plano[0])
        for fila in plano:
            if len(fila) != columnas:
                raise ValueError("Todas las filas deben tener el mismo tamaño.")

        self.__plano = list(plano)
        self.__muros = []

        for fila in range(len(self.__plano)):
            for columna in range(len(self.__plano[fila])):
                if self.__plano[fila][columna] == "#":
                    x = columna * TAMANO_CELDA
                    y = fila * TAMANO_CELDA
                    muro = Rect(x, y, TAMANO_CELDA, TAMANO_CELDA)
                    self.__muros.append(muro)

    def get_muros(self):
        muros = []
        for muro in self.__muros:
            muros.append(muro.copy())
        return muros

    def get_dimensiones(self):
        ancho = len(self.__plano[0]) * TAMANO_CELDA
        alto = len(self.__plano) * TAMANO_CELDA
        return ancho, alto
