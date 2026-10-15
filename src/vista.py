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
        self.texto(f"NIVEL {nivel.indice + 1} / {nivel.total_niveles}  ·  {nivel.nombre.upper()}",
                   70, 66, (139, 159, 178), self.pequena)
        self.texto(f"PUNTOS  {juego.panel.valor:04d}", 738, 28, (111, 226, 188), self.mediana)
        self.texto(f"TIEMPO  {nivel.tiempo:05.1f} s", 740, 62, (139, 159, 178), self.pequena)
        llave = "LLAVE OBTENIDA · BUSCA LA SALIDA" if nivel.prisionero.tiene_llave() else "OBJETIVO · CONSIGUE LA LLAVE Y ESCAPA"
        if nivel.combate and not nivel.combate.jefe.derrotado:
            llave = "DERROTA AL ALCAIDE · ESPACIO o IJKL para disparar"
        self.texto(llave, 70, 110, (236, 205, 117), self.pequena)
        self.texto("CARRERA  " + nivel.prisionero.carrera.get_estado(), 651, 110, (164, 201, 232), self.pequena)
        area = pygame.Rect(*ORIGEN, COLUMNAS * TAMANO, FILAS * TAMANO)
        pygame.draw.rect(self.pantalla, (45, 31, 43) if nivel.es_final else (28, 42, 53), area)
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                rect = pygame.Rect(ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO, TAMANO, TAMANO)
                pygame.draw.rect(self.pantalla, (33, 48, 60), rect, 1)
        for camara in nivel.camaras:
            self._dibujar_vision(camara.posicion, camara.angulo, camara.alcance, camara.apertura, nivel.muros, (241, 184, 79))
        for guardia in nivel.guardias:
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
        paso_guardia = round(math.sin(nivel.tiempo * 11) * 3)
        for guardia in nivel.guardias:
            self._dibujar_stickman(self.punto(guardia.get_posicion()), (242, 102, 113), paso_guardia)
        if nivel.combate:
            self._dibujar_combate(nivel)
        px, py = self.punto(nivel.prisionero.get_posicion())
        paso_prisionero = round(math.sin(nivel.tiempo * 14) * 3) if nivel.teclas else 0
        if not nivel.combate or nivel.combate.inmune <= 0 or int(nivel.tiempo * 12) % 2 == 0:
            self._dibujar_stickman((px, py), (101, 234, 204), paso_prisionero)
        self.texto("WASD / FLECHAS  Mover     SHIFT  Correr     P / ESC  Pausa" +
                   ("     ESPACIO / IJKL  Disparar" if nivel.es_final else ""), 69, 680, fuente=self.pequena)
        consejo = "Evita las zonas de visión. Los muros te ocultan. Contactar al guardia también te captura."
        if nivel.es_final:
            consejo = "Espacio apunta al jefe; IJKL fija la dirección. Esquiva los avisos rojos. Tras vencerlo, recoge la llave."
        self.texto(consejo, 69, 709, (139, 159, 178), self.pequena)
        if juego.estado.nombre != "JUGANDO":
            self._dibujar_panel_estado(juego)

    def _dibujar_combate(self, nivel):
        combate = nivel.combate
        jefe = combate.jefe
        self.texto(f"VIDA  {combate.vida} / {combate.vida_maxima}", 70, 86, (255, 147, 161), self.pequena)
        self.texto("ALCAIDE" if not jefe.derrotado else "DERROTADO", 360, 86, (216, 167, 198), self.pequena)
        pygame.draw.rect(self.pantalla, (65, 42, 60), (452, 91, 480, 10), border_radius=5)
        ancho = round(480 * jefe.vida / jefe.vida_maxima)
        if ancho:
            pygame.draw.rect(self.pantalla, (240, 100, 133), (452, 91, ancho, 10), border_radius=5)
        if not jefe.derrotado:
            x, y = self.punto(jefe.posicion)
            if jefe.aviso > 0:
                color = (255, 178, 104)
                pygame.draw.circle(self.pantalla, color, (x, y), jefe.radio + 12, 2)
                if jefe.patron % 3 == 2:
                    destino = self.punto(jefe.objetivo)
                    pygame.draw.line(self.pantalla, (243, 96, 122), (x, y), destino, 3)
                    pygame.draw.circle(self.pantalla, color, destino, 23, 2)
                self.texto(jefe.ataque, 360, 661, color, self.pequena)
            else:
                self.texto(f"FASE {jefe.fase} / 2  ·  " + ("¡EMBESTIDA!" if jefe.destino else "EL ALCAIDE"),
                           360, 661, (216, 167, 198), self.pequena)
            # Un alcaide monstruoso original: gorra, lágrimas y uniforme de rayas.
            pygame.draw.ellipse(self.pantalla, (20, 17, 27), (x - 36, y + 20, 72, 16))
            piel = (255, 230, 232) if jefe.golpe > 0 else ((190, 111, 147) if jefe.fase == 1 else (227, 105, 128))
            pygame.draw.ellipse(self.pantalla, (28, 22, 38), (x - 29, y - 12, 58, 49))
            pygame.draw.ellipse(self.pantalla, piel, (x - 27, y - 33, 54, 54))
            for lado in (-1, 1):
                pygame.draw.circle(self.pantalla, (23, 22, 38), (x + lado * 11, y - 10), 7)
                pygame.draw.line(self.pantalla, (106, 194, 226), (x + lado * 11, y - 4), (x + lado * 14, y + 12), 4)
                pygame.draw.circle(self.pantalla, (239, 218, 227), (x + lado * 12, y - 12), 2)
                pygame.draw.circle(self.pantalla, piel, (x + lado * 30, y + 12), 9)
            pygame.draw.ellipse(self.pantalla, (49, 22, 39), (x - 7, y + 4, 14, 10))
            pygame.draw.rect(self.pantalla, (39, 49, 71), (x - 27, y - 38, 54, 13), border_radius=4)
            pygame.draw.rect(self.pantalla, (226, 190, 102), (x - 5, y - 36, 10, 8), border_radius=2)
            for fila in range(3):
                pygame.draw.line(self.pantalla, (141, 146, 171), (x - 18, y + 20 + fila * 6), (x + 18, y + 20 + fila * 6), 3)
        for tiro in combate.proyectiles:
            x, y = self.punto(tiro.posicion)
            color = (255, 112, 145) if tiro.enemigo else (109, 234, 244)
            pygame.draw.circle(self.pantalla, (22, 17, 33), (x, y), round(tiro.radio + 2))
            pygame.draw.circle(self.pantalla, color, (x, y), round(tiro.radio))
            pygame.draw.circle(self.pantalla, (255, 235, 240), (x - 2, y - 2), 2)

    def _dibujar_panel_estado(self, juego):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((5, 10, 18, 195))
        self.pantalla.blit(capa, (0, 0))
        pygame.draw.rect(self.pantalla, (26, 40, 53), (220, 250, 560, 250), border_radius=16)
        nombre = juego.estado.nombre
        if nombre == "PAUSA":
            titulo = "PARTIDA EN PAUSA"
            detalle = "La vigilancia y tu habilidad están detenidas."
            accion = "P o ESC para continuar"
            color = (182, 212, 242)
        elif nombre == "VICTORIA":
            titulo = "¡ERES LIBRE!"
            detalle = f"4 niveles y el Alcaide vencidos · {juego.panel.valor} puntos"
            accion = "R para volver a jugar"
            color = (111, 226, 188)
        elif nombre == "NIVEL_COMPLETADO":
            titulo = f"¡NIVEL {juego.indice_nivel + 1} COMPLETADO!"
            detalle = f"Siguiente: {juego.nivel.configuracion_siguiente}"
            accion = "ENTER para continuar · N para empezar de cero"
            color = (111, 226, 188)
        else:
            titulo = "EL ALCAIDE TE DERROTÓ" if juego.nivel.es_final else "TE HAN DETECTADO"
            detalle = "Esquiva los avisos y usa la carrera." if juego.nivel.es_final else "Busca otra ruta y observa la vigilancia."
            accion = "R: reintentar este nivel · N: empezar de cero"
            color = (250, 142, 147)
        self.texto(titulo, 247, 286, color, self.mediana)
        self.texto(detalle, 247, 343)
        self.texto(accion, 247, 398, (236, 205, 117), self.pequena)
        self.texto("Cierra la ventana para salir", 247, 448, (139, 159, 178), self.pequena)
