import math
from .geometria import circulo_toca_rectangulo, distancia, dentro_de_vision
from .personajes import Prisionero, Guardia
from .combate import Combate

TAMANO = 36
COLUMNAS = 24
FILAS = 14

# Cada pabellón tiene su propia distribución y vigilancia.
ETAPAS = (
    {"nombre": "Pabellón de celdas", "inicio": (2, 11), "llave": (8, 2),
     "salida": (21, 2), "rutas": [((9, 7), (17, 7))],
     "camaras": [((15, 5), math.pi / 2)]},
    {"nombre": "Lavandería", "inicio": (2, 11), "llave": (21, 11),
     "salida": (21, 2), "rutas": [((8, 6), (16, 6)), ((14, 11), (7, 11))],
     "camaras": [((11, 2), math.pi / 2), ((21, 7), math.pi)]},
    {"nombre": "Patio de vigilancia", "inicio": (2, 11), "llave": (3, 2),
     "salida": (21, 11), "rutas": [((7, 5), (16, 5)), ((17, 9), (7, 9))],
     "camaras": [((12, 2), math.pi / 2), ((21, 7), math.pi), ((3, 7), 0)]},
    {"nombre": "El Alcaide", "inicio": (12, 11), "llave": (12, 3),
     "salida": (12, 1), "rutas": [], "camaras": []},
)


def centro(columna, fila):
    return (columna + 0.5) * TAMANO, (fila + 0.5) * TAMANO


class Camara:
    def __init__(self, posicion):
        self.posicion = posicion
        self.angulo = math.pi / 2
        self.alcance = 95
        self.apertura = math.radians(60)

    def detectar(self, prisionero, muros):
        return dentro_de_vision(self.posicion, prisionero.get_posicion(),
                               self.angulo, self.alcance, self.apertura, muros)


class Llave:
    def __init__(self, posicion):
        self.posicion = posicion
        self.disponible = True

    def recoger(self, prisionero):
        if self.disponible and distancia(self.posicion, prisionero.get_posicion()) < 22:
            self.disponible = False
            prisionero.recoger_llave()
            return True
        return False


class PuertaSalida:
    def __init__(self, posicion):
        self.posicion = posicion

    def puede_salir(self, prisionero):
        return prisionero.tiene_llave() and distancia(self.posicion, prisionero.get_posicion()) < 22


class Nivel:
    total_niveles = len(ETAPAS)

    @property
    def configuracion_siguiente(self):
        return ETAPAS[min(self.indice + 1, self.total_niveles - 1)]["nombre"]

    def __init__(self, puntaje, indice=0):
        if not 0 <= indice < self.total_niveles:
            raise ValueError("Nivel inexistente.")
        self.indice = indice
        self.configuracion = ETAPAS[indice]
        self.nombre = self.configuracion["nombre"]
        self.es_final = indice == self.total_niveles - 1
        self.puntaje = puntaje
        self.dt = 0.0
        self.tiempo = 0.0
        self.teclas = set()
        self.terminado = False
        self.muros = []
        self._crear_muros()
        self.prisionero = Prisionero(self, *centro(*self.configuracion["inicio"]))
        self.guardias = [Guardia(self, [centro(*p) for p in ruta])
                         for ruta in self.configuracion["rutas"]]
        # Alias conservado para las herramientas del prototipo.
        self.guardia = self.guardias[0] if self.guardias else None
        self.personajes = [self.prisionero, *self.guardias]
        self.camaras = []
        for posicion, angulo in self.configuracion["camaras"]:
            camara = Camara(centro(*posicion))
            camara.angulo = angulo
            self.camaras.append(camara)
        self.llave = Llave(centro(*self.configuracion["llave"]))
        self.salida = PuertaSalida(centro(*self.configuracion["salida"]))
        self.combate = Combate(self) if self.es_final else None
        if self.es_final:
            self.llave.disponible = False

    def _crear_muros(self):
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                borde = fila in (0, FILAS - 1) or columna in (0, COLUMNAS - 1)
                horizontal = fila in (4, 9) and 5 <= columna <= 18 and columna not in (11, 12)
                vertical = columna == 5 and fila in (5, 6, 8)
                divisiones = ((columna == 5 and fila in (1, 2)) or
                              (columna == 10 and 1 <= fila <= 3) or
                              (columna == 19 and 1 <= fila <= 3) or
                              (columna == 18 and 10 <= fila <= 12) or
                              (columna == 8 and 5 <= fila <= 7))
                coberturas = ((fila == 6 and 10 <= columna <= 13) or
                              (fila == 5 and 1 <= columna <= 4 and columna != 3) or
                              (fila == 8 and 1 <= columna <= 4 and columna != 2) or
                              (fila == 7 and 20 <= columna <= 22 and columna != 20) or
                              (fila == 4 and 20 <= columna <= 22 and columna != 22))
                original = horizontal or vertical or divisiones or coberturas
                lavanderia = ((columna in (6, 17) and fila in (2, 3, 4, 8, 9, 10)) or
                              (fila in (4, 9) and 9 <= columna <= 14) or
                              (columna in (3, 20) and fila in (5, 8)))
                patio = ((columna in (5, 18) and fila in (2, 3, 7, 11)) or
                         (fila in (3, 7, 11) and columna in (9, 10, 13, 14)) or
                         (fila == 9 and columna in (3, 4, 20, 21)))
                arena = columna in (5, 18) and fila in (5, 8)
                interior = (original, lavanderia, patio, arena)[self.indice]
                if borde or interior:
                    self.muros.append((columna * TAMANO, fila * TAMANO, TAMANO, TAMANO))

    def posicion_valida(self, x, y, radio):
        if x < radio or y < radio or x > COLUMNAS * TAMANO - radio or y > FILAS * TAMANO - radio:
            return False
        for muro in self.muros:
            if circulo_toca_rectangulo(x, y, radio, muro):
                return False
        return True

    def actualizar(self, dt, teclas):
        if self.terminado:
            return None
        self.dt = dt
        self.teclas = set(teclas)
        self.tiempo += dt
        for personaje in self.personajes:
            personaje.update()
        if self.combate:
            self.combate.actualizar(dt, self.teclas)
        return self.resolver_interacciones()

    def resolver_interacciones(self):
        if self.terminado:
            return None
        detectado = any(g.puede_detectar(self.prisionero) for g in self.guardias)
        for camara in self.camaras:
            detectado = detectado or camara.detectar(self.prisionero, self.muros)
        # La captura tiene prioridad sobre la llave y la salida.
        if detectado or (self.combate and self.combate.vida <= 0):
            self.terminado = True
            return "derrota"
        if self.combate and self.combate.jefe.derrotado and not self.combate.premiado:
            self.combate.premiado = True
            self.puntaje.sumar(1000)
            self.llave.disponible = True
        if self.llave.recoger(self.prisionero):
            self.puntaje.sumar(100)
        if self.salida.puede_salir(self.prisionero) and (not self.combate or self.combate.jefe.derrotado):
            self.terminado = True
            self.puntaje.sumar(500)
            return "victoria" if self.es_final else "nivel_completado"
        return None
