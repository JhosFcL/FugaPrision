import math
from .geometria import circulo_toca_rectangulo, distancia, dentro_de_vision
from .personajes import Prisionero, Guardia

TAMANO = 36
COLUMNAS = 24
FILAS = 14


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
    def __init__(self, puntaje):
        self.puntaje = puntaje
        self.dt = 0.0
        self.tiempo = 0.0
        self.teclas = set()
        self.terminado = False
        self.muros = []
        self._crear_muros()
        self.prisionero = Prisionero(self, *centro(2, 11))
        self.guardia = Guardia(self, [centro(9, 7), centro(17, 7)])
        self.personajes = [self.prisionero, self.guardia]
        # Montada bajo el muro horizontal: vigila el pasillo central.
        self.camaras = [Camara(centro(15, 5))]
        self.llave = Llave(centro(8, 2))
        self.salida = PuertaSalida(centro(21, 2))

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
                if borde or horizontal or vertical or divisiones or coberturas:
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
        return self.resolver_interacciones()

    def resolver_interacciones(self):
        if self.terminado:
            return None
        detectado = self.guardia.puede_detectar(self.prisionero)
        for camara in self.camaras:
            detectado = detectado or camara.detectar(self.prisionero, self.muros)
        # La captura tiene prioridad sobre la llave y la salida.
        if detectado:
            self.terminado = True
            return "derrota"
        if self.llave.recoger(self.prisionero):
            self.puntaje.sumar(100)
        if self.salida.puede_salir(self.prisionero):
            self.terminado = True
            self.puntaje.sumar(500)
            return "victoria"
        return None
