"""Vista Pygame. Las reglas se conservan fuera de esta clase."""
import math
import pygame
from .geometria import extremo_visible
from .nivel import TAMANO, COLUMNAS, FILAS

ANCHO = 1000
ALTO = 760
ORIGEN = (68, 152)


class Vista:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("segoeui", 18)
        self.pequena = pygame.font.SysFont("segoeui", 15)
        self.titulo = pygame.font.SysFont("segoeui", 32, bold=True)
        self.mediana = pygame.font.SysFont("segoeui", 23, bold=True)

    def texto(self, texto, x, y, color=(225, 234, 242), fuente=None):
        imagen = (fuente or self.fuente).render(texto, True, color)
        self.pantalla.blit(imagen, (x, y))

    def punto(self, posicion):
        return round(posicion[0] + ORIGEN[0]), round(posicion[1] + ORIGEN[1])

    def _dibujar_stickman(self, posicion, color, paso=0):
        x, y = posicion
        pygame.draw.ellipse(self.pantalla, (15, 25, 33), (x - 11, y + 12, 22, 6))

        cabeza = (x, y - 11)
        torso = ((x, y - 5), (x, y + 5))
        brazo_izquierdo = ((x, y - 2), (x - 9, y + 3))
        brazo_derecho = ((x, y - 2), (x + 9, y + 3))
        pierna_izquierda = ((x, y + 5), (x - 7 + paso, y + 15))
        pierna_derecha = ((x, y + 5), (x + 7 - paso, y + 15))

        for inicio, fin in (torso, brazo_izquierdo, brazo_derecho,
                            pierna_izquierda, pierna_derecha):
            pygame.draw.line(self.pantalla, (14, 27, 35), inicio, fin, 7)
            pygame.draw.line(self.pantalla, color, inicio, fin, 4)

        pygame.draw.circle(self.pantalla, (14, 27, 35), cabeza, 7)
        pygame.draw.circle(self.pantalla, color, cabeza, 5)

    def _dibujar_vision(self, origen, angulo, alcance, apertura, muros, color):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        puntos = [self.punto(origen)]
        for indice in range(61):
            direccion = angulo - apertura / 2 + apertura * indice / 60
            destino = (origen[0] + math.cos(direccion) * alcance,
                       origen[1] + math.sin(direccion) * alcance)
            puntos.append(self.punto(extremo_visible(origen, destino, muros)))
        pygame.draw.polygon(capa, (*color, 55), puntos)
        pygame.draw.lines(capa, (*color, 120), False, puntos[1:], 1)
        self.pantalla.blit(capa, (0, 0))

    def dibujar(self, juego):
        nivel = juego.nivel
        self.pantalla.fill((13, 21, 31))
        self.texto("FUGA DE LA PRISIÓN", 68, 24, fuente=self.titulo)
        self.texto("PROTOTIPO PARCIAL  /  PABELLÓN 01", 70, 66, (139, 159, 178), self.pequena)
        self.texto(f"PUNTOS  {juego.panel.valor:04d}", 738, 28, (111, 226, 188), self.mediana)
        self.texto(f"TIEMPO  {nivel.tiempo:05.1f} s", 740, 62, (139, 159, 178), self.pequena)
        llave = "LLAVE OBTENIDA · BUSCA LA SALIDA" if nivel.prisionero.tiene_llave() else "OBJETIVO · CONSIGUE LA LLAVE Y ESCAPA"
        self.texto(llave, 70, 110, (236, 205, 117), self.pequena)
        self.texto("CARRERA  " + nivel.prisionero.carrera.get_estado(), 651, 110, (164, 201, 232), self.pequena)
        area = pygame.Rect(*ORIGEN, COLUMNAS * TAMANO, FILAS * TAMANO)
        pygame.draw.rect(self.pantalla, (28, 42, 53), area)
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                rect = pygame.Rect(ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO, TAMANO, TAMANO)
                pygame.draw.rect(self.pantalla, (33, 48, 60), rect, 1)
        for camara in nivel.camaras:
            self._dibujar_vision(camara.posicion, camara.angulo, camara.alcance, camara.apertura, nivel.muros, (241, 184, 79))
        guardia = nivel.guardia
        self._dibujar_vision(guardia.get_posicion(), guardia.angulo, guardia.alcance, guardia.apertura, nivel.muros, (242, 102, 113))
        for muro in nivel.muros:
            rect = pygame.Rect(muro[0] + ORIGEN[0], muro[1] + ORIGEN[1], muro[2], muro[3])
            pygame.draw.rect(self.pantalla, (62, 78, 90), rect)
            pygame.draw.rect(self.pantalla, (77, 94, 107), rect, 1)
            pygame.draw.line(self.pantalla, (90, 104, 116), rect.topleft, rect.topright)
        salida = self.punto(nivel.salida.posicion)
        color_salida = (103, 222, 176) if nivel.prisionero.tiene_llave() else (93, 126, 117)
        pygame.draw.rect(self.pantalla, color_salida, (salida[0] - 14, salida[1] - 15, 28, 30), 3, border_radius=3)
        self.texto("SALIDA", salida[0] - 27, salida[1] + 20, color_salida, self.pequena)
        if nivel.llave.disponible:
            x, y = self.punto(nivel.llave.posicion)
            pygame.draw.circle(self.pantalla, (246, 210, 102), (x - 5, y), 6, 3)
            pygame.draw.line(self.pantalla, (246, 210, 102), (x, y), (x + 13, y), 4)
            pygame.draw.line(self.pantalla, (246, 210, 102), (x + 10, y), (x + 10, y + 6), 3)
            self.texto("LLAVE", x - 22, y + 18, (246, 210, 102), self.pequena)
        for camara in nivel.camaras:
            x, y = self.punto(camara.posicion)
            pygame.draw.line(self.pantalla, (152, 169, 179), (x, y - 18), (x, y - 7), 3)
            pygame.draw.rect(self.pantalla, (244, 190, 93), (x - 10, y - 8, 20, 12), border_radius=3)
            pygame.draw.circle(self.pantalla, (37, 43, 48), (x, y + 2), 5)
            pygame.draw.circle(self.pantalla, (101, 159, 180), (x, y + 2), 2)
            self.texto("CÁMARA", x - 30, y - 42, (244, 190, 93), self.pequena)
        gx, gy = self.punto(guardia.get_posicion())
        paso_guardia = round(math.sin(nivel.tiempo * 11) * 3)
        self._dibujar_stickman((gx, gy), (242, 102, 113), paso_guardia)
        px, py = self.punto(nivel.prisionero.get_posicion())
        paso_prisionero = round(math.sin(nivel.tiempo * 14) * 3) if nivel.teclas else 0
        self._dibujar_stickman((px, py), (101, 234, 204), paso_prisionero)
        self.texto("WASD / FLECHAS  Mover     SHIFT  Correr     P / ESC  Pausa", 69, 680, fuente=self.pequena)
        self.texto("Evita las zonas de visión. Los muros te ocultan. Contactar al guardia también te captura.", 69, 709, (139, 159, 178), self.pequena)
        if juego.estado.nombre != "JUGANDO":
            self._dibujar_panel_estado(juego)

    def _dibujar_panel_estado(self, juego):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((5, 10, 18, 195))
        self.pantalla.blit(capa, (0, 0))
        pygame.draw.rect(self.pantalla, (26, 40, 53), (245, 250, 510, 235), border_radius=16)
        nombre = juego.estado.nombre
        if nombre == "PAUSA":
            titulo = "PARTIDA EN PAUSA"
            detalle = "La vigilancia y tu habilidad están detenidas."
            accion = "P o ESC para continuar"
            color = (182, 212, 242)
        elif nombre == "VICTORIA":
            titulo = "¡ESCAPASTE DEL PABELLÓN!"
            detalle = f"Nivel completado · {juego.panel.valor} puntos"
            accion = "R para volver a jugar"
            color = (111, 226, 188)
        else:
            titulo = "TE HAN DETECTADO"
            detalle = "Busca otra ruta y observa la vigilancia."
            accion = "R para intentarlo de nuevo"
            color = (250, 142, 147)
        self.texto(titulo, 275, 286, color, self.mediana)
        self.texto(detalle, 275, 343)
        self.texto(accion, 275, 398, (236, 205, 117))
        self.texto("Cierra la ventana para salir", 275, 438, (139, 159, 178), self.pequena)
