"""Cálculos del mapa, sin dependencia de la ventana gráfica."""
import math


def distancia(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def circulo_toca_rectangulo(x, y, radio, rectangulo):
    izquierda, arriba, ancho, alto = rectangulo
    cercano_x = max(izquierda, min(x, izquierda + ancho))
    cercano_y = max(arriba, min(y, arriba + alto))
    return math.hypot(x - cercano_x, y - cercano_y) < radio


def fraccion_interseccion(origen, destino, rectangulo):
    """Primer contacto del segmento con un muro, o 1 si no lo cruza."""
    izquierda, arriba, ancho, alto = rectangulo
    entrada = 0.0
    salida = 1.0
    limites = [(izquierda, izquierda + ancho), (arriba, arriba + alto)]
    for eje in range(2):
        avance = destino[eje] - origen[eje]
        minimo, maximo = limites[eje]
        if abs(avance) < 0.000001:
            if origen[eje] < minimo or origen[eje] > maximo:
                return 1.0
        else:
            primero = (minimo - origen[eje]) / avance
            ultimo = (maximo - origen[eje]) / avance
            if primero > ultimo:
                primero, ultimo = ultimo, primero
            entrada = max(entrada, primero)
            salida = min(salida, ultimo)
            if entrada > salida:
                return 1.0
    return entrada


def extremo_visible(origen, destino, muros):
    fraccion = 1.0
    for muro in muros:
        fraccion = min(fraccion, fraccion_interseccion(origen, destino, muro))
    x = origen[0] + (destino[0] - origen[0]) * fraccion
    y = origen[1] + (destino[1] - origen[1]) * fraccion
    return x, y


def dentro_de_vision(origen, objetivo, angulo, alcance, apertura, muros):
    dx = objetivo[0] - origen[0]
    dy = objetivo[1] - origen[1]
    largo = math.hypot(dx, dy)
    if largo > alcance:
        return False
    if largo > 0.000001:
        producto = (dx * math.cos(angulo) + dy * math.sin(angulo)) / largo
        if producto < math.cos(apertura / 2):
            return False
    visible = extremo_visible(origen, objetivo, muros)
    return distancia(visible, objetivo) < 0.001
