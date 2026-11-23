"""Vista Pygame con tiles y sprites animados. Las reglas se conservan fuera de esta clase."""
import math
from pathlib import Path
import pygame
from .geometria import distancia, poligono_vision
from .mapa import TAMANO, COLUMNAS, FILAS

ANCHO = 1000
ALTO = 760
ORIGEN = (68, 152)
RUTA_IMG = Path(__file__).resolve().parents[1] / "img"
DIRECCIONES = ("abajo", "izquierda", "derecha", "arriba")
SECUENCIA_PASO = (0, 1, 0, 2)

DECORACIONES = (
    (
        (1, 1, "barril"), (5, 1, "caja_metal"), (16, 1, "tubo_codo"),
        (1, 7, "caja"), (22, 5, "caja"), (1, 12, "barril"),
        (20, 12, "carrito"), (22, 12, "caja"),
        (14, 3, "rejilla"), (16, 11, "rejilla"), (10, 12, "rejilla"),
    ),
    (
        (1, 1, "barril"), (7, 1, "panel"), (21, 1, "caja"),
        (7, 10, "caja"), (7, 11, "barril"), (15, 11, "barril"),
        (16, 11, "lona"), (15, 9, "marca_suelo"),
        (1, 6, "papeles"), (1, 12, "papeles"), (11, 10, "papeles"), (19, 6, "papeles"),
        (5, 5, "rejilla"), (10, 1, "rejilla"), (14, 6, "rejilla"),
        (10, 12, "rejilla"), (21, 5, "rejilla"),
    ),
    (
        (4, 1, "panel"), (22, 1, "barril"),
        (6, 1, "rejilla"), (20, 2, "rejilla"), (13, 5, "rejilla"),
        (4, 7, "rejilla"), (16, 11, "rejilla"),
    ),
    (
        (1, 1, "cajas"), (3, 1, "tubo_rojo"), (4, 1, "tubo_rojo"), (5, 1, "panel"),
        (18, 1, "rejilla"), (22, 1, "cajas"), (1, 12, "cajas"), (22, 12, "cajas"),
    ),
)

LAMPARAS_MURO = (
    {(c, 0) for c in (3, 8, 14, 20)} | {(c, FILAS - 1) for c in (3, 9, 15, 20)},
    {(c, 0) for c in (6, 14, 19)} | {(c, FILAS - 1) for c in (8, 15)},
    {(2, 0), (8, 0), (17, 0), (6, FILAS - 1), (16, FILAS - 1), (0, 5), (0, 10), (23, 5), (23, 10)},
    {(c, 0) for c in (3, 9, 14, 20)} | {(c, FILAS - 1) for c in (3, 9, 14, 20)},
)

VENTANAS_MURO = (
    {(0, 5), (0, 10), (6, 4), (6, 9), (12, 8), (18, 2), (18, 7), (23, 2), (23, 7)},
    {(0, 5), (0, 10), (6, 4), (6, 9), (12, 3), (12, 8), (18, 2), (18, 7), (23, 4), (23, 10)},
    {(23, 2), (23, 6), (23, 11)},
    {(0, 4), (0, 9), (23, 4), (23, 9)},
)

FRANJAS_PELIGRO = {
    (3, 4), (4, 4), (8, 8), (9, 8), (14, 5), (15, 5), (20, 7), (21, 7),
}

AMBIENTES = (
    (142, 148, 168),
    (132, 146, 166),
    (138, 144, 164),
    (138, 128, 152),
)

BARRILES_ARENA = ((5, 5), (18, 5), (5, 8), (18, 8))


def _cargar_imagen(ruta, tamano=None):
    imagen = pygame.image.load(str(ruta)).convert_alpha()
    if tamano and imagen.get_size() != tamano:
        imagen = pygame.transform.scale(imagen, tamano)
    return imagen


def _cargar_personaje(carpeta, prefijo, tamano=None):
    base = RUTA_IMG / carpeta
    frames = [_cargar_imagen(base / f"{prefijo}_{indice:02d}.png", tamano) for indice in range(1, 13)]
    return {direccion: frames[i * 3:(i + 1) * 3] for i, direccion in enumerate(DIRECCIONES)}


def _cargar_mapas():
    t = (TAMANO, TAMANO)
    etiq = (48, 30)
    c = RUTA_IMG / "mapas" / "celda_v2"
    l = RUTA_IMG / "mapas" / "lavanderia_v2"
    p = RUTA_IMG / "mapas" / "patio_v2"
    a = RUTA_IMG / "mapas" / "arena_v2"

    llave_comun = _cargar_imagen(c / "pabellon_tiles_07.png", (32, 32))
    etq_camara = _cargar_imagen(c / "pabellon_tiles_64.png", etiq)
    etq_llave = _cargar_imagen(c / "pabellon_tiles_65.png", etiq)
    cam_normal = _cargar_imagen(c / "pabellon_tiles_13.png", (32, 32))
    cam_activa = _cargar_imagen(c / "pabellon_tiles_70.png", (32, 32))
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
        "objeto": _cargar_imagen(c / "pabellon_tiles_06.png", t),
        "llave": llave_comun,
        "salida": _cargar_imagen(c / "pabellon_tiles_08.png", t),
        "salida_bloqueada": _cargar_imagen(c / "pabellon_tiles_69.png", t),
        "etq_camara": etq_camara,
        "etq_llave": etq_llave,
        "etq_salida": _cargar_imagen(c / "pabellon_tiles_66.png", etiq),
        "camara": cam_normal,
        "camara_activa": cam_activa,
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
        "puerta_abierta": puerta_abierta,
        "barrotes": _cargar_imagen(l / "tiles_08.png", t),
        "objeto": _cargar_imagen(l / "tiles_55.png", t),
        "objeto_alt": _cargar_imagen(l / "tiles_56.png", t),
        "llave": _cargar_imagen(l / "tiles_48.png", (32, 32)),
        "salida": _cargar_imagen(l / "tiles_05.png", t),
        "salida_bloqueada": _cargar_imagen(l / "tiles_47.png", t),
        "etq_camara": _cargar_imagen(l / "tiles_50.png", etiq),
        "etq_llave": _cargar_imagen(l / "tiles_51.png", etiq),
        "etq_salida": _cargar_imagen(l / "tiles_45.png", etiq),
        "camara": _cargar_imagen(l / "tiles_49.png", (32, 32)),
        "camara_activa": _cargar_imagen(l / "tiles_52.png", (32, 32)),
        "rejilla": _cargar_imagen(l / "tiles_06.png", t),
        "barril": _cargar_imagen(l / "tiles_53.png", t),
        "caja": caja_madera,
        "panel": _cargar_imagen(l / "tiles_57.png", t),
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
        "puerta_abierta": puerta_abierta,
        "barrotes": _cargar_imagen(p / "tiles_08.png", t),
        "objeto": caja_madera,
        "llave": llave_comun,
        "salida": _cargar_imagen(p / "tiles_05.png", t),
        "salida_bloqueada": _cargar_imagen(p / "tiles_55.png", t),
        "etq_camara": etq_camara,
        "etq_llave": etq_llave,
        "etq_salida": _cargar_imagen(p / "tiles_53.png", etiq),
        "camara": cam_normal,
        "camara_activa": cam_activa,
        "rejilla": _cargar_imagen(p / "tiles_06.png", t),
        "barril": _cargar_imagen(p / "tiles_56.png", t),
        "panel": _cargar_imagen(p / "tiles_59.png", t),
    }

    arena = {
        "suelo": _cargar_imagen(a / "tiles_01.png", t),
        "suelo_grieta": _cargar_imagen(a / "tiles_02.png", t),
        "suelo_alt": _cargar_imagen(a / "tiles_10.png", t),
        "muro": _cargar_imagen(a / "tiles_03.png", t),
        "muro_alt": _cargar_imagen(a / "tiles_16.png", t),
        "ventana": _cargar_imagen(a / "tiles_08.png", t),
        "lampara": _cargar_imagen(a / "tiles_07.png", t),
        "puerta_abierta": puerta_abierta,
        "barrotes": _cargar_imagen(a / "tiles_08.png", t),
        "objeto": _cargar_imagen(a / "tiles_60.png", t),
        "llave": llave_comun,
        "salida": _cargar_imagen(a / "tiles_05.png", t),
        "salida_bloqueada": _cargar_imagen(a / "tiles_57.png", t),
        "etq_camara": etq_camara,
        "etq_llave": etq_llave,
        "etq_salida": _cargar_imagen(a / "tiles_55.png", etiq),
        "camara": cam_normal,
        "camara_activa": cam_activa,
        "rejilla": _cargar_imagen(a / "tiles_06.png", t),
        "cajas": _cargar_imagen(a / "tiles_62.png", t),
        "panel": _cargar_imagen(a / "tiles_61.png", t),
        "tubo_rojo": _cargar_imagen(a / "tiles_63.png", t),
    }
    return [celda, lavanderia, patio, arena]


def _crear_sombra(ancho, alto, horizontal=False, maximo=100):
    sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    largo = ancho if horizontal else alto
    for i in range(largo):
        alpha = round(maximo * (1 - i / largo) ** 1.4)
        if horizontal:
            pygame.draw.line(sombra, (6, 8, 14, alpha), (i, 0), (i, alto - 1))
        else:
            pygame.draw.line(sombra, (6, 8, 14, alpha), (0, i), (ancho - 1, i))
    return sombra


def _escala_halo(ruta, tamano, alpha):
    origen = _cargar_imagen(ruta, (tamano, tamano))
    origen.set_alpha(alpha)
    halo = pygame.Surface((tamano, tamano))
    halo.fill((0, 0, 0))
    halo.blit(origen, (0, 0))
    return halo


def _construir_mapa_luz(indice, halo_luz, halo_barril):
    capa = pygame.Surface((COLUMNAS * TAMANO, FILAS * TAMANO))
    capa.fill(AMBIENTES[indice])
    for columna, fila in LAMPARAS_MURO[indice]:
        cx = (columna + 0.5) * TAMANO
        cy = (fila + 0.5) * TAMANO
        if fila == 0:
            cy += 18
        elif fila == FILAS - 1:
            cy -= 18
        if columna == 0:
            cx += 18
        elif columna == COLUMNAS - 1:
            cx -= 18
        rect = halo_luz.get_rect(center=(round(cx), round(cy)))
        capa.blit(halo_luz, rect, special_flags=pygame.BLEND_RGB_ADD)
    if indice == 3:
        for columna, fila in BARRILES_ARENA:
            cx, cy = (columna + 0.5) * TAMANO, (fila + 0.5) * TAMANO
            rect = halo_barril.get_rect(center=(round(cx), round(cy)))
            capa.blit(halo_barril, rect, special_flags=pygame.BLEND_RGB_ADD)
    return capa


def _cargar_recursos():
    c = RUTA_IMG / "mapas" / "celda_v2"
    halo_luz = _escala_halo(c / "halo_ambar.png", 176, 175)
    halo_barril = _escala_halo(c / "halo_ambar.png", 124, 120)
    return {
        "preso": _cargar_personaje("preso", "preso", (TAMANO, TAMANO)),
        "guardia": _cargar_personaje("guardias", "guardia", (TAMANO, TAMANO)),
        "alcaide": _cargar_personaje("alcaide", "alcaide", (TAMANO * 2, TAMANO * 2)),
        "mapas": _cargar_mapas(),
        "sombra_abajo": _crear_sombra(TAMANO, 12, False, 105),
        "sombra_lado": _crear_sombra(8, TAMANO, True, 65),
        "luces": [_construir_mapa_luz(i, halo_luz, halo_barril) for i in range(4)],
        "halo_lampara": _escala_halo(c / "halo_ambar.png", 104, 42),
        "halo_llave": _escala_halo(c / "halo_ambar.png", 86, 62),
        "halo_salida": _escala_halo(c / "halo_verde.png", 160, 210),
        "halo_salida_tenue": _escala_halo(c / "halo_verde.png", 132, 125),
    }


def _direccion_desde_vector(dx, dy, actual="abajo"):
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return actual
    if abs(dx) >= abs(dy):
        return "derecha" if dx > 0 else "izquierda"
    return "abajo" if dy > 0 else "arriba"


def _indice_frame(tiempo, ritmo, en_movimiento):
    if not en_movimiento:
        return 0
    return SECUENCIA_PASO[int(tiempo * ritmo) % len(SECUENCIA_PASO)]


def _es_objeto_interior(indice, columna, fila):
    if indice == 1:
        return 0 < fila < FILAS - 1 and columna not in (0, 6, 12, 18, COLUMNAS - 1)
    if indice == 2:
        return fila not in (0, 4, 9, FILAS - 1) and columna not in (0, COLUMNAS - 1)
    if indice == 3:
        return 0 < fila < FILAS - 1 and 0 < columna < COLUMNAS - 1
    return False


class Vista:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("segoeui", 18)
        self.pequena = pygame.font.SysFont("segoeui", 15)
        self.titulo = pygame.font.SysFont("segoeui", 32, bold=True)
        self.mediana = pygame.font.SysFont("segoeui", 23, bold=True)
        self.recursos = _cargar_recursos()
        self._direccion_preso = "abajo"
        self._posicion_preso = None
        self._nivel_actual = None

    def texto(self, texto, x, y, color=(225, 234, 242), fuente=None):
        imagen = (fuente or self.fuente).render(texto, True, color)
        self.pantalla.blit(imagen, (x, y))

    def punto(self, posicion):
        return round(posicion[0] + ORIGEN[0]), round(posicion[1] + ORIGEN[1])

    def _dibujar_sprite(self, sprite, posicion):
        rect = sprite.get_rect(center=posicion)
        self.pantalla.blit(sprite, rect)

    def _actualizar_direccion_preso(self, nivel):
        posicion = nivel.prisionero.get_posicion()
        if nivel is not self._nivel_actual:
            self._nivel_actual = nivel
            self._direccion_preso = "abajo"
            self._posicion_preso = posicion
        dx = int("derecha" in nivel.teclas) - int("izquierda" in nivel.teclas)
        dy = int("abajo" in nivel.teclas) - int("arriba" in nivel.teclas)
        if dx != 0 or dy != 0:
            self._direccion_preso = _direccion_desde_vector(dx, dy, self._direccion_preso)
        elif self._posicion_preso is not None and distancia(self._posicion_preso, posicion) > 0.1:
            self._direccion_preso = _direccion_desde_vector(
                posicion[0] - self._posicion_preso[0],
                posicion[1] - self._posicion_preso[1],
                self._direccion_preso,
            )
        self._posicion_preso = posicion

    def _dibujar_vision(self, origen, angulo, alcance, apertura, muros, color):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        puntos = [self.punto(punto) for punto in
                  poligono_vision(origen, angulo, alcance, apertura, muros)]
        pygame.draw.polygon(capa, (*color, 55), puntos)
        pygame.draw.lines(capa, (*color, 120), False, puntos[1:], 1)
        self.pantalla.blit(capa, (0, 0))

    def dibujar(self, juego):
        nivel = juego.nivel
        self._actualizar_direccion_preso(nivel)
        self.pantalla.fill((13, 21, 31))
        self._dibujar_encabezado(juego)
        self._dibujar_mapa(nivel)
        if nivel.celda:
            self._dibujar_celda(nivel.celda)
        self._dibujar_objetivos(nivel)
        for camara in nivel.camaras:
            self._dibujar_camara(camara, nivel.indice)
        self._dibujar_ambiente(nivel)
        for guardia in nivel.guardias:
            self._dibujar_guardia(guardia, nivel.tiempo)
        if nivel.combate:
            self._dibujar_combate(nivel)
        self._dibujar_prisionero(nivel)
        self._dibujar_controles(nivel)
        if juego.estado.nombre != "JUGANDO":
            self._dibujar_panel_estado(juego)

    def _dibujar_ambiente(self, nivel):
        area = pygame.Rect(*ORIGEN, COLUMNAS * TAMANO, FILAS * TAMANO)
        self.pantalla.blit(self.recursos["luces"][nivel.indice], ORIGEN, special_flags=pygame.BLEND_RGB_MULT)
        self.pantalla.set_clip(area)
        halo_lampara = self.recursos["halo_lampara"]
        for columna, fila in LAMPARAS_MURO[nivel.indice]:
            x = round(ORIGEN[0] + (columna + 0.5) * TAMANO)
            y = round(ORIGEN[1] + (fila + 0.5) * TAMANO)
            if fila == 0:
                y += 12
            elif fila == FILAS - 1:
                y -= 12
            elif columna == 0:
                x += 12
            elif columna == COLUMNAS - 1:
                x -= 12
            self.pantalla.blit(halo_lampara, halo_lampara.get_rect(center=(x, y)), special_flags=pygame.BLEND_RGB_ADD)
        halo_salida = self.recursos["halo_salida"] if nivel.prisionero.tiene_llave() else self.recursos["halo_salida_tenue"]
        salida = self.punto(nivel.salida.posicion)
        self.pantalla.blit(halo_salida, halo_salida.get_rect(center=salida), special_flags=pygame.BLEND_RGB_ADD)
        if nivel.llave.disponible:
            llave = self.punto(nivel.llave.posicion)
            halo_llave = self.recursos["halo_llave"]
            self.pantalla.blit(halo_llave, halo_llave.get_rect(center=llave), special_flags=pygame.BLEND_RGB_ADD)
        if nivel.celda and not nivel.celda.abierta:
            celda = self.punto(nivel.celda.posicion)
            halo_llave = self.recursos["halo_llave"]
            self.pantalla.blit(halo_llave, halo_llave.get_rect(center=celda), special_flags=pygame.BLEND_RGB_ADD)
        self.pantalla.set_clip(None)

    def _dibujar_prisionero(self, nivel):
        if nivel.combate and nivel.combate.inmune > 0 and int(nivel.tiempo * 12) % 2 != 0:
            return
        movimiento = nivel.prisionero.movimiento
        ritmo = {"QUIETO": 0.0, "SIGILO": 5.5, "CAMINA": 9.5, "CORRE": 14.0}[movimiento]
        frame = _indice_frame(nivel.tiempo, ritmo, movimiento != "QUIETO")
        sprite = self.recursos["preso"][self._direccion_preso][frame]
        self._dibujar_sprite(sprite, self.punto(nivel.prisionero.get_posicion()))

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
        indice = nivel.indice
        tiles = self.recursos["mapas"][indice]
        atajos = set(nivel.configuracion.get("atajos", []))
        lamparas = LAMPARAS_MURO[indice]
        ventanas = VENTANAS_MURO[indice]
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                destino = (ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO)
                celda = nivel.mapa.plano[fila][columna]
                if (columna, fila) in atajos and celda == ".":
                    self.pantalla.blit(tiles["puerta_abierta"], destino)
                elif (columna * 7 + fila * 13) % 11 == 0:
                    self.pantalla.blit(tiles["suelo_grieta"], destino)
                elif (columna * 5 + fila * 3) % 7 == 0:
                    self.pantalla.blit(tiles["suelo_alt"], destino)
                else:
                    self.pantalla.blit(tiles["suelo"], destino)
        for columna, fila, clave in DECORACIONES[indice]:
            destino = (ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO)
            self.pantalla.blit(tiles[clave], destino)
        sombra_abajo = self.recursos["sombra_abajo"]
        sombra_lado = self.recursos["sombra_lado"]
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                if nivel.mapa.plano[fila][columna] in "#P":
                    continue
                destino = (ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO)
                if fila > 0 and nivel.mapa.plano[fila - 1][columna] in "#P":
                    self.pantalla.blit(sombra_abajo, destino)
                if columna > 0 and nivel.mapa.plano[fila][columna - 1] in "#P":
                    self.pantalla.blit(sombra_lado, destino)
        for camara in nivel.camaras:
            self._dibujar_vision(camara.posicion, camara.angulo, camara.alcance, camara.apertura, nivel.mapa.muros, (241, 184, 79))
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                celda = nivel.mapa.plano[fila][columna]
                if celda not in "#P":
                    continue
                destino = (ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO)
                if celda == "P":
                    self.pantalla.blit(tiles["barrotes"], destino)
                elif _es_objeto_interior(indice, columna, fila):
                    objeto = tiles.get("objeto_alt", tiles["objeto"]) if (columna + fila) % 2 else tiles["objeto"]
                    self.pantalla.blit(objeto, destino)
                elif indice == 0 and (columna, fila) in FRANJAS_PELIGRO:
                    self.pantalla.blit(tiles["muro_peligro"], destino)
                elif (columna, fila) in ventanas:
                    self.pantalla.blit(tiles["muro"], destino)
                    self.pantalla.blit(tiles["ventana"], destino)
                else:
                    muro = tiles["muro_alt"] if (fila > 0 and nivel.mapa.plano[fila - 1][columna] == "#") else tiles["muro"]
                    self.pantalla.blit(muro, destino)
                    if "tubo_muro" in tiles and fila in (0, FILAS - 1) and columna in (4, 5, 10, 11, 18, 19) and (columna, fila) not in lamparas:
                        self.pantalla.blit(tiles["tubo_muro"], destino)
                    if "alambre" in tiles and fila == 0:
                        self.pantalla.blit(tiles["alambre"], (destino[0], destino[1] - 10))
                if (columna, fila) in lamparas:
                    self.pantalla.blit(tiles["lampara"], destino)

    def _dibujar_objetivos(self, nivel):
        tiles = self.recursos["mapas"][nivel.indice]
        salida = self.punto(nivel.salida.posicion)
        desbloqueada = nivel.prisionero.tiene_llave()
        self._dibujar_sprite(tiles["salida"] if desbloqueada else tiles["salida_bloqueada"], salida)
        self._dibujar_sprite(tiles["etq_salida"], (salida[0], salida[1] + 24))
        if nivel.llave.disponible:
            x, y = self.punto(nivel.llave.posicion)
            flote = round(math.sin(nivel.tiempo * 4.5) * 2)
            self._dibujar_sprite(tiles["llave"], (x, y + flote))
            self._dibujar_sprite(tiles["etq_llave"], (x, y + 24))

    def _dibujar_celda(self, celda):
        tiles = self.recursos["mapas"][0]
        x, y = self.punto(celda.posicion)
        if celda.abierta:
            self._dibujar_sprite(tiles["puerta_abierta"], (x, y))
            return
        self._dibujar_sprite(tiles["barrotes"], (x, y))
        pygame.draw.rect(self.pantalla, (246, 210, 102), (x - 4, y - 5, 8, 10), border_radius=2)
        self.texto(f"E · {celda.progreso / 2:.0%}", x - 28, y + 20, (246, 210, 102), self.pequena)

    def _dibujar_camara(self, camara, indice):
        tiles = self.recursos["mapas"][indice]
        x, y = self.punto(camara.posicion)
        base = tiles["camara_activa"] if camara.activa else tiles["camara"]
        rotada = pygame.transform.rotate(base, 90 - math.degrees(camara.angulo))
        self._dibujar_sprite(rotada, (x, y))
        self._dibujar_sprite(tiles["etq_camara"], (x, y - 24))

    def _dibujar_guardia(self, guardia, tiempo):
        x, y = self.punto(guardia.get_posicion())
        direccion = _direccion_desde_vector(math.cos(guardia.angulo), math.sin(guardia.angulo))
        if guardia.modo == "PERSIGUE":
            en_movimiento, ritmo = True, 13.0
        elif guardia.modo == "PATRULLA":
            en_movimiento, ritmo = True, 7.0
        else:
            en_movimiento = (guardia.ultima_posicion is not None
                             and distancia(guardia.get_posicion(), guardia.ultima_posicion) > 2.5)
            ritmo = 9.5
        frame = _indice_frame(tiempo, ritmo, en_movimiento)
        sprite = self.recursos["guardia"][direccion][frame]
        self._dibujar_sprite(sprite, (x, y))
        marca = "!" if guardia.modo == "PERSIGUE" else ("?" if guardia.modo != "PATRULLA" else "")
        if marca:
            color = (255, 118, 126) if guardia.modo == "PERSIGUE" else (255, 209, 108)
            self.texto(marca, x - 5, y - 38, color, self.mediana)

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
            if jefe.fase > 1:
                aura = (255, 154, 82) if jefe.fase == 2 else (255, 78, 90)
                pygame.draw.ellipse(self.pantalla, aura, (x - 32, y + 18, 64, 18), 2)
            blanco = jefe.destino or nivel.prisionero.get_posicion()
            direccion = _direccion_desde_vector(blanco[0] - jefe.x, blanco[1] - jefe.y)
            ritmo = 14.0 if jefe.destino else (10.0 if jefe.aviso > 0 else 4.0)
            frame = _indice_frame(nivel.tiempo, ritmo, True)
            sprite = self.recursos["alcaide"][direccion][frame]
            if jefe.golpe > 0:
                sprite = sprite.copy()
                sprite.fill((95, 95, 95, 0), special_flags=pygame.BLEND_RGB_ADD)
            self._dibujar_sprite(sprite, (x, y))
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
