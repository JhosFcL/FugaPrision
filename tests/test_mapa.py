"""Perímetros cerrados, ausencia de huecos aislados y barrido contra las paredes."""
from collections import deque
import math
import unittest

from src.geometria import distancia
from src.mapa import Mapa, PLANOS, COLUMNAS, FILAS, centro
from src.nivel import Nivel
from src.puntuacion import Puntaje


class PruebasMapa(unittest.TestCase):
    def test_todo_el_suelo_es_accesible_y_no_hay_huecos_de_una_celda(self):
        for plano in PLANOS:
            plano = tuple(fila.replace("P", ".") for fila in plano)
            suelo = {(x, y) for y, fila in enumerate(plano) for x, celda in enumerate(fila) if celda == "."}
            pendientes = deque([next(iter(suelo))])
            visitadas = set(pendientes)
            while pendientes:
                x, y = pendientes.popleft()
                vecinas = {(x+1,y), (x-1,y), (x,y+1), (x,y-1)} & suelo
                self.assertGreaterEqual(len(vecinas), 2)
                for vecina in vecinas - visitadas:
                    visitadas.add(vecina)
                    pendientes.append(vecina)
            self.assertEqual(visitadas, suelo)

    def test_movimiento_grande_y_diagonal_no_atraviesa_paredes(self):
        for plano in PLANOS:
            mapa = Mapa(plano)
            for posicion in (centro(2, 11), centro(2, 2), centro(21, 2), centro(21, 11)):
                for indice in range(16):
                    angulo = math.tau * indice / 16
                    final = mapa.desplazar(posicion, math.cos(angulo) * 4000, math.sin(angulo) * 4000, 12)
                    self.assertTrue(mapa.posicion_valida(*final, 12), (posicion, final))
                    self.assertTrue(48 <= final[0] <= COLUMNAS*36-48)
                    self.assertTrue(48 <= final[1] <= FILAS*36-48)

    def test_divisiones_obligan_a_usar_puertas_y_caminos_transitables(self):
        for indice in range(3):
            nivel = Nivel(Puntaje(), indice)
            if nivel.celda:
                nivel.mapa.abrir_puerta(nivel.celda.posicion)
            inicio = nivel.prisionero.get_posicion()
            ruta = nivel.mapa.buscar_ruta(inicio, nivel.llave.posicion)
            ruta += nivel.mapa.buscar_ruta(nivel.llave.posicion, nivel.salida.posicion)
            self.assertTrue(ruta)
            recorrido = (nivel.mapa.distancia_camino(inicio, nivel.llave.posicion)
                         + nivel.mapa.distancia_camino(nivel.llave.posicion, nivel.salida.posicion))
            directo = distancia(inicio, nivel.llave.posicion) + distancia(nivel.llave.posicion, nivel.salida.posicion)
            self.assertGreater(recorrido, directo * 1.5)
            for punto in ruta:
                self.assertTrue(nivel.posicion_valida(*punto, 12))

    def test_plano_abierto_o_con_tamano_incorrecto_se_rechaza(self):
        with self.assertRaises(ValueError):
            Mapa(("."*COLUMNAS,)*FILAS)
        with self.assertRaises(ValueError):
            Mapa(("###",)*3)

    def test_celda_bloquea_paso_y_exige_interaccion_cercana_continua(self):
        from src.juego import Juego
        juego = Juego()
        nivel = juego.nivel
        jugador = nivel.prisionero
        self.assertFalse(nivel.mapa.buscar_ruta(jugador.get_posicion(), nivel.llave.posicion))
        for _ in range(50):
            juego.actualizar(.05, {"interactuar"})
        self.assertFalse(nivel.celda.abierta)
        jugador.mover(100, 0)
        for _ in range(20):
            juego.actualizar(.05, {"interactuar"})
        self.assertGreater(nivel.celda.progreso, 0)
        juego.actualizar(.05, set())
        self.assertEqual(nivel.celda.progreso, 0)
        for _ in range(41):
            juego.actualizar(.05, {"interactuar"})
        self.assertTrue(nivel.celda.abierta)
        self.assertTrue(nivel.mapa.buscar_ruta(jugador.get_posicion(), nivel.llave.posicion))
        juego.reintentar_nivel()
        self.assertFalse(juego.nivel.celda.abierta)

    def test_camaras_estan_fijadas_a_pared_y_apuntan_al_suelo(self):
        for indice in range(3):
            nivel = Nivel(Puntaje(), indice)
            for camara in nivel.camaras:
                dx, dy = math.cos(camara.angulo), math.sin(camara.angulo)
                atras = (int((camara.posicion[0] - dx * 10) // 36),
                         int((camara.posicion[1] - dy * 10) // 36))
                frente = (camara.posicion[0] + dx * 25, camara.posicion[1] + dy * 25)
                self.assertEqual(nivel.mapa.plano[atras[1]][atras[0]], "#")
                self.assertTrue(nivel.posicion_valida(*frente, 10))

    def test_patio_tiene_galerias_horizontales_y_recorrido_de_ida_y_vuelta(self):
        nivel = Nivel(Puntaje(), 2)
        self.assertGreater(nivel.mapa.plano[4].count("#"), 18)
        self.assertGreater(nivel.mapa.plano[9].count("#"), 18)
        self.assertEqual(len(nivel.guardias), 3)
        for origen, destino in ((nivel.prisionero.get_posicion(), nivel.llave.posicion),
                                (nivel.llave.posicion, nivel.salida.posicion)):
            ruta = nivel.mapa.buscar_ruta(origen, destino)
            self.assertTrue(any(p[0] > 18 * 36 for p in ruta))
            self.assertTrue(any(p[0] < 6 * 36 for p in ruta))

    def test_llave_del_patio_abre_atajos_y_no_antes(self):
        from src.juego import Juego
        from tests.test_juego import ubicar
        juego = Juego()
        juego.indice_nivel = 2
        juego._cargar_nivel()
        nivel = juego.nivel
        for casilla in nivel.configuracion["atajos"]:
            self.assertFalse(nivel.posicion_valida(*centro(*casilla), 12))
        ubicar(nivel.prisionero, nivel.llave.posicion)
        juego.actualizar(0, set())
        for casilla in nivel.configuracion["atajos"]:
            self.assertTrue(nivel.posicion_valida(*centro(*casilla), 12))
        self.assertEqual(juego.panel.valor, 100)
