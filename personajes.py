"""Jerarquía de personajes del juego: Prisionero y guardias."""
from abc import ABC, abstractmethod
import math


class Personaje(ABC):
    def __init__(self, rect, velocidad, colisiones):
        if velocidad <= 0:
            raise ValueError("La velocidad debe ser positiva.")
        self.__rect = rect.copy()
        self.__velocidad = float(velocidad)
        self.__colisiones = colisiones

    def get_rect(self):
        return self.__rect.copy()

    def mover(self, dx, dy, dt):
        if dt <= 0 or (dx == 0 and dy == 0):
            return
        norma = math.hypot(dx, dy)
        ux = dx / norma
        uy = dy / norma
        paso_x = round(ux * self.__velocidad * dt)
        paso_y = round(uy * self.__velocidad * dt)
        self.__rect = self.__colisiones.mover(self.__rect, paso_x, paso_y)

    @abstractmethod
    def update(self, dt):
        ...


class Prisionero(Personaje):
    def __init__(self, rect, colisiones, velocidad=180.0):
        super().__init__(rect, velocidad, colisiones)
        self.__llave_obtenida = False
        self.__direccion = (0, 0)

    def set_direccion(self, dx, dy):
        self.__direccion = (int(dx), int(dy))

    def recoger_llave(self):
        self.__llave_obtenida = True

    def tiene_llave(self):
        return self.__llave_obtenida

    def update(self, dt):
        dx, dy = self.__direccion
        self.mover(dx, dy, dt)


class Guardia(Personaje, ABC):
    def __init__(self, rect, colisiones, velocidad=120.0):
        super().__init__(rect, velocidad, colisiones)
        self.__alerta = False
        self.__objetivo = None

    def alertar(self, posicion):
        self.__alerta = True
        self.__objetivo = (posicion[0], posicion[1])

    def dejar_alerta(self):
        self.__alerta = False
        self.__objetivo = None

    def esta_alerta(self):
        return self.__alerta

    def _perseguir(self, dt):
        if not self.__alerta or self.__objetivo is None:
            return False

        rect_antes = self.get_rect()
        dx = self.__objetivo[0] - rect_antes.centerx
        dy = self.__objetivo[1] - rect_antes.centery
        if math.hypot(dx, dy) <= 6:
            self.dejar_alerta()
            return True

        self.mover(dx, dy, dt)
        if self.get_rect() == rect_antes:
            self.dejar_alerta()
        return True

    @abstractmethod
    def update(self, dt):
        ...


class GuardiaPatrulla(Guardia):
    def __init__(self, rect, colisiones, ruta, velocidad=120.0):
        super().__init__(rect, colisiones, velocidad)
        if not ruta:
            raise ValueError("La ruta de patrulla no puede estar vacía.")
        self.__ruta = [tuple(punto) for punto in ruta]
        self.__indice = 0

    def update(self, dt):
        if self._perseguir(dt):
            return

        destino = self.__ruta[self.__indice]
        rect_actual = self.get_rect()
        dx = destino[0] - rect_actual.centerx
        dy = destino[1] - rect_actual.centery
        if math.hypot(dx, dy) <= 6:
            self.__indice = (self.__indice + 1) % len(self.__ruta)
            return

        self.mover(dx, dy, dt)
        if self.get_rect() == rect_actual:
            self.__indice = (self.__indice + 1) % len(self.__ruta)


class GuardiaCentinela(Guardia):
    def __init__(self, rect, colisiones, origen=None, velocidad=120.0):
        super().__init__(rect, colisiones, velocidad)
        if origen is None:
            self.__origen = (rect.centerx, rect.centery)
        else:
            self.__origen = (origen[0], origen[1])

    def update(self, dt):
        if self._perseguir(dt):
            return

        rect_actual = self.get_rect()
        dx = self.__origen[0] - rect_actual.centerx
        dy = self.__origen[1] - rect_actual.centery
        if math.hypot(dx, dy) > 6:
            self.mover(dx, dy, dt)
