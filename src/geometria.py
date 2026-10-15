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


def hay_linea_de_vision(origen, objetivo, muros):
    """Los muros bloquean tanto la visión frontal como la vigilancia cercana."""
    return distancia(extremo_visible(origen, objetivo, muros), objetivo) < 0.001


def _punto_en_campo(origen, objetivo, angulo, alcance, apertura):
    dx = objetivo[0] - origen[0]
    dy = objetivo[1] - origen[1]
    largo = math.hypot(dx, dy)
    if largo > alcance:
        return False
    if largo > 0.000001:
        producto = (dx * math.cos(angulo) + dy * math.sin(angulo)) / largo
        if producto + 0.000001 < math.cos(apertura / 2):
            return False
    return True


def dentro_de_vision(origen, objetivo, angulo, alcance, apertura, muros, radio_objetivo=0):
    """Detecta el cuerpo visible del objetivo, no solamente su punto central."""
    if distancia(origen, objetivo) > alcance + radio_objetivo:
        return False
    puntos = [objetivo]
    if radio_objetivo > 0:
        for indice in range(16):
            direccion = math.tau * indice / 16
            puntos.append((objetivo[0] + math.cos(direccion) * radio_objetivo,
                           objetivo[1] + math.sin(direccion) * radio_objetivo))
    return any(_punto_en_campo(origen, punto, angulo, alcance, apertura)
               and hay_linea_de_vision(origen, punto, muros) for punto in puntos)


def poligono_vision(origen, angulo, alcance, apertura, muros):
    """Recorta el área dibujada en los mismos muros que bloquean la detección."""
    muros = [muro for muro in muros if circulo_toca_rectangulo(*origen, alcance, muro)]
    pasos = max(60, math.ceil(apertura * alcance / 4))
    direcciones = [-apertura / 2 + apertura * i / pasos for i in range(pasos + 1)]
    for x, y, ancho, alto in muros:
        for esquina in ((x, y), (x + ancho, y), (x, y + alto), (x + ancho, y + alto)):
            if distancia(origen, esquina) > alcance:
                continue
            relativo = (math.atan2(esquina[1] - origen[1], esquina[0] - origen[0])
                        - angulo + math.pi) % math.tau - math.pi
            for ajuste in (-0.00001, 0, 0.00001):
                if -apertura / 2 <= relativo + ajuste <= apertura / 2:
                    direcciones.append(relativo + ajuste)
    puntos = [origen]
    for relativo in sorted(set(direcciones)):
        direccion = angulo + relativo
        destino = (origen[0] + math.cos(direccion) * alcance,
                   origen[1] + math.sin(direccion) * alcance)
        puntos.append(extremo_visible(origen, destino, muros))
    return puntos
