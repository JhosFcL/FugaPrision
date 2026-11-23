"""Coordinador principal de la partida y definición de los niveles."""
import math

from pygame import Rect

from creadores import CreadorCentinela, CreadorPatrulla
from estados import Derrota, Jugando, Pausa, Victoria
from mapa import Mapa, TAMANO_CELDA
from nivel import Nivel
from personajes import Prisionero
from puntaje import Puntaje
from seguridad import Camara, Llave, PanelSeguridad, Puerta
from sistema_colisiones import SistemaColisiones


PUNTOS_LLAVE = 100
PUNTOS_NIVEL = 500
TAMANO_PRISIONERO = (28, 28)
ALCANCE_VISION = 165


def _tiene_linea_de_vision(origen, destino, muros):
    for muro in muros:
        if muro.clipline(origen, destino):
            return False
    return True


def _pos_celda(columna, fila, tamano=TAMANO_PRISIONERO):
    x = columna * TAMANO_CELDA + (TAMANO_CELDA - tamano[0]) // 2
    y = fila * TAMANO_CELDA + (TAMANO_CELDA - tamano[1]) // 2
    return (x, y)


def _centro_celda(columna, fila):
    return (columna * TAMANO_CELDA + TAMANO_CELDA // 2, fila * TAMANO_CELDA + TAMANO_CELDA // 2)


def _rect_celda(columna, fila, cols=1, filas=1):
    return Rect(columna * TAMANO_CELDA, fila * TAMANO_CELDA, cols * TAMANO_CELDA, filas * TAMANO_CELDA)


NIVELES = [
    # Nivel 1: Pabellón de celdas
    {
        "nombre": "Pabellón de celdas",
        "plano": [
            "####################",
            "#......#...........#",
            "#......#...........#",
            "#..##..#....####...#",
            "#......#...........#",
            "#..................#",
            "#####..######..#####",
            "#..................#",
            "#......#...........#",
            "#..##..#....####...#",
            "#......#...........#",
            "#......#...........#",
            "####################",
        ],
        "prisionero": _pos_celda(2, 11),
        "llave": _rect_celda(2, 1),
        "puerta": _rect_celda(18, 1),
        "panel": _rect_celda(10, 7),
        "camaras": [
            _rect_celda(12, 1, 3, 2),
        ],
        "guardias": [
            (
                CreadorPatrulla(),
                {
                    "posicion": _pos_celda(8, 5),
                    "ruta": [_centro_celda(8, 5), _centro_celda(17, 5)],
                    "velocidad": 110.0,
                },
            ),
            (
                CreadorCentinela(),
                {
                    "posicion": _pos_celda(14, 10),
                    "velocidad": 120.0,
                },
            ),
        ],
    },
    # Nivel 2: Lavandería
    {
        "nombre": "Lavandería",
        "plano": [
            "####################",
            "#...........#......#",
            "#..###..##..#......#",
            "#...........#..##..#",
            "#..###.............#",
            "#......####........#",
            "#..................#",
            "####..######..######",
            "#..................#",
            "#..####....####....#",
            "#..................#",
            "#......#...........#",
            "####################",
        ],
        "prisionero": _pos_celda(2, 11),
        "llave": _rect_celda(17, 1),
        "puerta": _rect_celda(18, 11),
        "panel": _rect_celda(2, 6),
        "camaras": [
            _rect_celda(8, 1, 3, 1),
            _rect_celda(10, 8, 4, 1),
        ],
        "guardias": [
            (
                CreadorPatrulla(),
                {
                    "posicion": _pos_celda(2, 3),
                    "ruta": [_centro_celda(2, 3), _centro_celda(10, 3)],
                    "velocidad": 115.0,
                },
            ),
            (
                CreadorPatrulla(),
                {
                    "posicion": _pos_celda(10, 10),
                    "ruta": [_centro_celda(10, 10), _centro_celda(18, 10)],
                    "velocidad": 120.0,
                },
            ),
            (
                CreadorCentinela(),
                {
                    "posicion": _pos_celda(14, 5),
                    "velocidad": 125.0,
                },
            ),
        ],
    },
    # Nivel 3: Patio de vigilancia
    {
        "nombre": "Patio de vigilancia",
        "plano": [
            "####################",
            "#..................#",
            "#..####..##..####..#",
            "#..................#",
            "######..####..######",
            "#..................#",
            "#..##..######..##..#",
            "#..................#",
            "######..####..######",
            "#..................#",
            "#..####..##..####..#",
            "#..................#",
            "####################",
        ],
        "prisionero": _pos_celda(1, 11),
        "llave": _rect_celda(18, 1),
        "puerta": _rect_celda(18, 11),
        "panel": _rect_celda(1, 5),
        "camaras": [
            _rect_celda(9, 1, 3, 1),
            _rect_celda(8, 7, 4, 1),
            _rect_celda(10, 9, 3, 1),
        ],
        "guardias": [
            (
                CreadorPatrulla(),
                {
                    "posicion": _pos_celda(2, 3),
                    "ruta": [_centro_celda(2, 3), _centro_celda(17, 3)],
                    "velocidad": 125.0,
                },
            ),
            (
                CreadorPatrulla(),
                {
                    "posicion": _pos_celda(17, 5),
                    "ruta": [_centro_celda(17, 5), _centro_celda(4, 5)],
                    "velocidad": 125.0,
                },
            ),
            (
                CreadorCentinela(),
                {
                    "posicion": _pos_celda(14, 11),
                    "velocidad": 135.0,
                },
            ),
        ],
    },
]


class Juego:
    def __init__(self, vista=None):
        self.__nivel_actual = None
        self.__estado_actual = None
        self.__puntaje = Puntaje()
        self.__puntos_inicio_nivel = 0
        self.__vista = vista
        self.iniciar()

    def iniciar(self):
        self.__puntaje.reiniciar()
        self.cargar_nivel(1)
        self.__estado_actual = Jugando(self)

    def cargar_nivel(self, numero):
        if numero < 1 or numero > len(NIVELES):
            raise ValueError(f"Nivel fuera de rango: {numero}")

        config = NIVELES[numero - 1]
        mapa = Mapa(config["plano"])
        colisiones = SistemaColisiones(mapa)

        px, py = config["prisionero"]
        prisionero = Prisionero(Rect(px, py, *TAMANO_PRISIONERO), colisiones)
        camaras = [Camara(zona) for zona in config["camaras"]]
        llave = Llave(config["llave"])
        puerta = Puerta(config["puerta"])
        panel = PanelSeguridad(config["panel"], camaras) if config.get("panel") else None

        nivel = Nivel(numero, mapa, colisiones, prisionero, camaras, llave, puerta, panel)
        for creador, datos_guardia in config["guardias"]:
            creador.incorporar(nivel, datos_guardia)

        self.__nivel_actual = nivel
        self.__puntos_inicio_nivel = self.__puntaje.get_valor()

    def cambiar_estado(self, estado):
        self.__estado_actual = estado

    def procesar_evento(self, evento):
        self.__estado_actual.manejar_evento(evento)

    def update(self, dt):
        self.__estado_actual.update(dt)

    def actualizar_nivel(self, dt):
        nivel = self.__nivel_actual
        colisiones = nivel.get_colisiones()
        prisionero = nivel.get_prisionero()

        # Polimorfismo: una única llamada update(dt) para todos los personajes.
        for personaje in nivel.get_personajes():
            personaje.update(dt)

        panel = nivel.get_panel()
        if panel is not None:
            panel.update(dt)

        rect_preso = prisionero.get_rect()

        # Panel de seguridad: apaga sus cámaras a cambio de alertar a los guardias.
        if panel is not None and colisiones.toca(rect_preso, panel.get_rect()):
            if panel.activar():
                for guardia in nivel.get_guardias():
                    guardia.alertar(rect_preso.center)

        # Cámaras activas alertan a los guardias (no causan derrota instantánea).
        for camara in nivel.get_camaras():
            if camara.detectar(rect_preso):
                for guardia in nivel.get_guardias():
                    guardia.alertar(rect_preso.center)
                break

        # Visión directa de los guardias (bloqueada por los muros del mapa).
        muros = nivel.get_mapa().get_muros()
        for guardia in nivel.get_guardias():
            centro_g = guardia.get_rect().center
            distancia = math.hypot(rect_preso.centerx - centro_g[0], rect_preso.centery - centro_g[1])
            if distancia <= ALCANCE_VISION and _tiene_linea_de_vision(centro_g, rect_preso.center, muros):
                guardia.alertar(rect_preso.center)

        # Captura por contacto con cualquier guardia.
        for guardia in nivel.get_guardias():
            if colisiones.toca(rect_preso, guardia.get_rect()):
                self.cambiar_estado(Derrota(self))
                return

        # Recogida de llave (una sola vez).
        llave = nivel.get_llave()
        if colisiones.toca(rect_preso, llave.get_rect()) and llave.recoger():
            prisionero.recoger_llave()
            self.__puntaje.sumar(PUNTOS_LLAVE)

        # Puerta de salida: exige tener la llave.
        puerta = nivel.get_puerta()
        if prisionero.tiene_llave() and colisiones.toca(rect_preso, puerta.get_rect()):
            puerta.abrir()
            self.__puntaje.sumar(PUNTOS_NIVEL)
            self.siguiente_nivel()

    def dibujar(self):
        if self.__vista is None:
            return
        self.__vista.dibujar(self)
        if isinstance(self.__estado_actual, Pausa):
            self.__vista.dibujar_pausa()
        elif isinstance(self.__estado_actual, Victoria):
            self.__vista.dibujar_resultado(True)
        elif isinstance(self.__estado_actual, Derrota):
            self.__vista.dibujar_resultado(False)

    def siguiente_nivel(self):
        actual = self.__nivel_actual.get_numero()
        if actual < len(NIVELES):
            self.cargar_nivel(actual + 1)
        else:
            self.cambiar_estado(Victoria(self))

    def reiniciar_nivel(self):
        self.__puntaje.restaurar(self.__puntos_inicio_nivel)
        self.cargar_nivel(self.__nivel_actual.get_numero())
        self.cambiar_estado(Jugando(self))

    def reiniciar_partida(self):
        self.iniciar()

    def get_nivel(self):
        return self.__nivel_actual

    def get_puntaje(self):
        return self.__puntaje

    def get_estado(self):
        return self.__estado_actual
