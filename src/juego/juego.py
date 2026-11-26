"""Coordinador principal: menú, cinemática, sigilo estratégico y Boss Run."""
from collections import deque
import json
import math
from pathlib import Path

import pygame
from pygame import Rect

from src.entidades.personajes import GuardiaCentinela, GuardiaPatrulla, Prisionero
from src.escenario.mapa import Mapa, TAMANO_CELDA
from src.escenario.nivel import Nivel
from src.escenario.seguridad import Camara, Llave, PanelSeguridad, Puerta
from src.escenario.sistema_colisiones import SistemaColisiones
from src.juego.puntaje import Puntaje
from src.patrones.creadores import CreadorCentinela, CreadorPatrulla
from src.patrones.estados import Derrota, Jugando, Pausa, Victoria


PUNTOS_LLAVE = 100
PUNTOS_NIVEL = 500
TAMANO_PRISIONERO = (22, 22)

ALCANCE_VISION = 215
SEMIANGULO_VISION_DEG = 34
COS_SEMIANGULO = math.cos(math.radians(SEMIANGULO_VISION_DEG))
ALCANCE_ESCUCHA = 46
TIEMPO_PERSECUCION = 4.5

DURACION_INTRO = 11.5
DURACION_AVISO_BOSS = 2.6

RUTA_NIVELES = Path(__file__).resolve().parents[2] / "data" / "niveles.json"

CREADORES_GUARDIA = {
    "patrulla": CreadorPatrulla,
    "centinela": CreadorCentinela,
}


def _cargar_datos_niveles():
    """Lee la configuración de niveles desde data/niveles.json con manejo de errores."""
    try:
        with open(RUTA_NIVELES, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"No se encontró el archivo de niveles: {RUTA_NIVELES}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"El archivo {RUTA_NIVELES} no contiene un JSON válido.") from exc

    niveles = datos.get("niveles")
    if not isinstance(niveles, list) or not niveles:
        raise ValueError("El JSON de niveles debe incluir una lista no vacía en 'niveles'.")
    return niveles


def _pos_celda(columna, fila, tamano=TAMANO_PRISIONERO):
    x = columna * TAMANO_CELDA + (TAMANO_CELDA - tamano[0]) // 2
    y = fila * TAMANO_CELDA + (TAMANO_CELDA - tamano[1]) // 2
    return (x, y)


def _centro_celda(columna, fila):
    return (columna * TAMANO_CELDA + TAMANO_CELDA // 2, fila * TAMANO_CELDA + TAMANO_CELDA // 2)


def _rect_celda(columna, fila, cols=1, filas=1):
    return Rect(columna * TAMANO_CELDA, fila * TAMANO_CELDA, cols * TAMANO_CELDA, filas * TAMANO_CELDA)


def _tiene_linea_de_vision(origen, destino, muros):
    for muro in muros:
        if muro.clipline(origen, destino):
            return False
    return True


def _camino_recto_despejado(rect_origen, destino, muros):
    """Comprueba que todo el cuerpo del personaje pueda avanzar en línea recta sin chocar muros."""
    dx = destino[0] - rect_origen.centerx
    dy = destino[1] - rect_origen.centery
    if abs(dx) < 1 and abs(dy) < 1:
        return True
    esquinas = (rect_origen.topleft, rect_origen.topright, rect_origen.bottomleft, rect_origen.bottomright)
    for px, py in esquinas:
        fin = (px + dx, py + dy)
        for muro in muros:
            if muro.inflate(-2, -2).clipline((px, py), fin):
                return False
    return True


def _objetivo_navegacion_segura(rect_g, destino_pixel, muros, muros_celdas, cols, filas):
    """Calcula un punto intermedio libre de colisiones alineando al centro del pasillo antes de girar."""
    if _camino_recto_despejado(rect_g, destino_pixel, muros):
        return destino_pixel

    celda_g = (rect_g.centerx // TAMANO_CELDA, rect_g.centery // TAMANO_CELDA)
    celda_obj = (int(destino_pixel[0]) // TAMANO_CELDA, int(destino_pixel[1]) // TAMANO_CELDA)
    if celda_g == celda_obj:
        return destino_pixel

    sig = _siguiente_paso_bfs(celda_g, celda_obj, muros_celdas, cols, filas)
    centro_actual = _centro_celda(*celda_g)
    centro_sig = _centro_celda(*sig)

    # Alinear el eje perpendicular al centro de la celda actual antes de doblar (margen > 5 vs parada <= 2)
    if sig[0] == celda_g[0] and sig[1] != celda_g[1]:
        if abs(rect_g.centerx - centro_actual[0]) > 5:
            return (centro_actual[0], rect_g.centery)
    elif sig[1] == celda_g[1] and sig[0] != celda_g[0]:
        if abs(rect_g.centery - centro_actual[1]) > 5:
            return (rect_g.centerx, centro_actual[1])

    return centro_sig


def _detecta_en_cono(guardia, destino, muros):
    """Comprueba visión direccional en cono o cercanía inmediata, bloqueada por muros."""
    origen = guardia.get_rect().center
    dx = destino[0] - origen[0]
    dy = destino[1] - origen[1]
    dist = math.hypot(dx, dy)
    if dist > ALCANCE_VISION:
        return False
    if dist <= ALCANCE_ESCUCHA:
        return _tiene_linea_de_vision(origen, destino, muros)

    mx, my = guardia.get_mirada()
    cos_ang = (dx * mx + dy * my) / max(dist, 1e-6)
    return cos_ang >= COS_SEMIANGULO and _tiene_linea_de_vision(origen, destino, muros)


def _siguiente_paso_bfs(inicio, objetivo, muros_celdas, cols, filas):
    """Encuentra la siguiente celda transitable para rodear obstáculos sin trabarse."""
    if inicio == objetivo:
        return objetivo
    cola = deque([(inicio, None)])
    visitados = {inicio}
    while cola:
        actual, primer_paso = cola.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            vecino = (actual[0] + dx, actual[1] + dy)
            if not (0 <= vecino[0] < cols and 0 <= vecino[1] < filas):
                continue
            if vecino in muros_celdas or vecino in visitados:
                continue
            paso = vecino if primer_paso is None else primer_paso
            if vecino == objetivo:
                return paso
            visitados.add(vecino)
            cola.append((vecino, paso))
    return objetivo


NIVELES = _cargar_datos_niveles()


class Juego:
    def __init__(self, vista=None):
        self.__nivel_actual = None
        self.__config_nivel = None
        self.__muros_celdas = set()
        self.__estado_actual = None
        self.__puntaje = Puntaje()
        self.__puntos_inicio_nivel = 0
        self.__vista = vista
        self.__intro_restante = 0.0
        self.__intro_duracion = DURACION_INTRO
        self.__en_menu = True
        self.__opcion_menu = 0
        self.__salir = False

        # Memoria de persecución estratégica y mecánicas del Boss Run
        self.__persecuciones = {}
        self.__puestos_centinela = {}
        self.__boss_reloj = 0.0
        self.__boss_dash_ciclo = 0.0
        self.__boss_aturdido = 0.0
        self.__boss_alarma = 0.0
        self.__boss_mensaje = ""
        self.__boss_mensaje_t = 0.0

        self.cargar_nivel(1)
        self.__estado_actual = Jugando(self)

    def iniciar(self):
        self.__en_menu = False
        self.__puntaje.reiniciar()
        self.cargar_nivel(1)
        self.__iniciar_intro(DURACION_INTRO)
        self.__estado_actual = Jugando(self)

    def __iniciar_intro(self, duracion):
        self.__intro_duracion = duracion
        self.__intro_restante = duracion

    def cargar_nivel(self, numero):
        if numero < 1 or numero > len(NIVELES):
            raise ValueError(f"Nivel fuera de rango: {numero}")

        config = NIVELES[numero - 1]
        mapa = Mapa(config["plano"])
        colisiones = SistemaColisiones(mapa)

        px, py = _pos_celda(*config["prisionero"])
        prisionero = Prisionero(Rect(px, py, *TAMANO_PRISIONERO), colisiones)
        camaras = [Camara(_rect_celda(*zona)) for zona in config["camaras"]]
        llave = Llave(_rect_celda(*config["llave"]))
        puerta = Puerta(_rect_celda(*config["puerta"]))
        panel = PanelSeguridad(_rect_celda(*config["panel"]), camaras) if config.get("panel") else None

        nivel = Nivel(numero, mapa, colisiones, prisionero, camaras, llave, puerta, panel)
        self.__puestos_centinela = {}
        for g in config["guardias"]:
            creador = CREADORES_GUARDIA[g["tipo"]]()
            tamano = tuple(g.get("tamano", TAMANO_PRISIONERO))
            datos_guardia = {
                "posicion": _pos_celda(*g["posicion"], tamano),
                "tamano": tamano,
                "velocidad": g.get("velocidad", 112.0),
            }
            if "ruta" in g:
                datos_guardia["ruta"] = [_centro_celda(*punto) for punto in g["ruta"]]
            creador.incorporar(nivel, datos_guardia)
            guardia_nuevo = nivel.get_guardias()[-1]
            if isinstance(guardia_nuevo, GuardiaCentinela):
                self.__puestos_centinela[id(guardia_nuevo)] = tuple(g["posicion"])

        self.__nivel_actual = nivel
        self.__config_nivel = config
        self.__muros_celdas = {(m.x // TAMANO_CELDA, m.y // TAMANO_CELDA) for m in mapa.get_muros()}
        self.__puntos_inicio_nivel = self.__puntaje.get_valor()
        self.__persecuciones = {}
        self.__boss_reloj = 0.0
        self.__boss_dash_ciclo = 0.0
        self.__boss_aturdido = 0.0
        self.__boss_alarma = 0.0
        self.__boss_mensaje = ""
        self.__boss_mensaje_t = 0.0

        if config.get("es_boss_run") and not self.__en_menu:
            self.__iniciar_intro(DURACION_AVISO_BOSS)

    def cambiar_estado(self, estado):
        self.__estado_actual = estado

    def procesar_evento(self, evento):
        if self.__en_menu:
            self.__manejar_evento_menu(evento)
            return

        if (
            self.__intro_restante > 0
            and evento.type == pygame.KEYDOWN
            and evento.key in (pygame.K_RETURN, pygame.K_SPACE)
        ):
            self.__intro_restante = 0.0
            return

        if (
            isinstance(self.__estado_actual, (Pausa, Derrota, Victoria))
            and evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_m
        ):
            self.__en_menu = True
            self.__opcion_menu = 0
            return

        self.__estado_actual.manejar_evento(evento)

    def __manejar_evento_menu(self, evento):
        if evento.type == pygame.MOUSEMOTION and self.__vista is not None:
            opcion = self.__vista.opcion_menu_en_punto(evento.pos)
            if opcion is not None:
                self.__opcion_menu = opcion
            return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.__vista is not None:
            opcion = self.__vista.opcion_menu_en_punto(evento.pos)
            if opcion is not None:
                self.__opcion_menu = opcion
                self.__ejecutar_opcion_menu()
            return

        if evento.type != pygame.KEYDOWN:
            return

        if evento.key in (pygame.K_UP, pygame.K_w):
            self.__opcion_menu = (self.__opcion_menu - 1) % 2
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.__opcion_menu = (self.__opcion_menu + 1) % 2
        elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.__ejecutar_opcion_menu()
        elif evento.key == pygame.K_ESCAPE:
            self.__salir = True

    def __ejecutar_opcion_menu(self):
        if self.__opcion_menu == 0:
            self.iniciar()
        else:
            self.__salir = True

    def update(self, dt):
        if self.__en_menu:
            return
        if self.__intro_restante > 0:
            if isinstance(self.__estado_actual, Jugando):
                self.__intro_restante = max(0.0, self.__intro_restante - dt)
                # Durante la intro del nivel 1, los guardias patrullan el fondo para dar vida a la escena
                if not self.es_boss_run():
                    for guardia in self.__nivel_actual.get_guardias():
                        guardia.update(dt)
            return
        self.__estado_actual.update(dt)

    def __registrar_alerta(self, guardia, posicion_pixel):
        celda = (int(posicion_pixel[0]) // TAMANO_CELDA, int(posicion_pixel[1]) // TAMANO_CELDA)
        self.__persecuciones[id(guardia)] = [celda, (posicion_pixel[0], posicion_pixel[1]), TIEMPO_PERSECUCION]

    def __actualizar_boss_run(self, dt):
        nivel = self.__nivel_actual
        prisionero = nivel.get_prisionero()
        muros = nivel.get_mapa().get_muros()
        ancho, alto = nivel.get_mapa().get_dimensiones()
        cols, filas = ancho // TAMANO_CELDA, alto // TAMANO_CELDA

        self.__boss_reloj += dt
        if self.__boss_aturdido > 0:
            self.__boss_aturdido = max(0.0, self.__boss_aturdido - dt)
        if self.__boss_alarma > 0:
            self.__boss_alarma = max(0.0, self.__boss_alarma - dt)
        if self.__boss_mensaje_t > 0:
            self.__boss_mensaje_t = max(0.0, self.__boss_mensaje_t - dt)

        # Cámaras del Boss Run oscilan cada 2.1 s (si el panel no las ha apagado)
        panel = nivel.get_panel()
        if panel is None or not panel.esta_activo():
            encendidas = (int(self.__boss_reloj / 2.1) % 2) == 0
            for cam in nivel.get_camaras():
                if encendidas:
                    cam.activar()
                else:
                    cam.desactivar()

        # Fase 2 (con llave): ciclo de embestidas periódicas del Alcaide
        if prisionero.tiene_llave() and self.__boss_aturdido <= 0:
            self.__boss_dash_ciclo = (self.__boss_dash_ciclo + dt) % 3.6
        else:
            self.__boss_dash_ciclo = 0.0

        rect_preso = prisionero.get_rect()
        celda_preso = (rect_preso.centerx // TAMANO_CELDA, rect_preso.centery // TAMANO_CELDA)

        for guardia in nivel.get_guardias():
            if isinstance(guardia, GuardiaPatrulla):
                # El Alcaide
                if self.__boss_aturdido > 0:
                    guardia.alertar(guardia.get_rect().center, factor_velocidad=0.0)
                    continue

                factor = 1.12 if prisionero.tiene_llave() else 1.0
                if prisionero.tiene_llave() and self.__boss_dash_ciclo >= 2.95:
                    factor = 1.40  # Embestida corta tras aviso visual
                elif self.__boss_alarma > 0:
                    factor = max(factor, 1.18)

                rect_g = guardia.get_rect()
                punto = _objetivo_navegacion_segura(
                    rect_g, rect_preso.center, muros, self.__muros_celdas, cols, filas
                )
                guardia.alertar(punto, factor_velocidad=factor)
            else:
                # Escolta centinela del tramo final: solo se alerta si te ve en su cono
                if _detecta_en_cono(guardia, rect_preso.center, muros):
                    self.__registrar_alerta(guardia, rect_preso.center)
                self.__guiar_guardia_sigilo(guardia, dt, muros, cols, filas)

    def __guiar_guardia_sigilo(self, guardia, dt, muros, cols, filas):
        clave = id(guardia)
        rect_g = guardia.get_rect()

        if clave in self.__persecuciones:
            _, pos_obj, restante = self.__persecuciones[clave]
            restante -= dt
            if restante <= 0 or math.hypot(pos_obj[0] - rect_g.centerx, pos_obj[1] - rect_g.centery) <= 10:
                del self.__persecuciones[clave]
                guardia.dejar_alerta()
            else:
                self.__persecuciones[clave][2] = restante
                punto = _objetivo_navegacion_segura(
                    rect_g, pos_obj, muros, self.__muros_celdas, cols, filas
                )
                guardia.alertar(punto, factor_velocidad=1.24)
            return

        # Regreso suave sorteando muros: tanto patrullas como centinelas vuelven sin chocarse
        if isinstance(guardia, GuardiaCentinela) and clave in self.__puestos_centinela:
            destino_regreso = _centro_celda(*self.__puestos_centinela[clave])
        elif isinstance(guardia, GuardiaPatrulla):
            destino_regreso = guardia.get_destino_patrulla()
        else:
            guardia.dejar_alerta()
            return

        if _camino_recto_despejado(rect_g, destino_regreso, muros):
            guardia.dejar_alerta()
        else:
            punto = _objetivo_navegacion_segura(
                rect_g, destino_regreso, muros, self.__muros_celdas, cols, filas
            )
            guardia.guiar_a(punto)

    def actualizar_nivel(self, dt):
        nivel = self.__nivel_actual
        colisiones = nivel.get_colisiones()
        prisionero = nivel.get_prisionero()
        muros = nivel.get_mapa().get_muros()
        ancho, alto = nivel.get_mapa().get_dimensiones()
        cols, filas = ancho // TAMANO_CELDA, alto // TAMANO_CELDA

        rect_preso = prisionero.get_rect()

        if self.es_boss_run():
            self.__actualizar_boss_run(dt)
        else:
            # Visión direccional en cono (bloqueada por muros)
            for guardia in nivel.get_guardias():
                if _detecta_en_cono(guardia, rect_preso.center, muros):
                    self.__registrar_alerta(guardia, rect_preso.center)
                self.__guiar_guardia_sigilo(guardia, dt, muros, cols, filas)

        # Polimorfismo: una única llamada update(dt) para todos los personajes.
        for personaje in nivel.get_personajes():
            personaje.update(dt)

        panel = nivel.get_panel()
        if panel is not None:
            panel.update(dt)

        rect_preso = prisionero.get_rect()

        # Panel de seguridad: apaga cámaras; en sigilo alerta guardias, en Boss Run aturde al Alcaide.
        if panel is not None and colisiones.toca(rect_preso, panel.get_rect()):
            if panel.activar():
                if self.es_boss_run():
                    self.__boss_aturdido = 1.8
                    self.__boss_mensaje = "¡SOBRECARGA! ALCAIDE ATURDIDO"
                    self.__boss_mensaje_t = 2.0
                else:
                    for guardia in nivel.get_guardias():
                        self.__registrar_alerta(guardia, rect_preso.center)

        # Cámaras activas
        for camara in nivel.get_camaras():
            if camara.detectar(rect_preso):
                if self.es_boss_run():
                    self.__boss_alarma = 1.8
                    self.__boss_mensaje = "¡ALARMA! EL ALCAIDE ACELERA"
                    self.__boss_mensaje_t = 1.6
                else:
                    for guardia in nivel.get_guardias():
                        self.__registrar_alerta(guardia, rect_preso.center)
                break

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
            if self.es_boss_run():
                self.__boss_mensaje = "¡LLAVE OBTENIDA! EL ALCAIDE ENFURECE"
                self.__boss_mensaje_t = 2.4

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
        if self.__en_menu:
            self.__vista.dibujar_menu(self)
        elif isinstance(self.__estado_actual, Pausa):
            self.__vista.dibujar_pausa()
        elif isinstance(self.__estado_actual, Victoria):
            self.__vista.dibujar_resultado(True, len(NIVELES))
        elif isinstance(self.__estado_actual, Derrota):
            self.__vista.dibujar_resultado(False, len(NIVELES))

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

    def esta_en_menu(self):
        return self.__en_menu

    def get_opcion_menu(self):
        return self.__opcion_menu

    def quiere_salir(self):
        return self.__salir

    def es_boss_run(self):
        return bool(self.__config_nivel and self.__config_nivel.get("es_boss_run"))

    def get_estado_boss(self):
        if not self.es_boss_run():
            return None
        nivel = self.__nivel_actual
        preso = nivel.get_prisionero()
        alcaide = next((g for g in nivel.get_guardias() if isinstance(g, GuardiaPatrulla)), None)
        dist = 400.0
        if alcaide is not None:
            pa, pp = alcaide.get_rect().center, preso.get_rect().center
            dist = math.hypot(pa[0] - pp[0], pa[1] - pp[1])
        proximidad = max(0.0, min(1.0, 1.0 - (dist - 30.0) / 360.0))

        if self.__boss_aturdido > 0:
            estado = "aturdido"
        elif preso.tiene_llave() and self.__boss_dash_ciclo >= 2.95:
            estado = "embistiendo"
        elif preso.tiene_llave() and self.__boss_dash_ciclo >= 2.30:
            estado = "cargando"
        elif self.__boss_alarma > 0:
            estado = "alarma"
        else:
            estado = "furia" if preso.tiene_llave() else "persiguiendo"

        return {
            "fase": 2 if preso.tiene_llave() else 1,
            "estado": estado,
            "proximidad": proximidad,
            "mensaje": self.__boss_mensaje if self.__boss_mensaje_t > 0 else "",
        }

    def get_config_nivel(self):
        return self.__config_nivel

    def get_total_niveles(self):
        return len(NIVELES)

    def get_intro_progreso(self):
        if self.__en_menu or self.__intro_restante <= 0:
            return None
        return 1.0 - self.__intro_restante / self.__intro_duracion

    def get_nivel(self):
        return self.__nivel_actual

    def get_puntaje(self):
        return self.__puntaje

    def get_estado(self):
        return self.__estado_actual
