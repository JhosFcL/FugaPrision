from abc import ABC, abstractmethod
import math
from .geometria import distancia, dentro_de_vision, hay_linea_de_vision


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
        self.radio = 12

    def get_posicion(self):
        return self._x, self._y

    def mover(self, dx, dy):
        self._x, self._y = self.nivel.mapa.desplazar(self.get_posicion(), dx, dy, self.radio)

    @abstractmethod
    def update(self):
        pass


class Prisionero(Personaje):
    def __init__(self, nivel, x, y):
        super().__init__(nivel, x, y, 145)
        self._tiene_llave = False
        self.carrera = HabilidadCarrera()
        self.movimiento = "QUIETO"
        self.ruido = 0.0
        self._pasos = 0.0

    def tiene_llave(self):
        return self._tiene_llave

    def recoger_llave(self):
        self._tiene_llave = True

    def update(self):
        teclas = self.nivel.teclas
        dx = int("derecha" in teclas) - int("izquierda" in teclas)
        dy = int("abajo" in teclas) - int("arriba" in teclas)
        norma = math.hypot(dx, dy)
        self.movimiento = "QUIETO"
        self.ruido = 0.0
        if norma > 0:
            sigilo = "sigilo" in teclas
            multiplicador = 0.55 if sigilo else self.carrera.get_multiplicador()
            avance = self._velocidad * multiplicador * self.nivel.dt
            anterior = self.get_posicion()
            self.mover(dx / norma * avance, dy / norma * avance)
            recorrido = distancia(anterior, self.get_posicion())
            if recorrido > 0.001:
                self.movimiento = "SIGILO" if sigilo else ("CORRE" if multiplicador > 1 else "CAMINA")
                self.ruido = 20.0 if sigilo else (210.0 if multiplicador > 1 else 80.0)
                self._pasos += recorrido
                if self._pasos >= 22:
                    self._pasos %= 22
                    self.nivel.ruidos.emitir(self.get_posicion(), self.ruido)
        self.carrera.actualizar(self.nivel.dt)


class Guardia(Personaje):
    def __init__(self, nivel, ruta):
        if len(ruta) < 2:
            raise ValueError("La patrulla necesita al menos dos posiciones.")
        super().__init__(nivel, ruta[0][0], ruta[0][1], 65)
        self.ruta = ruta
        self._objetivo = 1
        self.angulo = math.atan2(ruta[1][1] - ruta[0][1], ruta[1][0] - ruta[0][0])
        self.alcance = 155
        self.apertura = math.radians(65)
        self.modo = "PATRULLA"
        self.ultima_posicion = None
        self._recuerdo = 0.0
        self._busqueda = 3.0
        self._camino = []
        self._destino = None
        self._recalculo = 0.0

    def update(self):
        dt = self.nivel.dt
        self._recalculo = max(0.0, self._recalculo - dt)
        self._recuerdo = max(0.0, self._recuerdo - dt)
        if self.puede_detectar(self.nivel.prisionero):
            self.alertar(self.nivel.prisionero.get_posicion())
        elif self.modo == "PERSIGUE" and self._recuerdo == 0:
            self.modo = "BUSCA"
        if self.modo == "PATRULLA":
            if self._ir_a(self.ruta[self._objetivo], self._velocidad):
                self._objetivo = (self._objetivo + 1) % len(self.ruta)
        else:
            velocidad = 155 if self.modo == "PERSIGUE" else 95
            if self._ir_a(self.ultima_posicion, velocidad) and self.modo != "PERSIGUE":
                self.angulo += dt * 1.6
                self._busqueda = max(0.0, self._busqueda - dt)
                if self._busqueda == 0:
                    self._volver_a_patrulla()

    def escuchar(self, posicion):
        if self.modo == "PERSIGUE":
            return
        self.modo = "INVESTIGA"
        self.ultima_posicion = posicion
        self._busqueda = 3.0

    def alertar(self, posicion):
        self.modo = "PERSIGUE"
        self.ultima_posicion = posicion
        self._recuerdo = 0.4
        self._busqueda = 3.0

    def _volver_a_patrulla(self):
        self.modo = "PATRULLA"
        self.ultima_posicion = None
        self._objetivo = min(range(len(self.ruta)), key=lambda i:
                             self.nivel.mapa.distancia_camino(self.get_posicion(), self.ruta[i]))
        self._recalculo = 0.0
        self._destino = None

    def _ir_a(self, objetivo, velocidad):
        if distancia(self.get_posicion(), objetivo) <= 2:
            return True
        if (self._recalculo == 0 or self._destino is None
                or distancia(self._destino, objetivo) > 18):
            self._camino = self.nivel.mapa.buscar_ruta(self.get_posicion(), objetivo, self.radio)
            self._destino = objetivo
            self._recalculo = 0.35
        if not self._camino:
            return False
        dx = self._camino[0][0] - self._x
        dy = self._camino[0][1] - self._y
        largo = math.hypot(dx, dy)
        if largo > 0:
            self.angulo = math.atan2(dy, dx)
            avance = min(largo, velocidad * self.nivel.dt)
            self.mover(dx / largo * avance, dy / largo * avance)
        if distancia(self.get_posicion(), self._camino[0]) < 0.5:
            self._camino.pop(0)
        return distancia(self.get_posicion(), objetivo) <= 2

    def puede_detectar(self, prisionero):
        return dentro_de_vision(self.get_posicion(), prisionero.get_posicion(), self.angulo,
                               self.alcance, self.apertura, self.nivel.mapa.muros, prisionero.radio)

    def puede_capturar(self, prisionero):
        return (distancia(self.get_posicion(), prisionero.get_posicion()) <= self.radio + prisionero.radio
                and hay_linea_de_vision(self.get_posicion(), prisionero.get_posicion(), self.nivel.mapa.muros))
