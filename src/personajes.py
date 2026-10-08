from abc import ABC, abstractmethod
import math
from .geometria import distancia, dentro_de_vision


class HabilidadCarrera:
    def __init__(self):
        self._duracion = 0.0
        self._recarga = 0.0

    def activar(self):
        if self._duracion > 0 or self._recarga > 0:
            return False
        self._duracion = 2.0
        return True

    def actualizar(self, dt):
        if self._duracion > 0:
            sobrante = max(0.0, dt - self._duracion)
            self._duracion = max(0.0, self._duracion - dt)
            if self._duracion == 0:
                self._recarga = max(0.0, 5.0 - sobrante)
        else:
            self._recarga = max(0.0, self._recarga - dt)

    def get_multiplicador(self):
        if self._duracion > 0:
            return 1.5
        return 1.0

    def get_estado(self):
        if self._duracion > 0:
            return f"ACTIVA  {self._duracion:.1f} s"
        if self._recarga > 0:
            return f"RECARGA  {self._recarga:.1f} s"
        return "LISTA  [SHIFT]"


class Personaje(ABC):
    def __init__(self, nivel, x, y, velocidad):
        self.nivel = nivel
        self._x = float(x)
        self._y = float(y)
        self._velocidad = velocidad
        self.radio = 10

    def get_posicion(self):
        return self._x, self._y

    def mover(self, dx, dy):
        # Pasos pequeños evitan atravesar muros a velocidades altas.
        pasos = max(1, math.ceil(max(abs(dx), abs(dy)) / 4))
        for _ in range(pasos):
            nuevo_x = self._x + dx / pasos
            if self.nivel.posicion_valida(nuevo_x, self._y, self.radio):
                self._x = nuevo_x
            nuevo_y = self._y + dy / pasos
            if self.nivel.posicion_valida(self._x, nuevo_y, self.radio):
                self._y = nuevo_y

    @abstractmethod
    def update(self):
        pass


class Prisionero(Personaje):
    def __init__(self, nivel, x, y):
        super().__init__(nivel, x, y, 145)
        self._tiene_llave = False
        self.carrera = HabilidadCarrera()

    def tiene_llave(self):
        return self._tiene_llave

    def recoger_llave(self):
        self._tiene_llave = True

    def update(self):
        teclas = self.nivel.teclas
        dx = int("derecha" in teclas) - int("izquierda" in teclas)
        dy = int("abajo" in teclas) - int("arriba" in teclas)
        norma = math.hypot(dx, dy)
        if norma > 0:
            avance = self._velocidad * self.carrera.get_multiplicador() * self.nivel.dt
            self.mover(dx / norma * avance, dy / norma * avance)
        self.carrera.actualizar(self.nivel.dt)


class Guardia(Personaje):
    def __init__(self, nivel, ruta):
        super().__init__(nivel, ruta[0][0], ruta[0][1], 65)
        self.ruta = ruta
        self._objetivo = 1
        self.angulo = 0.0
        self.alcance = 155
        self.apertura = math.radians(65)

    def update(self):
        objetivo = self.ruta[self._objetivo]
        largo = distancia(self.get_posicion(), objetivo)
        if largo < 0.01:
            self._objetivo = (self._objetivo + 1) % len(self.ruta)
            objetivo = self.ruta[self._objetivo]
            largo = distancia(self.get_posicion(), objetivo)
        if largo > 0:
            dx = objetivo[0] - self._x
            dy = objetivo[1] - self._y
            self.angulo = math.atan2(dy, dx)
            avance = min(largo, self._velocidad * self.nivel.dt)
            self.mover(dx / largo * avance, dy / largo * avance)

    def puede_detectar(self, prisionero):
        if distancia(self.get_posicion(), prisionero.get_posicion()) <= self.radio + prisionero.radio:
            return True
        return dentro_de_vision(self.get_posicion(), prisionero.get_posicion(),
                               self.angulo, self.alcance, self.apertura, self.nivel.muros)
