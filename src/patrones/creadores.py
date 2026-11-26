"""Patrón Factory Method para crear e incorporar guardias en un nivel."""
from abc import ABC, abstractmethod

from pygame import Rect

from src.entidades.personajes import GuardiaCentinela, GuardiaPatrulla


TAMANO_GUARDIA = (22, 22)


class CreadorGuardia(ABC):
    @abstractmethod
    def crear(self, datos, colisiones):
        ...

    def incorporar(self, nivel, datos):
        guardia = self.crear(datos, nivel.get_colisiones())
        nivel.agregar_guardia(guardia)


class CreadorPatrulla(CreadorGuardia):
    def crear(self, datos, colisiones):
        x, y = datos["posicion"]
        ancho, alto = datos.get("tamano", TAMANO_GUARDIA)
        velocidad = datos.get("velocidad", 95.0)
        return GuardiaPatrulla(Rect(x, y, ancho, alto), colisiones, datos["ruta"], velocidad)


class CreadorCentinela(CreadorGuardia):
    def crear(self, datos, colisiones):
        x, y = datos["posicion"]
        ancho, alto = datos.get("tamano", TAMANO_GUARDIA)
        velocidad = datos.get("velocidad", 100.0)
        origen = datos.get("origen")
        return GuardiaCentinela(Rect(x, y, ancho, alto), colisiones, origen, velocidad)
