"""Vista Pygame. Las reglas se conservan fuera de esta clase."""
import math
import pygame
from .geometria import poligono_vision
from .mapa import TAMANO, COLUMNAS, FILAS

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
        pygame.draw.ellipse(self.pantalla, (15, 25, 33), (x - 9, y + 9, 18, 5))

        cabeza = (x, y - 7)
        torso = ((x, y - 2), (x, y + 4))
        brazo_izquierdo = ((x, y), (x - 8, y + 3))
        brazo_derecho = ((x, y), (x + 8, y + 3))
        pierna_izquierda = ((x, y + 4), (x - 5 + paso, y + 9))
        pierna_derecha = ((x, y + 4), (x + 5 - paso, y + 9))

        for inicio, fin in (torso, brazo_izquierdo, brazo_derecho,
                            pierna_izquierda, pierna_derecha):
            pygame.draw.line(self.pantalla, (14, 27, 35), inicio, fin, 5)
            pygame.draw.line(self.pantalla, color, inicio, fin, 3)

        pygame.draw.circle(self.pantalla, (14, 27, 35), cabeza, 5)
        pygame.draw.circle(self.pantalla, color, cabeza, 4)

    def _dibujar_vision(self, origen, angulo, alcance, apertura, muros, color):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        puntos = [self.punto(punto) for punto in
                  poligono_vision(origen, angulo, alcance, apertura, muros)]
        pygame.draw.polygon(capa, (*color, 55), puntos)
        pygame.draw.lines(capa, (*color, 120), False, puntos[1:], 1)
        self.pantalla.blit(capa, (0, 0))

    def dibujar(self, juego):
        nivel = juego.nivel
        self.pantalla.fill((13, 21, 31))
        self._dibujar_encabezado(juego)
        self._dibujar_mapa(nivel)
        if nivel.celda:
            self._dibujar_celda(nivel.celda)
        self._dibujar_objetivos(nivel)
        for camara in nivel.camaras:
            self._dibujar_camara(camara)
        paso_guardia = round(math.sin(nivel.tiempo * 11) * 3)
        for guardia in nivel.guardias:
            self._dibujar_guardia(guardia, paso_guardia)
        if nivel.combate:
            self._dibujar_combate(nivel)
        paso_prisionero = round(math.sin(nivel.tiempo * 14) * 2) if nivel.prisionero.movimiento != "QUIETO" else 0
        if not nivel.combate or nivel.combate.inmune <= 0 or int(nivel.tiempo * 12) % 2 == 0:
            self._dibujar_stickman(self.punto(nivel.prisionero.get_posicion()),
                                  (101, 234, 204), paso_prisionero)
        self._dibujar_controles(nivel)
        if juego.estado.nombre != "JUGANDO":
            self._dibujar_panel_estado(juego)

    def _dibujar_encabezado(self, juego):
        nivel = juego.nivel
        self.texto("FUGA DE LA PRISIÓN", 68, 24, fuente=self.titulo)
        self.texto(f"NIVEL {nivel.indice + 1} / {nivel.total_niveles}  ·  {nivel.nombre.upper()}",
                   70, 66, (139, 159, 178), self.pequena)
        self.texto(f"PUNTOS  {juego.panel.valor:04d}", 738, 28, (111, 226, 188), self.mediana)
        self.texto(f"TIEMPO  {nivel.tiempo:05.1f} s", 740, 62, (139, 159, 178), self.pequena)
        if not nivel.es_final:
            movimiento = nivel.prisionero.movimiento
            ruido = {"QUIETO": "NINGUNO", "SIGILO": "BAJO", "CAMINA": "MEDIO", "CORRE": "ALTO"}[movimiento]
            perseguido = any(g.modo == "PERSIGUE" for g in nivel.guardias)
            investigan = any(g.modo != "PATRULLA" for g in nivel.guardias)
            alarma = any(c.activa for c in nivel.camaras)
            estado = "ALARMA · GUARDIAS ALERTADOS" if alarma else (
                "¡TE PERSIGUEN!" if perseguido else ("INVESTIGAN LA ZONA" if investigan else "PATRULLA TRANQUILA"))
            self.texto("RUIDO  " + ruido, 70, 86, (164, 201, 232), self.pequena)
            self.texto(estado, 360, 86, (250, 142, 147) if perseguido else (236, 205, 117), self.pequena)
        llave = "LLAVE OBTENIDA · BUSCA LA SALIDA" if nivel.prisionero.tiene_llave() else "OBJETIVO · CONSIGUE LA LLAVE Y ESCAPA"
        if nivel.combate and not nivel.combate.jefe.derrotado:
            llave = "DERROTA AL ALCAIDE · ESPACIO o IJKL para disparar"
        elif nivel.celda and not nivel.celda.abierta:
            llave = "SAL DE TU CELDA · ACÉRCATE A LA PUERTA Y MANTÉN E (2 s)"
        elif nivel.indice == 2:
            llave = ("LLAVE OBTENIDA · ATAJOS ABIERTOS; BUSCA LA SALIDA" if nivel.prisionero.tiene_llave()
                     else "OBJETIVO · LA LLAVE DEL ALA NORTE ABRE LOS ATAJOS")
        self.texto(llave, 70, 110, (236, 205, 117), self.pequena)
        self.texto("CARRERA  " + nivel.prisionero.carrera.get_estado(), 651, 110, (164, 201, 232), self.pequena)

    def _dibujar_mapa(self, nivel):
        area = pygame.Rect(*ORIGEN, COLUMNAS * TAMANO, FILAS * TAMANO)
        pygame.draw.rect(self.pantalla, (45, 31, 43) if nivel.es_final else (28, 42, 53), area)
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                rect = pygame.Rect(ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO, TAMANO, TAMANO)
                pygame.draw.rect(self.pantalla, (33, 48, 60), rect, 1)
        for camara in nivel.camaras:
            self._dibujar_vision(camara.posicion, camara.angulo, camara.alcance, camara.apertura, nivel.mapa.muros, (241, 184, 79))
        for muro in nivel.mapa.muros:
            rect = pygame.Rect(muro[0] + ORIGEN[0], muro[1] + ORIGEN[1], muro[2], muro[3])
            pygame.draw.rect(self.pantalla, (62, 78, 90), rect)
            pygame.draw.rect(self.pantalla, (77, 94, 107), rect, 1)
            pygame.draw.line(self.pantalla, (90, 104, 116), rect.topleft, rect.topright)
            if nivel.mapa.plano[int(muro[1] // TAMANO)][int(muro[0] // TAMANO)] == "P":
                pygame.draw.rect(self.pantalla, (100, 151, 181), rect, 3)
                for separacion in (8, 18, 28):
                    pygame.draw.line(self.pantalla, (143, 183, 204),
                                     (rect.x + separacion, rect.y + 3), (rect.x + separacion, rect.bottom - 3), 2)

    def _dibujar_objetivos(self, nivel):
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

    def _dibujar_celda(self, celda):
        x, y = self.punto(celda.posicion)
        if celda.abierta:
            pygame.draw.rect(self.pantalla, (103, 222, 176), (x - 17, y - 17, 34, 34), 2)
            return
        pygame.draw.rect(self.pantalla, (25, 33, 42), (x - 17, y - 17, 34, 34))
        for separacion in (-12, -4, 4, 12):
            pygame.draw.line(self.pantalla, (173, 188, 204),
                             (x + separacion, y - 17), (x + separacion, y + 17), 3)
        pygame.draw.rect(self.pantalla, (246, 210, 102), (x - 4, y - 5, 8, 10))
        self.texto(f"E · {celda.progreso / 2:.0%}", x - 28, y + 20, (246, 210, 102), self.pequena)

    def _dibujar_camara(self, camara):
        x, y = self.punto(camara.posicion)
        dx, dy = math.cos(camara.angulo), math.sin(camara.angulo)
        lente = (round(x + dx * 9), round(y + dy * 9))
        soporte = (round(x - dx * 10), round(y - dy * 10))
        pygame.draw.line(self.pantalla, (188, 201, 208), soporte, (x, y), 5)
        cuerpo = [(round(x + dx * largo - dy * ancho), round(y + dy * largo + dx * ancho))
                  for largo, ancho in ((-7, -6), (7, -6), (7, 6), (-7, 6))]
        pygame.draw.polygon(self.pantalla, (250, 100, 110) if camara.activa else (244, 190, 93), cuerpo)
        pygame.draw.line(self.pantalla, (37, 43, 48), (x, y), lente, 9)
        pygame.draw.circle(self.pantalla, (101, 159, 180), lente, 3)
        self.texto("CÁMARA", x - 30, y - 34, (244, 190, 93), self.pequena)

    def _dibujar_guardia(self, guardia, paso):
        x, y = self.punto(guardia.get_posicion())
        self._dibujar_stickman((x, y), (242, 102, 113), paso)
        mirada = (round(x + math.cos(guardia.angulo) * 12),
                  round(y - 7 + math.sin(guardia.angulo) * 12))
        pygame.draw.line(self.pantalla, (255, 205, 184), (x, y - 7), mirada, 2)
        marca = "!" if guardia.modo == "PERSIGUE" else ("?" if guardia.modo != "PATRULLA" else "")
        self.texto(marca, x - 5, y - 33, (255, 209, 108), self.mediana)

    def _dibujar_controles(self, nivel):
        self.texto("WASD / FLECHAS  Mover    CTRL  Sigilo    SHIFT  Correr    P / ESC  Pausa" +
                   ("     ESPACIO / IJKL  Disparar" if nivel.es_final else ("    E  Abrir celda" if nivel.celda else "")),
                   69, 680, fuente=self.pequena)
        consejo = "Correr hace ruido. Si te ven, huye y rompe la visión tras una pared. Solo el contacto te captura."
        if nivel.es_final:
            consejo = "Espacio apunta al jefe; IJKL fija la dirección. Esquiva los avisos rojos. Tras vencerlo, recoge la llave."
        self.texto(consejo, 69, 709, (139, 159, 178), self.pequena)

    def _dibujar_combate(self, nivel):
        combate = nivel.combate
        jefe = combate.jefe
        self.texto(f"VIDA  {combate.vida} / {combate.vida_maxima}", 70, 86, (255, 147, 161), self.pequena)
        self.texto(f"CAPAS  {jefe.capas_restantes} / 3", 310, 86, (216, 167, 198), self.pequena)
        for capa in range(jefe.capas_totales):
            rect = pygame.Rect(452 + capa * 162, 91, 156, 10)
            pygame.draw.rect(self.pantalla, (65, 42, 60), rect, border_radius=5)
            vida = 0
            if capa < jefe.capas_restantes - 1:
                vida = jefe.vida_por_capa
            elif capa == jefe.capas_restantes - 1:
                vida = jefe.vida_capa
            ancho = round(rect.width * vida / jefe.vida_por_capa)
            if ancho:
                color = ((255, 80, 107), (255, 154, 82), (198, 127, 244))[capa]
                pygame.draw.rect(self.pantalla, color, (rect.x, rect.y, ancho, rect.height), border_radius=5)
        if not jefe.derrotado:
            x, y = self.punto(jefe.posicion)
            if jefe.transicion > 0:
                self.texto(f"¡CAPA ROTA!  FASE {jefe.fase} · MÁS RÁPIDO Y MÁS PROYECTILES",
                           245, 661, (255, 182, 92), self.pequena)
            elif jefe.aviso > 0:
                color = (255, 178, 104)
                pygame.draw.circle(self.pantalla, color, (x, y), jefe.radio + 12, 2)
                if jefe.patron % 3 == 2:
                    destino = self.punto(jefe.objetivo)
                    pygame.draw.line(self.pantalla, (243, 96, 122), (x, y), destino, 3)
                    pygame.draw.circle(self.pantalla, color, destino, 23, 2)
                self.texto(jefe.ataque, 360, 661, color, self.pequena)
            else:
                self.texto(f"FASE {jefe.fase} / 3  ·  " + ("¡EMBESTIDA!" if jefe.destino else "EL ALCAIDE"),
                           360, 661, (216, 167, 198), self.pequena)
            # Un alcaide monstruoso original: gorra, lágrimas y uniforme de rayas.
            pygame.draw.ellipse(self.pantalla, (20, 17, 27), (x - 36, y + 20, 72, 16))
            piel = (255, 230, 232) if jefe.golpe > 0 else (
                (190, 111, 147), (227, 105, 128), (255, 78, 90))[jefe.fase - 1]
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
            titulo = "EL ALCAIDE TE DERROTÓ" if juego.nivel.es_final else "TE HAN ATRAPADO"
            detalle = "Esquiva los avisos y usa la carrera." if juego.nivel.es_final else "Usa Ctrl para acercarte con menos ruido."
            accion = "R: reintentar este nivel · N: empezar de cero"
            color = (250, 142, 147)
        self.texto(titulo, 247, 286, color, self.mediana)
        self.texto(detalle, 247, 343)
        self.texto(accion, 247, 398, (236, 205, 117), self.pequena)
        self.texto("Cierra la ventana para salir", 247, 448, (139, 159, 178), self.pequena)
