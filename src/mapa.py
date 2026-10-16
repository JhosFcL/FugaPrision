"""Planos cerrados, colisiones y caminos compartidos por movimiento y sonido."""
from collections import deque
import math

from .geometria import distancia

TAMANO = 36
COLUMNAS = 24
FILAS = 14
PLANOS = (
    (
        "########################",
        "#.....#.....#.....#....#",
        "#.....#...........#....#",
        "#.....#...........#....#",
        "#..##.#.....#.....#....#",
        "#..##.#.....#.##..#....#",
        "#...........#.##..#....#",
        "#...........#.....#.##.#",
        "#.....#..##.#.....#.##.#",
        "#####.#..##.#.....#....#",
        "#...#.#.....#..........#",
        "#...P.#.....#..........#",
        "#...###.....#.....#....#",
        "########################",
    ),
    (
        "########################",
        "#.....#.....#.....#....#",
        "#...........#.##..#....#",
        "#...........#.##..#....#",
        "#.....#.....#.....#....#",
        "#.....#..##.#..........#",
        "#.....#..##.#..........#",
        "#.....#.....#.....#....#",
        "#..##.#.....#.....#....#",
        "#..##.#.....#.....#.##.#",
        "#.....#...........#.##.#",
        "#.....#...........#....#",
        "#.....#.....#.....#....#",
        "########################",
    ),
    (
        "########################",
        "#.......##.............#",
        "#.......##.............#",
        "#......................#",
        "####PP############..####",
        "#..............##......#",
        "#.........##...##......#",
        "#.........##...........#",
        "#......................#",
        "####..##############PP##",
        "#.................##...#",
        "#...........##....##...#",
        "#...........##.........#",
        "########################",
    ),
    (
        "########################",
        "#......................#",
        "#......................#",
        "#......................#",
        "#......................#",
        "#....#............#....#",
        "#......................#",
        "#......................#",
        "#....#............#....#",
        "#......................#",
        "#......................#",
        "#......................#",
        "#......................#",
        "########################",
    ),
)


def centro(columna, fila):
    return (columna + 0.5) * TAMANO, (fila + 0.5) * TAMANO


class Mapa:
    def __init__(self, plano):
        if len(plano) != FILAS or any(len(fila) != COLUMNAS for fila in plano):
            raise ValueError("El plano debe tener 24 columnas y 14 filas.")
        if (any(c != "#" for c in plano[0] + plano[-1]) or
                any(fila[0] != "#" or fila[-1] != "#" for fila in plano)):
            raise ValueError("El perímetro del mapa debe estar cerrado.")
        self.plano = plano
        self.muros = [(x * TAMANO, y * TAMANO, TAMANO, TAMANO)
                      for y, fila in enumerate(plano) for x, celda in enumerate(fila) if celda in "#P"]

    def abrir_puerta(self, posicion):
        columna, fila = int(posicion[0] // TAMANO), int(posicion[1] // TAMANO)
        if self.plano[fila][columna] == "P":
            filas = list(self.plano)
            filas[fila] = filas[fila][:columna] + "." + filas[fila][columna + 1:]
            self.plano = tuple(filas)
            self.muros.remove((columna * TAMANO, fila * TAMANO, TAMANO, TAMANO))

    def posicion_valida(self, x, y, radio):
        if not all(math.isfinite(v) for v in (x, y, radio)) or radio <= 0:
            return False
        if not (radio <= x <= COLUMNAS * TAMANO - radio and
                radio <= y <= FILAS * TAMANO - radio):
            return False
        return not any(x + radio > mx + 0.000001 and x - radio < mx + ancho - 0.000001
                       and y + radio > my + 0.000001 and y - radio < my + alto - 0.000001
                       for mx, my, ancho, alto in self.muros)

    def desplazar(self, posicion, dx, dy, radio):
        """Recorta cada eje en la primera pared; un salto grande tampoco la atraviesa."""
        x, y = posicion
        destino_x = max(radio, min(COLUMNAS * TAMANO - radio, x + dx))
        for mx, my, ancho, alto in self.muros:
            if y + radio <= my + 0.000001 or y - radio >= my + alto - 0.000001:
                continue
            if dx > 0 and x + radio <= mx + 0.000001:
                destino_x = min(destino_x, mx - radio)
            elif dx < 0 and x - radio >= mx + ancho - 0.000001:
                destino_x = max(destino_x, mx + ancho + radio)
        destino_y = max(radio, min(FILAS * TAMANO - radio, y + dy))
        for mx, my, ancho, alto in self.muros:
            if destino_x + radio <= mx + 0.000001 or destino_x - radio >= mx + ancho - 0.000001:
                continue
            if dy > 0 and y + radio <= my + 0.000001:
                destino_y = min(destino_y, my - radio)
            elif dy < 0 and y - radio >= my + alto - 0.000001:
                destino_y = max(destino_y, my + alto + radio)
        return destino_x, destino_y

    def buscar_ruta(self, origen, destino, radio=12):
        """Busca un camino por suelo transitable, sin cortar esquinas ni cruzar muros."""
        if not self.posicion_valida(*origen, radio) or not self.posicion_valida(*destino, radio):
            return []
        inicio = int(origen[0] // TAMANO), int(origen[1] // TAMANO)
        final = int(destino[0] // TAMANO), int(destino[1] // TAMANO)
        if inicio == final:
            return [destino]
        pendientes = deque([inicio])
        anteriores = {inicio: None}
        while pendientes:
            actual = pendientes.popleft()
            if actual == final:
                break
            x, y = actual
            for vecina in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if vecina not in anteriores and self.posicion_valida(*centro(*vecina), radio):
                    anteriores[vecina] = actual
                    pendientes.append(vecina)
        if final not in anteriores:
            return []
        ruta = []
        actual = final
        while actual is not None:
            ruta.append(centro(*actual))
            actual = anteriores[actual]
        ruta.reverse()
        if len(ruta) > 1 or distancia(origen, ruta[0]) < 1:
            ruta.pop(0)
        if not ruta or distancia(ruta[-1], destino) > 1:
            ruta.append(destino)
        return ruta

    def distancia_camino(self, origen, destino):
        ruta = self.buscar_ruta(origen, destino)
        if not ruta:
            return math.inf
        return sum(distancia(a, b) for a, b in zip([origen, *ruta], ruta))
