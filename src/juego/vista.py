"""Capa de presentación en Pygame: sprites, conos de visión, cinemática y HUD."""
import math
from pathlib import Path

import pygame

from src.entidades.personajes import Guardia, GuardiaPatrulla, Prisionero
from src.escenario.mapa import TAMANO_CELDA
from src.juego.juego import ALCANCE_VISION, SEMIANGULO_VISION_DEG


ANCHO = 900
ALTO = 660
ORIGEN = (50, 96)
RUTA_IMG = Path(__file__).resolve().parents[2] / "img"

DIRECCIONES = ("abajo", "izquierda", "derecha", "arriba")
SECUENCIA_PASO = (0, 1, 0, 2)

DECORACIONES_SUELO = {"rejilla", "papeles", "marca_suelo", "lona", "puerta_abierta"}
DECORACIONES_MURO = {"ventana", "muro_peligro", "tubo_muro", "alambre"}
BOTONES_MENU = (
    ("INICIAR JUEGO", pygame.Rect(310, 326, 280, 54)),
    ("SALIR", pygame.Rect(310, 400, 280, 54)),
)


def _cargar_imagen(ruta, tamano=None):
    imagen = pygame.image.load(str(ruta)).convert_alpha()
    if tamano and imagen.get_size() != tamano:
        imagen = pygame.transform.scale(imagen, tamano)
    return imagen


def _cargar_personaje(carpeta, prefijo, tamano):
    base = RUTA_IMG / carpeta
    frames = [_cargar_imagen(base / f"{prefijo}_{i:02d}.png", tamano) for i in range(1, 13)]
    return {direccion: frames[i * 3:(i + 1) * 3] for i, direccion in enumerate(DIRECCIONES)}


def _cargar_halo(ruta, tamano, alpha):
    origen = _cargar_imagen(ruta, (tamano, tamano))
    origen.set_alpha(alpha)
    halo = pygame.Surface((tamano, tamano))
    halo.fill((0, 0, 0))
    halo.blit(origen, (0, 0))
    return halo


def _crear_sombra(ancho, alto, horizontal=False, maximo=95):
    sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    largo = ancho if horizontal else alto
    for i in range(largo):
        alpha = round(maximo * (1 - i / largo) ** 1.4)
        if horizontal:
            pygame.draw.line(sombra, (6, 8, 14, alpha), (i, 0), (i, alto - 1))
        else:
            pygame.draw.line(sombra, (6, 8, 14, alpha), (0, i), (ancho - 1, i))
    return sombra


def _cargar_tilesets():
    t = (TAMANO_CELDA, TAMANO_CELDA)
    c = RUTA_IMG / "mapas" / "celda_v2"
    l = RUTA_IMG / "mapas" / "lavanderia_v2"
    p = RUTA_IMG / "mapas" / "patio_v2"
    a = RUTA_IMG / "mapas" / "arena_v2"

    llave_comun = _cargar_imagen(c / "pabellon_tiles_07.png", (34, 34))
    cam_off = _cargar_imagen(c / "pabellon_tiles_13.png", (30, 30))
    cam_on = _cargar_imagen(c / "pabellon_tiles_70.png", (30, 30))
    puerta_abierta = _cargar_imagen(c / "pabellon_tiles_05.png", t)
    caja_madera = _cargar_imagen(l / "tiles_38.png", t)

    celda = {
        "suelo": _cargar_imagen(c / "pabellon_tiles_01.png", t),
        "suelo_grieta": _cargar_imagen(c / "pabellon_tiles_02.png", t),
        "suelo_alt": _cargar_imagen(c / "pabellon_tiles_01.png", t),
        "muro": _cargar_imagen(c / "pabellon_tiles_03.png", t),
        "muro_alt": _cargar_imagen(c / "pabellon_tiles_19.png", t),
        "muro_peligro": _cargar_imagen(c / "pabellon_tiles_04.png", t),
        "ventana": _cargar_imagen(c / "pabellon_tiles_53.png", t),
        "lampara": _cargar_imagen(c / "pabellon_tiles_10.png", t),
        "puerta_abierta": puerta_abierta,
        "barrotes": _cargar_imagen(c / "pabellon_tiles_06.png", t),
        "llave": llave_comun,
        "salida": _cargar_imagen(c / "pabellon_tiles_08.png", t),
        "salida_bloqueada": _cargar_imagen(c / "pabellon_tiles_69.png", t),
        "camara": cam_off,
        "camara_activa": cam_on,
        "panel": _cargar_imagen(l / "tiles_57.png", t),
        "rejilla": _cargar_imagen(c / "pabellon_tiles_09.png", t),
        "barril": _cargar_imagen(c / "pabellon_tiles_56.png", t),
        "caja": _cargar_imagen(c / "pabellon_tiles_54.png", t),
        "caja_metal": _cargar_imagen(c / "pabellon_tiles_55.png", t),
        "carrito": _cargar_imagen(c / "pabellon_tiles_58.png", t),
        "tubo_codo": _cargar_imagen(c / "pabellon_tiles_51.png", t),
    }
    lavanderia = {
        "suelo": _cargar_imagen(l / "tiles_01.png", t),
        "suelo_grieta": _cargar_imagen(l / "tiles_02.png", t),
        "suelo_alt": _cargar_imagen(l / "tiles_29.png", t),
        "muro": _cargar_imagen(l / "tiles_11.png", t),
        "muro_alt": _cargar_imagen(l / "tiles_12.png", t),
        "ventana": _cargar_imagen(l / "tiles_08.png", t),
        "lampara": _cargar_imagen(l / "tiles_07.png", t),
        "alambre": _cargar_imagen(l / "tiles_62.png", t),
        "tubo_muro": _cargar_imagen(l / "tiles_63.png", t),
        "objeto": _cargar_imagen(l / "tiles_55.png", t),
        "objeto_alt": _cargar_imagen(l / "tiles_56.png", t),
        "llave": _cargar_imagen(l / "tiles_48.png", (34, 34)),
        "salida": _cargar_imagen(l / "tiles_05.png", t),
        "salida_bloqueada": _cargar_imagen(l / "tiles_47.png", t),
        "camara": _cargar_imagen(l / "tiles_49.png", (30, 30)),
        "camara_activa": _cargar_imagen(l / "tiles_52.png", (30, 30)),
        "panel": _cargar_imagen(l / "tiles_57.png", t),
        "rejilla": _cargar_imagen(l / "tiles_06.png", t),
        "barril": _cargar_imagen(l / "tiles_53.png", t),
        "caja": caja_madera,
        "marca_suelo": _cargar_imagen(l / "tiles_59.png", t),
        "lona": _cargar_imagen(l / "tiles_60.png", t),
        "papeles": _cargar_imagen(l / "tiles_61.png", t),
    }
    patio = {
        "suelo": _cargar_imagen(p / "tiles_01.png", t),
        "suelo_grieta": _cargar_imagen(p / "tiles_02.png", t),
        "suelo_alt": _cargar_imagen(p / "tiles_10.png", t),
        "muro": _cargar_imagen(p / "tiles_03.png", t),
        "muro_alt": _cargar_imagen(p / "tiles_16.png", t),
        "ventana": _cargar_imagen(p / "tiles_08.png", t),
        "lampara": _cargar_imagen(p / "tiles_07.png", t),
        "tubo_muro": _cargar_imagen(p / "tiles_61.png", t),
        "llave": llave_comun,
        "salida": _cargar_imagen(p / "tiles_05.png", t),
        "salida_bloqueada": _cargar_imagen(p / "tiles_55.png", t),
        "camara": cam_off,
        "camara_activa": cam_on,
        "panel": _cargar_imagen(p / "tiles_59.png", t),
        "rejilla": _cargar_imagen(p / "tiles_06.png", t),
        "barril": _cargar_imagen(p / "tiles_56.png", t),
        "caja": caja_madera,
    }
    arena = {
        "suelo": _cargar_imagen(a / "tiles_01.png", t),
        "suelo_grieta": _cargar_imagen(a / "tiles_02.png", t),
        "suelo_alt": _cargar_imagen(a / "tiles_10.png", t),
        "muro": _cargar_imagen(a / "tiles_03.png", t),
        "muro_alt": _cargar_imagen(a / "tiles_16.png", t),
        "ventana": _cargar_imagen(a / "tiles_08.png", t),
        "lampara": _cargar_imagen(a / "tiles_07.png", t),
        "objeto": _cargar_imagen(a / "tiles_60.png", t),
        "cajas": _cargar_imagen(a / "tiles_62.png", t),
        "tubo_rojo": _cargar_imagen(a / "tiles_63.png", t),
        "llave": llave_comun,
        "salida": _cargar_imagen(a / "tiles_05.png", t),
        "salida_bloqueada": _cargar_imagen(a / "tiles_57.png", t),
        "camara": cam_off,
        "camara_activa": cam_on,
        "panel": _cargar_imagen(a / "tiles_61.png", t),
        "rejilla": _cargar_imagen(a / "tiles_06.png", t),
    }
    return {
        "celda": celda,
        "lavanderia": lavanderia,
        "patio": patio,
        "arena": arena,
    }


def _direccion_estable(mx, my, actual="abajo"):
    """Determina la dirección de sprite con histéresis para evitar parpadeos diagonales."""
    ax, ay = abs(mx), abs(my)
    if ax < 1e-4 and ay < 1e-4:
        return actual
    if actual in ("izquierda", "derecha"):
        if ay > ax * 1.25:
            return "abajo" if my > 0 else "arriba"
        return "derecha" if mx >= 0 else "izquierda"
    if ax > ay * 1.10:
        return "derecha" if mx > 0 else "izquierda"
    return "abajo" if my >= 0 else "arriba"


def _poligono_cono(origen, mirada, alcance, semiangulo_deg, muros, rayos=11):
    """Calcula el polígono del cono de linterna recortado por los muros del mapa."""
    ang_base = math.atan2(mirada[1], mirada[0])
    semi = math.radians(semiangulo_deg)
    puntos = [origen]
    for i in range(rayos + 1):
        ang = ang_base - semi + (2 * semi * i / rayos)
        fin = (origen[0] + math.cos(ang) * alcance, origen[1] + math.sin(ang) * alcance)
        mejor = fin
        mejor_d2 = alcance * alcance
        for muro in muros:
            corte = muro.clipline(origen, fin)
            if corte:
                p = corte[0]
                d2 = (p[0] - origen[0]) ** 2 + (p[1] - origen[1]) ** 2
                if d2 < mejor_d2:
                    mejor_d2 = d2
                    mejor = p
        puntos.append(mejor)
    return puntos


class Vista:
    def __init__(self, pantalla):
        self.__pantalla = pantalla
        self.__fuente_grande = pygame.font.SysFont("dejavusans", 38, bold=True)
        self.__fuente_titulo = pygame.font.SysFont("dejavusans", 26, bold=True)
        self.__fuente_mediana = pygame.font.SysFont("dejavusans", 20, bold=True)
        self.__fuente = pygame.font.SysFont("dejavusans", 15)
        self.__fuente_pequena = pygame.font.SysFont("dejavusans", 13)

        c = RUTA_IMG / "mapas" / "celda_v2"
        self.__recursos = {
            "preso": _cargar_personaje("preso", "preso", (38, 38)),
            "guardia": _cargar_personaje("guardias", "guardia", (38, 38)),
            "alcaide": _cargar_personaje("alcaide", "alcaide", (46, 46)),
            "mapas": _cargar_tilesets(),
            "sombra_abajo": _crear_sombra(TAMANO_CELDA, 12, False, 100),
            "sombra_lado": _crear_sombra(8, TAMANO_CELDA, True, 65),
            "halo_lampara": _cargar_halo(c / "halo_ambar.png", 104, 42),
            "halo_llave": _cargar_halo(c / "halo_ambar.png", 90, 75),
            "halo_salida": _cargar_halo(c / "halo_verde.png", 140, 175),
            "halo_salida_tenue": _cargar_halo(c / "halo_verde.png", 110, 85),
        }
        self.__direcciones = {}
        self.__fases_paso = {}
        self.__ultimo_tick = pygame.time.get_ticks() / 1000.0

    def opcion_menu_en_punto(self, pos):
        for indice, (_, rect) in enumerate(BOTONES_MENU):
            if rect.collidepoint(pos):
                return indice
        return None

    def dibujar(self, juego):
        ahora = pygame.time.get_ticks() / 1000.0
        dt_visual = min(0.05, max(0.0, ahora - self.__ultimo_tick))
        self.__ultimo_tick = ahora

        nivel = juego.get_nivel()
        config = juego.get_config_nivel() or {}
        tema = config.get("tema", "celda")
        tiles = self.__recursos["mapas"][tema]
        decoraciones = config.get("decoraciones", [])
        intro_progreso = juego.get_intro_progreso()

        self.__pantalla.fill((13, 21, 31))
        self.__dibujar_encabezado(juego, nivel, config)
        self.__dibujar_mapa(nivel, tiles, decoraciones)
        self.__dibujar_camaras(nivel, tiles)
        self.__dibujar_conos_vision(juego, nivel)
        self.__dibujar_objetos(nivel, tiles, ahora, intro_progreso, juego.es_boss_run())
        self.__dibujar_personajes(juego, nivel, ahora, dt_visual, intro_progreso)

        estado_boss = juego.get_estado_boss()
        if intro_progreso is not None:
            self.__dibujar_banner_intro(intro_progreso, juego.es_boss_run())
        elif estado_boss and estado_boss["mensaje"]:
            self.__dibujar_aviso_boss(estado_boss["mensaje"])

        self.__dibujar_pie(juego.es_boss_run())

    def dibujar_menu(self, juego):
        tiempo = pygame.time.get_ticks() / 1000.0
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((7, 12, 20, 208))
        self.__pantalla.blit(capa, (0, 0))

        tarjeta = pygame.Rect(160, 126, 580, 396)
        pygame.draw.rect(self.__pantalla, (18, 29, 42), tarjeta, border_radius=16)
        pygame.draw.rect(self.__pantalla, (242, 206, 114), tarjeta, 2, border_radius=16)

        titulo = self.__fuente_grande.render("FUGA DE LA PRISIÓN", True, (242, 246, 252))
        self.__pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 198)))

        subtitulo = self.__fuente.render(
            "Sigilo, estrategia y persecución final contra el Alcaide",
            True,
            (156, 182, 206),
        )
        self.__pantalla.blit(subtitulo, subtitulo.get_rect(center=(ANCHO // 2, 242)))

        paso = SECUENCIA_PASO[int(tiempo * 5.5) % len(SECUENCIA_PASO)]
        preso_img = pygame.transform.scale(self.__recursos["preso"]["derecha"][paso], (64, 64))
        alcaide_img = pygame.transform.scale(self.__recursos["alcaide"]["izquierda"][paso], (72, 72))
        self.__pantalla.blit(preso_img, preso_img.get_rect(center=(234, 390)))
        self.__pantalla.blit(alcaide_img, alcaide_img.get_rect(center=(666, 388)))

        seleccion = juego.get_opcion_menu()
        for indice, (etiqueta, rect) in enumerate(BOTONES_MENU):
            activo = indice == seleccion
            fondo = (39, 64, 88) if activo else (25, 39, 54)
            borde = (242, 206, 114) if activo else (84, 110, 136)
            color_txt = (255, 240, 185) if activo else (216, 228, 240)
            pygame.draw.rect(self.__pantalla, fondo, rect, border_radius=10)
            pygame.draw.rect(self.__pantalla, borde, rect, 2, border_radius=10)
            prefijo = "▶  " if activo else ""
            txt = self.__fuente_mediana.render(f"{prefijo}{etiqueta}", True, color_txt)
            self.__pantalla.blit(txt, txt.get_rect(center=rect.center))

    def dibujar_pausa(self):
        self.__dibujar_overlay(
            "PARTIDA EN PAUSA",
            "El nivel y los temporizadores están detenidos.",
            "P / ESC: Continuar   ·   M: Menú",
            (182, 212, 242),
        )

    def dibujar_resultado(self, victoria, total_niveles=7):
        if victoria:
            self.__dibujar_overlay(
                "¡FUGA COMPLETADA!",
                f"Superaste los {total_niveles} sectores y escapaste del Alcaide.",
                "R: Nueva partida   ·   M: Menú",
                (111, 226, 188),
            )
        else:
            self.__dibujar_overlay(
                "TE HAN ATRAPADO",
                "Te interceptaron antes de lograr la fuga.",
                "R: Reintentar nivel   ·   M: Menú",
                (250, 142, 147),
            )

    def __texto(self, texto, x, y, color=(225, 234, 242), fuente=None):
        superficie = (fuente or self.__fuente).render(texto, True, color)
        self.__pantalla.blit(superficie, (x, y))

    def __a_pantalla(self, rect):
        return rect.move(ORIGEN[0], ORIGEN[1])

    def __dibujar_encabezado(self, juego, nivel, config):
        self.__texto("FUGA DE LA PRISIÓN", ORIGEN[0], 14, fuente=self.__fuente_titulo)
        nombre = config.get("nombre", f"Nivel {nivel.get_numero()}")
        self.__texto(
            f"NIVEL {nivel.get_numero()} / {juego.get_total_niveles()}  ·  {nombre.upper()}",
            ORIGEN[0],
            48,
            (145, 168, 190),
            self.__fuente_pequena,
        )

        prisionero = nivel.get_prisionero()
        estado_boss = juego.get_estado_boss()
        if estado_boss is not None:
            if prisionero.tiene_llave():
                objetivo = "¡TIENES LA LLAVE! CORRE A LA SALIDA FINAL"
                color_obj = (111, 226, 188)
            else:
                objetivo = "¡CORRE! ESQUIVA OBSTÁCULOS Y TOMA LA LLAVE"
                color_obj = (255, 130, 120)
        elif prisionero.tiene_llave():
            objetivo = "LLAVE OBTENIDA  ·  VE A LA SALIDA"
            color_obj = (111, 226, 188)
        else:
            objetivo = "BUSCA LA LLAVE Y EVITA LAS LINTERNAS"
            color_obj = (242, 206, 114)
        self.__texto(objetivo, ORIGEN[0], 68, color_obj, self.__fuente_pequena)

        puntos = juego.get_puntaje().get_valor()
        self.__texto(f"PUNTOS  {puntos:04d}", 680, 16, (111, 226, 188), self.__fuente_mediana)

        if estado_boss is not None:
            self.__dibujar_hud_boss(estado_boss)
            return

        en_alerta = any(g.esta_alerta() for g in nivel.get_guardias())
        if en_alerta:
            self.__texto("¡GUARDIA EN ALERTA!", 680, 48, (250, 118, 126), self.__fuente_pequena)
        else:
            panel = nivel.get_panel()
            if panel is not None:
                if panel.esta_activo():
                    estado_panel = "CÁMARAS APAGADAS"
                    color_panel = (111, 226, 188)
                else:
                    estado_panel = "CÁMARAS ACTIVAS"
                    color_panel = (241, 184, 79)
                self.__texto(estado_panel, 680, 48, color_panel, self.__fuente_pequena)

    def __dibujar_hud_boss(self, estado_boss):
        etiquetas = {
            "persiguiendo": ("ALCAIDE · FASE 1", (255, 126, 120)),
            "furia": ("ALCAIDE · FASE 2 FURIA", (255, 92, 98)),
            "cargando": ("¡PREPARA EMBESTIDA!", (255, 214, 92)),
            "embistiendo": ("¡EMBESTIDA!", (255, 70, 78)),
            "aturdido": ("ALCAIDE ATURDIDO", (110, 205, 255)),
            "alarma": ("¡ALARMA ACTIVA!", (255, 145, 90)),
        }
        texto, color = etiquetas.get(estado_boss["estado"], ("ALCAIDE", (255, 110, 110)))
        self.__texto(texto, 680, 46, color, self.__fuente_pequena)

        # Barra de proximidad del Alcaide
        barra = pygame.Rect(680, 68, 170, 10)
        pygame.draw.rect(self.__pantalla, (30, 42, 56), barra, border_radius=5)
        relleno_w = max(6, round(barra.width * estado_boss["proximidad"]))
        pygame.draw.rect(self.__pantalla, color, (barra.x, barra.y, relleno_w, barra.height), border_radius=5)
        pygame.draw.rect(self.__pantalla, (120, 140, 160), barra, 1, border_radius=5)

    def __dibujar_mapa(self, nivel, tiles, decoraciones):
        mapa = nivel.get_mapa()
        ancho, alto = mapa.get_dimensiones()
        cols = ancho // TAMANO_CELDA
        filas = alto // TAMANO_CELDA
        muros_set = {(m.x // TAMANO_CELDA, m.y // TAMANO_CELDA) for m in mapa.get_muros()}
        decor_mapa = {(c, f): tipo for c, f, tipo in decoraciones}

        for fila in range(filas):
            for col in range(cols):
                destino = (ORIGEN[0] + col * TAMANO_CELDA, ORIGEN[1] + fila * TAMANO_CELDA)
                tipo_dec = decor_mapa.get((col, fila))
                es_prop_solido = (col, fila) in muros_set and tipo_dec and tipo_dec not in DECORACIONES_MURO
                if (col, fila) in muros_set and not es_prop_solido:
                    continue

                if (col * 7 + fila * 13) % 11 == 0:
                    tile_suelo = tiles["suelo_grieta"]
                elif (col * 5 + fila * 3) % 9 == 0:
                    tile_suelo = tiles["suelo_alt"]
                else:
                    tile_suelo = tiles["suelo"]
                self.__pantalla.blit(tile_suelo, destino)

                if tipo_dec in DECORACIONES_SUELO and tipo_dec in tiles:
                    self.__pantalla.blit(tiles[tipo_dec], destino)

                if (col, fila - 1) in muros_set:
                    self.__pantalla.blit(self.__recursos["sombra_abajo"], destino)
                if (col - 1, fila) in muros_set:
                    self.__pantalla.blit(self.__recursos["sombra_lado"], destino)

        lamparas_pos = []
        for col, fila in muros_set:
            destino = (ORIGEN[0] + col * TAMANO_CELDA, ORIGEN[1] + fila * TAMANO_CELDA)
            tipo_dec = decor_mapa.get((col, fila))

            if tipo_dec and tipo_dec not in DECORACIONES_MURO and tipo_dec in tiles:
                self.__pantalla.blit(tiles[tipo_dec], destino)
                continue

            tile_muro = tiles["muro_alt"] if (col, fila - 1) in muros_set else tiles["muro"]
            self.__pantalla.blit(tile_muro, destino)
            if tipo_dec in DECORACIONES_MURO and tipo_dec in tiles:
                self.__pantalla.blit(tiles[tipo_dec], destino)

            if fila in (0, filas - 1) and col in (4, 10, 15) and tipo_dec is None:
                self.__pantalla.blit(tiles["lampara"], destino)
                lamparas_pos.append((destino[0] + TAMANO_CELDA // 2, destino[1] + TAMANO_CELDA // 2))

        area = pygame.Rect(ORIGEN[0], ORIGEN[1], ancho, alto)
        self.__pantalla.set_clip(area)
        halo_lampara = self.__recursos["halo_lampara"]
        for lx, ly in lamparas_pos:
            self.__pantalla.blit(halo_lampara, halo_lampara.get_rect(center=(lx, ly)), special_flags=pygame.BLEND_RGB_ADD)
        self.__pantalla.set_clip(None)

    def __dibujar_camaras(self, nivel, tiles):
        for camara in nivel.get_camaras():
            zona = self.__a_pantalla(camara.get_zona())
            activa = camara.detectar(camara.get_zona())

            capa = pygame.Surface((zona.width, zona.height), pygame.SRCALPHA)
            if activa:
                capa.fill((241, 184, 79, 58))
                borde = (241, 184, 79)
                sprite_cam = tiles["camara_activa"]
            else:
                capa.fill((120, 136, 154, 22))
                borde = (110, 126, 144)
                sprite_cam = tiles["camara"]

            self.__pantalla.blit(capa, zona.topleft)
            pygame.draw.rect(self.__pantalla, borde, zona, 1)
            self.__pantalla.blit(sprite_cam, sprite_cam.get_rect(midtop=(zona.centerx, zona.top + 2)))

    def __dibujar_conos_vision(self, juego, nivel):
        ancho, alto = nivel.get_mapa().get_dimensiones()
        capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        muros = nivel.get_mapa().get_muros()
        estado_boss = juego.get_estado_boss()

        for guardia in nivel.get_guardias():
            origen = guardia.get_rect().center
            mirada = guardia.get_mirada()
            es_alcaide = juego.es_boss_run() and isinstance(guardia, GuardiaPatrulla)
            alcance = 225 if es_alcaide else ALCANCE_VISION
            poligono = _poligono_cono(origen, mirada, alcance, SEMIANGULO_VISION_DEG, muros)

            if es_alcaide and estado_boss:
                st = estado_boss["estado"]
                if st == "aturdido":
                    color = (100, 195, 255, 55)
                elif st == "cargando":
                    color = (255, 214, 92, 72)
                else:
                    color = (255, 72, 82, 68)
            elif guardia.esta_alerta():
                color = (255, 84, 92, 62)
            else:
                color = (255, 215, 115, 38)

            if len(poligono) >= 3:
                pygame.draw.polygon(capa, color, poligono)

        self.__pantalla.blit(capa, ORIGEN)

    def __dibujar_objetos(self, nivel, tiles, tiempo, intro_progreso=None, es_boss_run=False):
        area = pygame.Rect(ORIGEN[0], ORIGEN[1], *nivel.get_mapa().get_dimensiones())
        self.__pantalla.set_clip(area)

        puerta_rect = self.__a_pantalla(nivel.get_puerta().get_rect())
        tiene_llave = nivel.get_prisionero().tiene_llave()
        halo_salida = self.__recursos["halo_salida"] if tiene_llave else self.__recursos["halo_salida_tenue"]
        self.__pantalla.blit(
            halo_salida, halo_salida.get_rect(center=puerta_rect.center), special_flags=pygame.BLEND_RGB_ADD
        )
        sprite_puerta = tiles["salida"] if tiene_llave else tiles["salida_bloqueada"]
        self.__pantalla.blit(sprite_puerta, puerta_rect.topleft)

        llave = nivel.get_llave()
        if not llave.esta_recogida():
            llave_rect = self.__a_pantalla(llave.get_rect())
            flote = round(math.sin(tiempo * 4.5) * 3)
            self.__pantalla.blit(
                self.__recursos["halo_llave"],
                self.__recursos["halo_llave"].get_rect(center=llave_rect.center),
                special_flags=pygame.BLEND_RGB_ADD,
            )
            sprite_llave = tiles["llave"]
            self.__pantalla.blit(
                sprite_llave, sprite_llave.get_rect(center=(llave_rect.centerx, llave_rect.centery + flote))
            )
            # Resaltar la llave durante la escena 3 de la cinemática
            if intro_progreso is not None and not es_boss_run and 0.40 <= intro_progreso < 0.60:
                radio = 24 + round(math.sin(tiempo * 7) * 4)
                pygame.draw.circle(self.__pantalla, (255, 218, 110), llave_rect.center, radio, 2)

        panel = nivel.get_panel()
        if panel is not None:
            panel_rect = self.__a_pantalla(panel.get_rect())
            self.__pantalla.blit(tiles["panel"], panel_rect.topleft)
            color_borde = (111, 226, 188) if panel.esta_activo() else (110, 195, 250)
            pygame.draw.rect(self.__pantalla, color_borde, panel_rect, 2, border_radius=4)
            # Resaltar el panel durante la escena 4 de la cinemática
            if intro_progreso is not None and not es_boss_run and 0.60 <= intro_progreso < 0.80:
                radio = 26 + round(math.sin(tiempo * 7) * 4)
                pygame.draw.circle(self.__pantalla, (110, 205, 255), panel_rect.center, radio, 2)

        self.__pantalla.set_clip(None)

    def __dibujar_personajes(self, juego, nivel, tiempo, dt_visual, intro_progreso=None):
        es_boss = juego.es_boss_run()
        estado_boss = juego.get_estado_boss()

        for personaje in nivel.get_personajes():
            rect = self.__a_pantalla(personaje.get_rect())
            clave = id(personaje)
            es_preso = isinstance(personaje, Prisionero)
            es_alcaide = es_boss and isinstance(personaje, GuardiaPatrulla)

            if es_preso and intro_progreso is not None and not es_boss:
                progreso = max(0.0, min(1.0, intro_progreso))
                direccion = "derecha"
                frame = 0
                if progreso < 0.16:
                    avance = progreso / 0.16
                    avance = avance * avance * (3 - 2 * avance)
                    rect.x -= round(TAMANO_CELDA * (1.0 - avance))
                    frame = SECUENCIA_PASO[int(tiempo * 7.5) % len(SECUENCIA_PASO)]
                elif progreso < 0.28:
                    direccion = "arriba"
                elif progreso < 0.38:
                    direccion = "derecha"
                elif progreso < 0.56:
                    direccion = "arriba"
                elif progreso < 0.78:
                    direccion = "derecha"
                else:
                    direccion = "arriba"
                self.__direcciones[clave] = direccion
            else:
                defecto = "derecha" if es_boss else "abajo"
                mx, my = personaje.get_mirada()
                direccion = _direccion_estable(mx, my, self.__direcciones.get(clave, defecto))
                self.__direcciones[clave] = direccion

                if personaje.esta_moviendose():
                    ritmo = 9.0 if (es_preso or es_alcaide) else 7.2
                    fase = self.__fases_paso.get(clave, 0.0) + dt_visual * ritmo
                    self.__fases_paso[clave] = fase
                    frame = SECUENCIA_PASO[int(fase) % len(SECUENCIA_PASO)]
                else:
                    self.__fases_paso[clave] = 0.0
                    frame = 0

            if es_preso:
                grupo = "preso"
            elif es_alcaide:
                grupo = "alcaide"
            else:
                grupo = "guardia"
            sprite = self.__recursos[grupo][direccion][frame]

            if es_alcaide:
                st = estado_boss["estado"] if estado_boss else "persiguiendo"
                if st == "aturdido":
                    color_aro = (110, 205, 255)
                elif st == "cargando":
                    color_aro = (255, 214, 92)
                elif st == "embistiendo":
                    color_aro = (255, 68, 76)
                else:
                    color_aro = (255, 102, 108)
                grosor = 3 if st in ("cargando", "embistiendo") else 2
                pygame.draw.ellipse(
                    self.__pantalla,
                    color_aro,
                    (rect.centerx - 21, rect.bottom - 6, 42, 12),
                    grosor,
                )
            elif isinstance(personaje, Guardia) and personaje.esta_alerta():
                pygame.draw.ellipse(
                    self.__pantalla,
                    (250, 100, 112),
                    (rect.centerx - 16, rect.bottom - 6, 32, 10),
                    2,
                )

            self.__pantalla.blit(sprite, sprite.get_rect(center=rect.center))

            if es_alcaide:
                st = estado_boss["estado"] if estado_boss else "persiguiendo"
                if st == "aturdido":
                    etq, col_etq = "ATURDIDO", (110, 205, 255)
                elif st == "cargando":
                    etq, col_etq = "¡EMBESTIDA!", (255, 214, 92)
                else:
                    etq, col_etq = "ALCAIDE", (255, 112, 118)
                surf_etq = self.__fuente_pequena.render(etq, True, col_etq)
                rect_etq = surf_etq.get_rect(midbottom=(rect.centerx, rect.top - 12))
                pygame.draw.rect(self.__pantalla, (12, 18, 28), rect_etq.inflate(8, 2), border_radius=4)
                self.__pantalla.blit(surf_etq, rect_etq)
            elif isinstance(personaje, Guardia) and personaje.esta_alerta():
                self.__texto("!", rect.centerx - 4, rect.top - 24, (250, 100, 112), self.__fuente_mediana)

    def __dibujar_banner_intro(self, progreso, es_boss_run=False):
        caja = pygame.Rect(120, 128, 660, 88)
        fondo = pygame.Surface((caja.width, caja.height), pygame.SRCALPHA)
        fondo.fill((10, 17, 26, 238))
        self.__pantalla.blit(fondo, caja.topleft)

        if es_boss_run:
            retrato_grupo = "alcaide"
            borde = (255, 100, 108)
            linea1 = "ALCAIDE: «¡Alto ahí, prisionero! ¡Nadie escapa de mi sector!»"
            linea2 = "Esquiva los obstáculos, toma la llave y usa el panel azul para aturdirlo."
        elif progreso < 0.20:
            retrato_grupo = "preso"
            borde = (242, 206, 114)
            linea1 = "Pabellón Central — 02:14 AM."
            linea2 = "Tres años encerrado por un crimen que nunca cometiste."
        elif progreso < 0.40:
            retrato_grupo = "preso"
            borde = (242, 206, 114)
            linea1 = "Esta noche el guardia dejó sin seguro el cerrojo de tu celda."
            linea2 = "Es tu única oportunidad para escapar antes del amanecer."
        elif progreso < 0.60:
            retrato_grupo = "preso"
            borde = (242, 206, 114)
            linea1 = "Cada sector esconde una llave que desbloquea la puerta de salida."
            linea2 = "Evita las linternas de los guardias y las cámaras de vigilancia."
        elif progreso < 0.80:
            retrato_grupo = "preso"
            borde = (110, 195, 250)
            linea1 = "Los paneles azules apagan las cámaras durante unos segundos,"
            linea2 = "pero la alarma atraerá a los guardias hacia esa posición."
        else:
            retrato_grupo = "alcaide"
            borde = (255, 105, 112)
            linea1 = "Tras cruzar los seis sectores te aguarda el Alcaide en su arena."
            linea2 = "Cuando te descubra en el tramo final... no mires atrás y corre."

        pygame.draw.rect(self.__pantalla, borde, caja, 2, border_radius=10)

        # Retrato del personaje a la izquierda
        marco = pygame.Rect(caja.x + 14, caja.y + 14, 60, 60)
        pygame.draw.rect(self.__pantalla, (20, 31, 45), marco, border_radius=8)
        pygame.draw.rect(self.__pantalla, borde, marco, 1, border_radius=8)
        retrato = pygame.transform.scale(self.__recursos[retrato_grupo]["abajo"][0], (48, 48))
        self.__pantalla.blit(retrato, retrato.get_rect(center=marco.center))

        self.__texto(linea1, caja.x + 88, caja.y + 20, (242, 246, 252), self.__fuente)
        self.__texto(linea2, caja.x + 88, caja.y + 48, (186, 204, 222), self.__fuente)

    def __dibujar_aviso_boss(self, mensaje):
        surf = self.__fuente_mediana.render(mensaje, True, (255, 232, 160))
        rect = surf.get_rect(center=(ANCHO // 2, 126))
        caja = rect.inflate(28, 14)
        fondo = pygame.Surface((caja.width, caja.height), pygame.SRCALPHA)
        fondo.fill((22, 12, 18, 220))
        self.__pantalla.blit(fondo, caja.topleft)
        pygame.draw.rect(self.__pantalla, (255, 100, 108), caja, 2, border_radius=8)
        self.__pantalla.blit(surf, rect)

    def __dibujar_pie(self, es_boss_run=False):
        if es_boss_run:
            texto = "WASD / Flechas: Correr  ·  Panel azul aturde al Alcaide  ·  P / ESC: Pausa  ·  F11: Pantalla completa"
        else:
            texto = "WASD / Flechas: Mover  ·  P / ESC: Pausa  ·  F11: Pantalla completa  ·  Panel azul apaga cámaras (alerta guardias)"
        self.__texto(texto, ORIGEN[0], 628, (145, 168, 190), self.__fuente_pequena)

    def __dibujar_overlay(self, titulo, detalle, accion, color):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((6, 11, 18, 194))
        self.__pantalla.blit(capa, (0, 0))

        caja = pygame.Rect(185, 225, 530, 190)
        pygame.draw.rect(self.__pantalla, (24, 37, 50), caja, border_radius=14)
        pygame.draw.rect(self.__pantalla, color, caja, 2, border_radius=14)

        self.__texto(titulo, caja.x + 32, caja.y + 30, color, self.__fuente_mediana)
        self.__texto(detalle, caja.x + 32, caja.y + 84, (225, 234, 242), self.__fuente)
        self.__texto(accion, caja.x + 32, caja.y + 132, (242, 206, 114), self.__fuente)
