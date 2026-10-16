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
            inicio = nivel.prisionero.get_posicion()
            ruta = nivel.mapa.buscar_ruta(inicio, nivel.salida.posicion)
            self.assertTrue(ruta)
            self.assertGreater(nivel.mapa.distancia_camino(inicio, nivel.salida.posicion),
                               distancia(inicio, nivel.salida.posicion) * 1.5)
            for punto in ruta:
                self.assertTrue(nivel.posicion_valida(*punto, 12))

    def test_plano_abierto_o_con_tamano_incorrecto_se_rechaza(self):
        with self.assertRaises(ValueError):
            Mapa(("."*COLUMNAS,)*FILAS)
        with self.assertRaises(ValueError):
            Mapa(("###",)*3)
