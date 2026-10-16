"""Ruido, persecución, memoria de la última posición y captura por contacto."""
import math
import unittest
from unittest.mock import patch

from src.estados import Derrota, Jugando
from src.geometria import dentro_de_vision
from src.juego import Juego
from src.mapa import Mapa, centro
from src.nivel import Camara
from tests.test_juego import ubicar


def mapa_prueba(muros=()):
    filas = [["#" if x in (0, 23) or y in (0, 13) else "." for x in range(24)] for y in range(14)]
    for x, y in muros:
        filas[y][x] = "#"
    return Mapa(tuple("".join(fila) for fila in filas))


class PruebasVigilancia(unittest.TestCase):
    def setUp(self):
        self.juego = Juego()
        self.nivel = self.juego.nivel
        self.nivel.celda = None
        self.nivel.mapa = mapa_prueba()
        self.nivel.ruidos.mapa = self.nivel.mapa
        self.guardia = self.nivel.guardias[0]
        self.nivel.guardias = [self.guardia]
        self.nivel.personajes = [self.nivel.prisionero, self.guardia]
        self.nivel.ruidos.oyentes = [self.guardia]
        self.nivel.camaras = []
        ubicar(self.guardia, centro(7, 5))
        self.guardia.angulo = 0
        ubicar(self.nivel.prisionero, centro(3, 11))

    def test_ruido_investiga_sin_captura_instantanea(self):
        origen = centro(7, 7)
        self.nivel.ruidos.emitir(origen, 100)
        self.assertEqual(self.guardia.modo, "INVESTIGA")
        self.assertEqual(self.guardia.ultima_posicion, origen)
        self.assertIsInstance(self.juego.estado, Jugando)

    def test_carrera_por_pasillo_real_hace_investigar_sin_teletransportes(self):
        from tests.recorridos import acercarse_haciendo_ruido
        juego = Juego()
        acercarse_haciendo_ruido(juego)
        self.assertTrue(any(g.modo == "INVESTIGA" for g in juego.nivel.guardias))
        self.assertIsInstance(juego.estado, Jugando)

    def test_sonido_rodea_paredes_sin_atravesarlas(self):
        self.nivel.mapa = mapa_prueba([(8, 5)])
        self.nivel.ruidos.mapa = self.nivel.mapa
        origen = centro(9, 5)
        self.nivel.ruidos.emitir(origen, 80)
        self.assertEqual(self.guardia.modo, "PATRULLA")
        self.nivel.ruidos.emitir(origen, 210)
        self.assertEqual(self.guardia.modo, "INVESTIGA")

    def test_quieto_o_empujando_pared_no_emite_pasos(self):
        jugador = self.nivel.prisionero
        ubicar(jugador, (48, 90))
        with patch.object(self.nivel.ruidos, "emitir") as emitir:
            for teclas in (set(), {"izquierda"}):
                for _ in range(20):
                    self.nivel.dt = .05
                    self.nivel.teclas = teclas
                    jugador.update()
            emitir.assert_not_called()
        self.assertEqual(jugador.get_posicion(), (48, 90))

    def test_sigilo_caminar_y_carrera_emiten_distinto_ruido(self):
        for accion, esperado in (({"sigilo"}, 20), (set(), 80), ({"carrera"}, 210)):
            with self.subTest(accion=accion):
                juego = Juego()
                jugador = juego.nivel.prisionero
                if "carrera" in accion:
                    juego.manejar_entrada("carrera")
                with patch.object(juego.nivel.ruidos, "emitir") as emitir:
                    for _ in range(12):
                        juego.nivel.dt = .05
                        juego.nivel.teclas = {"derecha"} | accion
                        jugador.update()
                    self.assertTrue(emitir.called)
                    self.assertTrue(all(c.args[1] == esperado for c in emitir.call_args_list))

    def test_ver_inicia_persecucion_y_solo_contacto_captura(self):
        ubicar(self.nivel.prisionero, centro(10, 5))
        self.juego.actualizar(.05, set())
        self.assertEqual(self.guardia.modo, "PERSIGUE")
        self.assertIsInstance(self.juego.estado, Jugando)
        for _ in range(40):
            self.juego.actualizar(.05, set())
        self.assertIsInstance(self.juego.estado, Derrota)

    def test_pared_oculta_y_guardia_no_conoce_posicion_nueva(self):
        self.nivel.mapa = mapa_prueba([(8, y) for y in range(1, 11)])
        self.nivel.ruidos.mapa = self.nivel.mapa
        conocida = centro(7, 7)
        self.guardia.alertar(conocida)
        ubicar(self.nivel.prisionero, centro(10, 5))
        for _ in range(10):
            self.nivel.dt = .05
            self.guardia.update()
        self.assertEqual(self.guardia.modo, "BUSCA")
        self.assertEqual(self.guardia.ultima_posicion, conocida)

    def test_persecucion_encuentra_puerta_y_no_cruza_pared(self):
        self.nivel.mapa = mapa_prueba([(8, y) for y in range(1, 11)])
        self.nivel.ruidos.mapa = self.nivel.mapa
        ubicar(self.nivel.prisionero, centro(9, 5))
        self.guardia.alertar(self.nivel.prisionero.get_posicion())
        self.assertFalse(self.guardia.puede_capturar(self.nivel.prisionero))
        for _ in range(300):
            self.juego.actualizar(.05, set())
            self.assertTrue(self.nivel.posicion_valida(*self.guardia.get_posicion(), self.guardia.radio))
            if isinstance(self.juego.estado, Derrota):
                break
        self.assertIsInstance(self.juego.estado, Derrota)

    def test_investiga_y_regresa_a_patrulla_si_no_encuentra_jugador(self):
        self.guardia.escuchar(centro(9, 5))
        for _ in range(130):
            self.nivel.dt = .05
            self.guardia.update()
        self.assertEqual(self.guardia.modo, "PATRULLA")
        self.assertIsNone(self.guardia.ultima_posicion)

    def test_camara_considera_el_cuerpo_y_la_cobertura(self):
        camara = Camara((0, 0), 0)
        posicion = (80 * math.cos(math.radians(33)), 80 * math.sin(math.radians(33)))
        ubicar(self.nivel.prisionero, posicion)
        self.assertFalse(dentro_de_vision((0, 0), posicion, 0, 95, math.pi / 3, []))
        self.assertTrue(camara.detectar(self.nivel.prisionero, []))
        self.assertFalse(camara.detectar(self.nivel.prisionero, [(20, -100, 10, 200)]))

    def test_alarmas_de_los_tres_mapas_alertan_a_todos_sin_derrota_instantanea(self):
        for indice in range(3):
            for numero in range(indice + 1):
                juego = Juego()
                juego.indice_nivel = indice
                juego._cargar_nivel()
                nivel = juego.nivel
                camara = nivel.camaras[numero]
                x, y = camara.posicion
                ubicar(nivel.prisionero, (x + math.cos(camara.angulo) * 30,
                                          y + math.sin(camara.angulo) * 30))
                juego.actualizar(0, set())
                self.assertTrue(camara.activa)
                self.assertTrue(all(g.modo == "PERSIGUE" for g in nivel.guardias))
                self.assertIsInstance(juego.estado, Jugando)
