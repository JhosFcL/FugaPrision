"""Combate de arena independiente de Pygame: ráfagas, avisos y colisiones."""
import math
from dataclasses import dataclass
from .geometria import distancia, fraccion_interseccion


@dataclass
class Proyectil:
    x: float
    y: float
    vx: float
    vy: float
    enemigo: bool = True
    radio: float = 6
    duracion: float = 7

    @property
    def posicion(self):
        return self.x, self.y

    def avanzar(self, dt):
        inicio = self.posicion
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.duracion -= dt
        return inicio, self.posicion


def contacto_segmento(inicio, fin, centro, radio):
    """Fracción del primer impacto; los tiros rápidos no atraviesan objetivos."""
    dx, dy = fin[0] - inicio[0], fin[1] - inicio[1]
    ox, oy = inicio[0] - centro[0], inicio[1] - centro[1]
    c = ox * ox + oy * oy - radio * radio
    if c <= 0:
        return 0.0
    a = dx * dx + dy * dy
    if a == 0:
        return None
    b = 2 * (ox * dx + oy * dy)
    discriminante = b * b - 4 * a * c
    if discriminante < 0:
        return None
    t = (-b - math.sqrt(discriminante)) / (2 * a)
    return t if 0 <= t <= 1 else None


class Alcaide:
    nombre = "EL ALCAIDE"
    capas_totales = 3
    vida_por_capa = 72
    vida_maxima = capas_totales * vida_por_capa
    radio = 28

    def __init__(self):
        self.x, self.y = 450.0, 126.0
        self.vida = self.vida_maxima
        self.espera = 2.0  # Tiempo para leer los controles al entrar.
        self.aviso = 0.0
        self.patron = 0
        self.objetivo = (450.0, 414.0)
        self.destino = None
        self.golpe = 0.0
        self.transicion = 0.0

    @property
    def posicion(self):
        return self.x, self.y

    @property
    def derrotado(self):
        return self.vida <= 0

    @property
    def fase(self):
        return min(self.capas_totales, self.capas_totales - self.capas_restantes + 1)

    @property
    def capas_restantes(self):
        return math.ceil(max(0, self.vida) / self.vida_por_capa)

    @property
    def vida_capa(self):
        return (self.vida - 1) % self.vida_por_capa + 1 if not self.derrotado else 0

    @property
    def ataque(self):
        return ("CORONA DE LÁGRIMAS", "RÁFAGA DIRIGIDA", "EMBESTIDA")[self.patron % 3]

    def recibir_impacto(self):
        if self.derrotado or self.transicion > 0:
            return
        fase_anterior = self.fase
        self.vida = max(0, self.vida - 1)
        self.golpe = 0.08
        if self.fase != fase_anterior:
            # Cada capa tiene su propia fase y un aviso breve antes de reanudar.
            self.transicion = 1.1
            self.aviso = 0.0
            self.destino = None
            self.espera = 0.0
            self.patron = 0

    def actualizar(self, combate, dt):
        if self.derrotado:
            return
        self.golpe = max(0, self.golpe - dt)
        if self.transicion > 0:
            self.transicion = max(0, self.transicion - dt)
            return
        if self.destino is not None:
            largo = distancia(self.posicion, self.destino)
            avance = min(largo, (280, 370, 460)[self.fase - 1] * dt)
            if largo > 0:
                self.x += (self.destino[0] - self.x) / largo * avance
                self.y += (self.destino[1] - self.y) / largo * avance
            if largo <= avance + 0.01:
                self.destino = None
                self.patron += 1
                self.espera = (1.1, 0.65, 0.35)[self.fase - 1]
            return
        if self.aviso > 0:
            self.aviso = max(0, self.aviso - dt)
            if self.aviso == 0:
                self._atacar(combate)
            return
        self.espera = max(0, self.espera - dt)
        if self.espera == 0:
            self.objetivo = combate.nivel.prisionero.get_posicion()
            self.aviso = (0.95, 0.72, 0.50)[self.fase - 1]

    def _atacar(self, combate):
        angulo = math.atan2(self.objetivo[1] - self.y, self.objetivo[0] - self.x)
        tipo = self.patron % 3
        if tipo == 0:
            cantidad = (12, 20, 28)[self.fase - 1]
            for anillo in range(self.fase):
                for i in range(cantidad):
                    direccion = angulo + i * math.tau / cantidad + anillo * math.pi / cantidad
                    velocidad = (115, 155, 205)[self.fase - 1] - anillo * 20
                    combate.emitir(self.posicion, direccion, velocidad)
        elif tipo == 1:
            cantidad = (5, 9, 13)[self.fase - 1]
            for i in range(cantidad):
                combate.emitir(self.posicion, angulo + (i - cantidad // 2) * 0.16,
                               (185, 240, 300)[self.fase - 1])
        else:
            # La embestida fija su destino al comenzar el aviso, se puede esquivar.
            destino = (max(80, min(784, self.objetivo[0])),
                       max(80, min(424, self.objetivo[1])))
            fraccion = min((fraccion_interseccion(self.posicion, destino,
                            (x - self.radio, y - self.radio,
                             w + 2 * self.radio, h + 2 * self.radio))
                            for x, y, w, h in combate.nivel.mapa.muros), default=1.0)
            fraccion = max(0, fraccion - 0.005)
            self.destino = (self.x + (destino[0] - self.x) * fraccion,
                            self.y + (destino[1] - self.y) * fraccion)
            return
        self.patron += 1
        self.espera = (1.45, 0.85, 0.45)[self.fase - 1]


class Combate:
    vida_maxima = 5

    def __init__(self, nivel):
        self.nivel = nivel
        self.jefe = Alcaide()
        self.proyectiles = []
        self.vida = self.vida_maxima
        self.inmune = 0.0
        self.recarga = 0.0
        self.premiado = False

    def emitir(self, origen, angulo, velocidad, enemigo=True):
        self.proyectiles.append(Proyectil(*origen, math.cos(angulo) * velocidad,
                                         math.sin(angulo) * velocidad, enemigo,
                                         6 if enemigo else 5))

    def recibir_dano(self):
        if self.inmune > 0 or self.jefe.derrotado:
            return
        self.vida = max(0, self.vida - 1)
        self.inmune = 1.1

    def actualizar(self, dt, teclas):
        self.inmune = max(0, self.inmune - dt)
        self.recarga = max(0, self.recarga - dt)
        if self.jefe.derrotado or self.vida <= 0:
            self.proyectiles.clear()
            return
        jugador = self.nivel.prisionero
        posicion_anterior = self.jefe.posicion
        self.jefe.actualizar(self, dt)
        if contacto_segmento(posicion_anterior, self.jefe.posicion, jugador.get_posicion(),
                             jugador.radio + self.jefe.radio) is not None:
            self.recibir_dano()
        dx = int("tiro_derecha" in teclas) - int("tiro_izquierda" in teclas)
        dy = int("tiro_abajo" in teclas) - int("tiro_arriba" in teclas)
        if self.recarga == 0 and (dx or dy or "disparar" in teclas):
            if not (dx or dy):
                dx = self.jefe.x - jugador.get_posicion()[0]
                dy = self.jefe.y - jugador.get_posicion()[1]
            self.emitir(jugador.get_posicion(), math.atan2(dy, dx), 430, enemigo=False)
            self.recarga = 0.18
        vivos = []
        fase_anterior = self.jefe.fase
        for tiro in self.proyectiles:
            inicio, fin = tiro.avanzar(dt)
            # Se expande cada muro por el radio del proyectil.
            muro = min((fraccion_interseccion(inicio, fin,
                        (x - tiro.radio, y - tiro.radio, w + 2 * tiro.radio, h + 2 * tiro.radio))
                        for x, y, w, h in self.nivel.mapa.muros), default=1.0)
            objetivo = jugador.get_posicion() if tiro.enemigo else self.jefe.posicion
            radio = jugador.radio if tiro.enemigo else self.jefe.radio
            impacto = contacto_segmento(inicio, fin, objetivo, radio + tiro.radio)
            if impacto is not None and impacto <= muro:
                if tiro.enemigo:
                    self.recibir_dano()
                else:
                    self.jefe.recibir_impacto()
                continue
            if muro < 1.0 or tiro.duracion <= 0:
                continue
            vivos.append(tiro)
        self.proyectiles = [] if self.jefe.derrotado or self.jefe.fase != fase_anterior else vivos
