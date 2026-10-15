from abc import ABC, abstractmethod


class ObservadorPuntaje(ABC):
    @abstractmethod
    def actualizar_puntaje(self, valor):
        pass


class PanelPuntaje(ObservadorPuntaje):
    def __init__(self):
        self.valor = 0

    def actualizar_puntaje(self, valor):
        self.valor = valor


class Puntaje:
    def __init__(self):
        self._valor = 0
        self._observadores = []

    def get_valor(self):
        return self._valor

    def set_valor(self, valor):
        """Cambia el puntaje sin permitir valores inválidos y avisa al panel."""
        if type(valor) is not int or valor < 0:
            raise ValueError("El puntaje debe ser un entero no negativo.")
        self._valor = valor
        self._notificar()

    def suscribir(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)
            observador.actualizar_puntaje(self._valor)

    def desuscribir(self, observador):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def sumar(self, cantidad):
        if type(cantidad) is not int or cantidad <= 0:
            raise ValueError("Los puntos deben ser un entero positivo.")
        self.set_valor(self._valor + cantidad)

    def reiniciar(self):
        self.set_valor(0)

    def _notificar(self):
        for observador in tuple(self._observadores):
            observador.actualizar_puntaje(self._valor)
