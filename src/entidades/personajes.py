"""Jerarquía de personajes del juego: Prisionero y guardias."""
from abc import ABC, abstractmethod
import math


class Personaje(ABC):
    def __init__(self, rect, velocidad, colisiones):
        if velocidad <= 0:
            raise ValueError("La velocidad debe ser positiva.")
        self.__rect = rect.copy()
        self.__pos_x = float(self.__rect.x)
        self.__pos_y = float(self.__rect.y)
        self.__bloqueado = False
        self.__velocidad = float(velocidad)
        self.__colisiones = colisiones
        self.__mirada = (0.0, 1.0)
        self.__en_movimiento = False

    def get_rect(self):
        return self.__rect.copy()

    def get_mirada(self):
        return self.__mirada

    def esta_moviendose(self):
        return self.__en_movimiento

    def _set_mirada(self, vx, vy):
        norma = math.hypot(vx, vy)
        if norma > 1e-6:
            self.__mirada = (vx / norma, vy / norma)

    def _set_en_movimiento(self, activo):
        self.__en_movimiento = bool(activo)

    def _esta_bloqueado(self):
        return self.__bloqueado

    def _mover_con_factor(self, dx, dy, dt, factor=1.0):
        if dt <= 0 or (dx == 0 and dy == 0):
            self.__bloqueado = False
            self.__en_movimiento = False
            return
        norma = math.hypot(dx, dy)
        ux = dx / norma
        uy = dy / norma
        self.__mirada = (ux, uy)

        vel = self.__velocidad * factor
        nuevo_x = self.__pos_x + ux * vel * dt
        nuevo_y = self.__pos_y + uy * vel * dt
        paso_x = round(nuevo_x) - self.__rect.x
        paso_y = round(nuevo_y) - self.__rect.y

        if paso_x == 0 and paso_y == 0:
            self.__pos_x = nuevo_x
            self.__pos_y = nuevo_y
            self.__bloqueado = False
            self.__en_movimiento = True
            return

        rect_nuevo = self.__colisiones.mover(self.__rect, paso_x, paso_y)
        self.__bloqueado = rect_nuevo == self.__rect
        self.__en_movimiento = not self.__bloqueado
        self.__pos_x = nuevo_x if rect_nuevo.x == self.__rect.x + paso_x else float(rect_nuevo.x)
        self.__pos_y = nuevo_y if rect_nuevo.y == self.__rect.y + paso_y else float(rect_nuevo.y)
        self.__rect = rect_nuevo

    def mover(self, dx, dy, dt):
        self._mover_con_factor(dx, dy, dt, 1.0)

    @abstractmethod
    def update(self, dt):
        ...


class Prisionero(Personaje):
    def __init__(self, rect, colisiones, velocidad=200.0):
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
    def __init__(self, rect, colisiones, velocidad=112.0):
        super().__init__(rect, velocidad, colisiones)
        self.__alerta = False
        self.__objetivo = None
        self.__factor_velocidad = 1.0

    def alertar(self, posicion, factor_velocidad=1.22):
        self.__alerta = True
        self.__objetivo = (posicion[0], posicion[1])
        self.__factor_velocidad = float(factor_velocidad)

    def guiar_a(self, posicion):
        """Dirige al guardia rodeando muros sin activar el estado visual de alerta."""
        self.__alerta = False
        self.__objetivo = (posicion[0], posicion[1])
        self.__factor_velocidad = 1.0

    def dejar_alerta(self):
        self.__alerta = False
        self.__objetivo = None
        self.__factor_velocidad = 1.0

    def esta_alerta(self):
        return self.__alerta

    def _perseguir(self, dt):
        if self.__objetivo is None:
            return False

        rect_antes = self.get_rect()
        dx = self.__objetivo[0] - rect_antes.centerx
        dy = self.__objetivo[1] - rect_antes.centery
        if math.hypot(dx, dy) <= 2:
            self.dejar_alerta()
            return True

        self._mover_con_factor(dx, dy, dt, self.__factor_velocidad)
        if self._esta_bloqueado():
            self.dejar_alerta()
        return True

    @abstractmethod
    def update(self, dt):
        ...


class GuardiaPatrulla(Guardia):
    def __init__(self, rect, colisiones, ruta, velocidad=112.0):
        super().__init__(rect, colisiones, velocidad)
        if not ruta:
            raise ValueError("La ruta de patrulla no puede estar vacía.")
        self.__ruta = [tuple(punto) for punto in ruta]
        self.__indice = 0
        if len(self.__ruta) > 1:
            dx = self.__ruta[1][0] - rect.centerx
            dy = self.__ruta[1][1] - rect.centery
            self._set_mirada(dx, dy)

    def get_destino_patrulla(self):
        return self.__ruta[self.__indice]

    def update(self, dt):
        if self._perseguir(dt):
            return

        destino = self.__ruta[self.__indice]
        rect_actual = self.get_rect()
        dx = destino[0] - rect_actual.centerx
        dy = destino[1] - rect_actual.centery
        if math.hypot(dx, dy) <= 6:
            self.__indice = (self.__indice + 1) % len(self.__ruta)
            self._set_en_movimiento(False)
            return

        self.mover(dx, dy, dt)
        if self._esta_bloqueado():
            self.__indice = (self.__indice + 1) % len(self.__ruta)


class GuardiaCentinela(Guardia):
    def __init__(self, rect, colisiones, origen=None, velocidad=118.0):
        super().__init__(rect, colisiones, velocidad)
        if origen is None:
            self.__origen = (rect.centerx, rect.centery)
        else:
            self.__origen = (origen[0], origen[1])
        self.__angulo_barrido = 0.0

    def update(self, dt):
        if self._perseguir(dt):
            return

        rect_actual = self.get_rect()
        dx = self.__origen[0] - rect_actual.centerx
        dy = self.__origen[1] - rect_actual.centery
        if math.hypot(dx, dy) > 6:
            self.mover(dx, dy, dt)
            return

        self._set_en_movimiento(False)
        self.__angulo_barrido = (self.__angulo_barrido + 0.72 * max(0.0, dt)) % (2.0 * math.pi)
        self._set_mirada(math.cos(self.__angulo_barrido), math.sin(self.__angulo_barrido))
