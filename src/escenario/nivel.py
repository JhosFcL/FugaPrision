"""Contenedor de las entidades y colaboradores de un escenario."""
from src.entidades.personajes import Guardia, Prisionero


class Nivel:
    def __init__(self, numero, mapa, colisiones, prisionero, camaras, llave, puerta, panel=None):
        self.__numero = numero
        self.__mapa = mapa
        self.__colisiones = colisiones
        self.__personajes = [prisionero]
        self.__camaras = list(camaras)
        self.__llave = llave
        self.__puerta = puerta
        self.__panel = panel

    def agregar_guardia(self, guardia):
        if not isinstance(guardia, Guardia):
            raise TypeError("Solo se pueden agregar instancias de Guardia.")
        self.__personajes.append(guardia)

    def get_numero(self):
        return self.__numero

    def get_mapa(self):
        return self.__mapa

    def get_colisiones(self):
        return self.__colisiones

    def get_personajes(self):
        return list(self.__personajes)

    def get_prisionero(self):
        for personaje in self.__personajes:
            if isinstance(personaje, Prisionero):
                return personaje
        raise ValueError("El nivel no tiene un prisionero.")

    def get_guardias(self):
        return [p for p in self.__personajes if isinstance(p, Guardia)]

    def get_camaras(self):
        return list(self.__camaras)

    def get_llave(self):
        return self.__llave

    def get_puerta(self):
        return self.__puerta

    def get_panel(self):
        return self.__panel
