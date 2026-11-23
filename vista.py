"""Capa de presentación en Pygame usando los tiles y sprites de img/."""
import math
from pathlib import Path

import pygame

from mapa import TAMANO_CELDA
from personajes import Prisionero


ANCHO = 900
ALTO = 660
ORIGEN = (50, 96)
RUTA_IMG = Path(__file__).resolve().parent / "img"

DIRECCIONES = ("abajo", "izquierda", "derecha", "arriba")
SECUENCIA_PASO = (0, 1, 0, 2)
NOMBRES_NIVEL = ("Pabellón de celdas", "Lavandería", "Patio de vigilancia")


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

    llave_comun = _cargar_imagen(c / "pabellon_tiles_07.png", (34, 34))
    cam_off = _cargar_imagen(c / "pabellon_tiles_13.png", (30, 30))
    cam_on = _cargar_imagen(c / "pabellon_tiles_70.png", (30, 30))

    celda = {
        "suelo": _cargar_imagen(c / "pabellon_tiles_01.png", t),
        "suelo_grieta": _cargar_imagen(c / "pabellon_tiles_02.png", t),
        "muro": _cargar_imagen(c / "pabellon_tiles_03.png", t),
        "muro_alt": _cargar_imagen(c / "pabellon_tiles_19.png", t),
        "lampara": _cargar_imagen(c / "pabellon_tiles_10.png", t),
        "llave": llave_comun,
        "salida": _cargar_imagen(c / "pabellon_tiles_08.png", t),
        "salida_bloqueada": _cargar_imagen(c / "pabellon_tiles_69.png", t),
        "camara": cam_off,
        "camara_activa": cam_on,
        "panel": _cargar_imagen(l / "tiles_57.png", t),
    }
    lavanderia = {
        "suelo": _cargar_imagen(l / "tiles_01.png", t),
        "suelo_grieta": _cargar_imagen(l / "tiles_02.png", t),
        "muro": _cargar_imagen(l / "tiles_11.png", t),
        "muro_alt": _cargar_imagen(l / "tiles_12.png", t),
        "lampara": _cargar_imagen(l / "tiles_07.png", t),
        "llave": _cargar_imagen(l / "tiles_48.png", (34, 34)),
        "salida": _cargar_imagen(l / "tiles_05.png", t),
        "salida_bloqueada": _cargar_imagen(l / "tiles_47.png", t),
        "camara": _cargar_imagen(l / "tiles_49.png", (30, 30)),
        "camara_activa": _cargar_imagen(l / "tiles_52.png", (30, 30)),
        "panel": _cargar_imagen(l / "tiles_57.png", t),
    }
    patio = {
        "suelo": _cargar_imagen(p / "tiles_01.png", t),
        "suelo_grieta": _cargar_imagen(p / "tiles_02.png", t),
        "muro": _cargar_imagen(p / "tiles_03.png", t),
        "muro_alt": _cargar_imagen(p / "tiles_16.png", t),
        "lampara": _cargar_imagen(p / "tiles_07.png", t),
        "llave": llave_comun,
        "salida": _cargar_imagen(p / "tiles_05.png", t),
        "salida_bloqueada": _cargar_imagen(p / "tiles_55.png", t),
        "camara": cam_off,
        "camara_activa": cam_on,
        "panel": _cargar_imagen(p / "tiles_59.png", t),
    }
    return [celda, lavanderia, patio]


def _direccion_desde_vector(dx, dy, actual="abajo"):
    if dx == 0 and dy == 0:
        return actual
    if abs(dx) >= abs(dy):
        return "derecha" if dx > 0 else "izquierda"
    return "abajo" if dy > 0 else "arriba"


class Vista:
    def __init__(self, pantalla):
        self.__pantalla = pantalla
        self.__fuente_titulo = pygame.font.SysFont("dejavusans", 26, bold=True)
        self.__fuente_mediana = pygame.font.SysFont("dejavusans", 20, bold=True)
        self.__fuente = pygame.font.SysFont("dejavusans", 15)
        self.__fuente_pequena = pygame.font.SysFont("dejavusans", 13)

        c = RUTA_IMG / "mapas" / "celda_v2"
        self.__recursos = {
            "preso": _cargar_personaje("preso", "preso", (38, 38)),
            "guardia": _cargar_personaje("guardias", "guardia", (38, 38)),
            "mapas": _cargar_tilesets(),
            "sombra_abajo": _crear_sombra(TAMANO_CELDA, 12, False, 100),
            "sombra_lado": _crear_sombra(8, TAMANO_CELDA, True, 65),
            "halo_llave": _cargar_halo(c / "halo_ambar.png", 90, 75),
            "halo_salida": _cargar_halo(c / "halo_verde.png", 140, 175),
            "halo_salida_tenue": _cargar_halo(c / "halo_verde.png", 110, 85),
        }
        self.__posiciones_previas = {}
        self.__direcciones = {}

    def dibujar(self, juego):
        nivel = juego.get_nivel()
        indice = nivel.get_numero() - 1
        tiles = self.__recursos["mapas"][indice]
        tiempo = pygame.time.get_ticks() / 1000.0

        self.__pantalla.fill((13, 21, 31))
        self.__dibujar_encabezado(juego, nivel, indice)
        self.__dibujar_mapa(nivel, tiles)
        self.__dibujar_camaras(nivel, tiles)
        self.__dibujar_objetos(nivel, tiles, tiempo)
        self.__dibujar_personajes(nivel, tiempo)
        self.__dibujar_pie(nivel)

    def dibujar_pausa(self):
        self.__dibujar_overlay(
            "PARTIDA EN PAUSA",
            "El nivel y los temporizadores están detenidos.",
            "Presiona P o ESC para continuar",
            (182, 212, 242),
        )

    def dibujar_resultado(self, victoria):
        if victoria:
            self.__dibujar_overlay(
                "¡FUGA COMPLETADA!",
                "Superaste los 3 niveles de la prisión.",
                "Presiona R para iniciar una nueva partida",
                (111, 226, 188),
            )
        else:
            self.__dibujar_overlay(
                "TE HAN ATRAPADO",
                "Un guardia te interceptó en el recorrido.",
                "Presiona R para reintentar este nivel",
                (250, 142, 147),
            )

    def __texto(self, texto, x, y, color=(225, 234, 242), fuente=None):
        superficie = (fuente or self.__fuente).render(texto, True, color)
        self.__pantalla.blit(superficie, (x, y))

    def __a_pantalla(self, rect):
        return rect.move(ORIGEN[0], ORIGEN[1])

    def __dibujar_encabezado(self, juego, nivel, indice):
        self.__texto("FUGA DE LA PRISIÓN", ORIGEN[0], 14, fuente=self.__fuente_titulo)
        nombre = NOMBRES_NIVEL[indice] if indice < len(NOMBRES_NIVEL) else f"Nivel {nivel.get_numero()}"
        self.__texto(
            f"NIVEL {nivel.get_numero()} / {len(NOMBRES_NIVEL)}  ·  {nombre.upper()}",
            ORIGEN[0],
            48,
            (145, 168, 190),
            self.__fuente_pequena,
        )

        prisionero = nivel.get_prisionero()
        if prisionero.tiene_llave():
            objetivo = "LLAVE OBTENIDA  ·  VE A LA SALIDA"
            color_obj = (111, 226, 188)
        else:
            objetivo = "BUSCA LA LLAVE Y EVITA A LOS GUARDIAS"
            color_obj = (242, 206, 114)
        self.__texto(objetivo, ORIGEN[0], 68, color_obj, self.__fuente_pequena)

        puntos = juego.get_puntaje().get_valor()
        self.__texto(f"PUNTOS  {puntos:04d}", 685, 20, (111, 226, 188), self.__fuente_mediana)

        en_alerta = any(g.esta_alerta() for g in nivel.get_guardias())
        if en_alerta:
            self.__texto("¡GUARDIA EN ALERTA!", 685, 52, (250, 118, 126), self.__fuente_pequena)
        else:
            panel = nivel.get_panel()
            if panel is not None:
                if panel.esta_activo():
                    estado_panel = "CÁMARAS APAGADAS"
                    color_panel = (111, 226, 188)
                else:
                    estado_panel = "CÁMARAS ACTIVAS"
                    color_panel = (241, 184, 79)
                self.__texto(estado_panel, 685, 52, color_panel, self.__fuente_pequena)

    def __dibujar_mapa(self, nivel, tiles):
        mapa = nivel.get_mapa()
        ancho, alto = mapa.get_dimensiones()
        cols = ancho // TAMANO_CELDA
        filas = alto // TAMANO_CELDA
        muros_set = {(m.x // TAMANO_CELDA, m.y // TAMANO_CELDA) for m in mapa.get_muros()}

        # Suelo y sombras proyectadas por los muros.
        for fila in range(filas):
            for col in range(cols):
                destino = (ORIGEN[0] + col * TAMANO_CELDA, ORIGEN[1] + fila * TAMANO_CELDA)
                if (col, fila) in muros_set:
                    continue
                tile_suelo = tiles["suelo_grieta"] if (col * 7 + fila * 13) % 11 == 0 else tiles["suelo"]
                self.__pantalla.blit(tile_suelo, destino)
                if (col, fila - 1) in muros_set:
                    self.__pantalla.blit(self.__recursos["sombra_abajo"], destino)
                if (col - 1, fila) in muros_set:
                    self.__pantalla.blit(self.__recursos["sombra_lado"], destino)

        # Muros con variación y lámparas en el borde superior/inferior.
        for col, fila in muros_set:
            destino = (ORIGEN[0] + col * TAMANO_CELDA, ORIGEN[1] + fila * TAMANO_CELDA)
            tile_muro = tiles["muro_alt"] if (col, fila - 1) in muros_set else tiles["muro"]
            self.__pantalla.blit(tile_muro, destino)
            if fila in (0, filas - 1) and col in (4, 10, 15):
                self.__pantalla.blit(tiles["lampara"], destino)

    def __dibujar_camaras(self, nivel, tiles):
        for camara in nivel.get_camaras():
            zona = self.__a_pantalla(camara.get_zona())
            activa = camara.detectar(camara.get_zona())

            capa = pygame.Surface((zona.width, zona.height), pygame.SRCALPHA)
            if activa:
                capa.fill((241, 184, 79, 62))
                borde = (241, 184, 79)
                sprite_cam = tiles["camara_activa"]
            else:
                capa.fill((120, 136, 154, 24))
                borde = (110, 126, 144)
                sprite_cam = tiles["camara"]

            self.__pantalla.blit(capa, zona.topleft)
            pygame.draw.rect(self.__pantalla, borde, zona, 1)
            self.__pantalla.blit(sprite_cam, sprite_cam.get_rect(midtop=(zona.centerx, zona.top + 2)))

    def __dibujar_objetos(self, nivel, tiles, tiempo):
        area = pygame.Rect(ORIGEN[0], ORIGEN[1], *nivel.get_mapa().get_dimensiones())
        self.__pantalla.set_clip(area)

        # Puerta de salida con halo verde.
        puerta_rect = self.__a_pantalla(nivel.get_puerta().get_rect())
        tiene_llave = nivel.get_prisionero().tiene_llave()
        halo_salida = self.__recursos["halo_salida"] if tiene_llave else self.__recursos["halo_salida_tenue"]
        self.__pantalla.blit(halo_salida, halo_salida.get_rect(center=puerta_rect.center), special_flags=pygame.BLEND_RGB_ADD)
        sprite_puerta = tiles["salida"] if tiene_llave else tiles["salida_bloqueada"]
        self.__pantalla.blit(sprite_puerta, puerta_rect.topleft)

        # Llave con flotación suave y halo ámbar.
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
            self.__pantalla.blit(sprite_llave, sprite_llave.get_rect(center=(llave_rect.centerx, llave_rect.centery + flote)))

        # Panel de seguridad.
        panel = nivel.get_panel()
        if panel is not None:
            panel_rect = self.__a_pantalla(panel.get_rect())
            self.__pantalla.blit(tiles["panel"], panel_rect.topleft)
            color_borde = (111, 226, 188) if panel.esta_activo() else (110, 195, 250)
            pygame.draw.rect(self.__pantalla, color_borde, panel_rect, 2, border_radius=4)

        self.__pantalla.set_clip(None)

    def __dibujar_personajes(self, nivel, tiempo):
        for personaje in nivel.get_personajes():
            rect = self.__a_pantalla(personaje.get_rect())
            clave = id(personaje)
            anterior = self.__posiciones_previas.get(clave, rect.center)
            dx = rect.centerx - anterior[0]
            dy = rect.centery - anterior[1]
            en_movimiento = dx != 0 or dy != 0

            direccion = _direccion_desde_vector(dx, dy, self.__direcciones.get(clave, "abajo"))
            self.__direcciones[clave] = direccion
            self.__posiciones_previas[clave] = rect.center

            es_preso = isinstance(personaje, Prisionero)
            ritmo = 10.0 if es_preso else 7.5
            frame = SECUENCIA_PASO[int(tiempo * ritmo) % len(SECUENCIA_PASO)] if en_movimiento else 0
            grupo = "preso" if es_preso else "guardia"
            sprite = self.__recursos[grupo][direccion][frame]

            if not es_preso and personaje.esta_alerta():
                pygame.draw.ellipse(
                    self.__pantalla,
                    (250, 100, 112),
                    (rect.centerx - 16, rect.bottom - 8, 32, 10),
                    2,
                )
            self.__pantalla.blit(sprite, sprite.get_rect(center=rect.center))
            if not es_preso and personaje.esta_alerta():
                self.__texto("!", rect.centerx - 4, rect.top - 24, (250, 100, 112), self.__fuente_mediana)

    def __dibujar_pie(self, nivel):
        texto = "WASD / Flechas: Mover  ·  P / ESC: Pausa  ·  F11: Pantalla completa  ·  Panel azul apaga cámaras (alerta guardias)"
        self.__texto(texto, ORIGEN[0], 628, (145, 168, 190), self.__fuente_pequena)

    def __dibujar_overlay(self, titulo, detalle, accion, color):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((6, 11, 18, 190))
        self.__pantalla.blit(capa, (0, 0))

        caja = pygame.Rect(190, 215, 520, 210)
        pygame.draw.rect(self.__pantalla, (24, 37, 50), caja, border_radius=14)
        pygame.draw.rect(self.__pantalla, color, caja, 2, border_radius=14)

        self.__texto(titulo, caja.x + 32, caja.y + 30, color, self.__fuente_mediana)
        self.__texto(detalle, caja.x + 32, caja.y + 84, (225, 234, 242), self.__fuente)
        self.__texto(accion, caja.x + 32, caja.y + 132, (242, 206, 114), self.__fuente)
        self.__texto("Cierra la ventana para salir", caja.x + 32, caja.y + 170, (145, 168, 190), self.__fuente_pequena)
