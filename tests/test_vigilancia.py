"""Regresiones de detección cercana, cuerpo visible y cobertura de los muros."""
import math
import unittest

from src.geometria import dentro_de_vision, poligono_vision
from src.juego import Juego
from src.nivel import Camara
from tests.test_juego import ubicar


class PruebasVigilancia(unittest.TestCase):
    def setUp(self):
        self.nivel = Juego().nivel
        self.nivel.muros = []
        self.guardia = self.nivel.guardias[0]
        ubicar(self.guardia, (100, 100))
        self.guardia.angulo = 0

    def test_alerta_cercana_detecta_a_los_lados_y_por_detras(self):
        for dx, dy in ((0, 35), (0, -35), (-35, 0), (35, 0)):
            with self.subTest(desplazamiento=(dx, dy)):
                ubicar(self.nivel.prisionero, (100 + dx, 100 + dy))
                self.assertTrue(self.guardia.puede_detectar(self.nivel.prisionero))

    def test_cuerpo_que_toca_alerta_tambien_se_detecta(self):
        ubicar(self.nivel.prisionero, (100, 140))
        self.assertTrue(self.guardia.puede_detectar(self.nivel.prisionero))
        ubicar(self.nivel.prisionero, (100, 145))
        self.assertFalse(self.guardia.puede_detectar(self.nivel.prisionero))

    def test_espalda_fuera_de_alerta_sigue_permitiendo_sigilo(self):
        ubicar(self.nivel.prisionero, (30, 100))
        self.assertFalse(self.guardia.puede_detectar(self.nivel.prisionero))

    def test_alerta_y_vision_frontal_respetan_muros(self):
        self.nivel.muros = [(115, 80, 5, 40)]
        ubicar(self.nivel.prisionero, (135, 100))
        self.assertFalse(self.guardia.puede_detectar(self.nivel.prisionero))
        self.nivel.muros.clear()
        self.assertTrue(self.guardia.puede_detectar(self.nivel.prisionero))

    def test_camara_detecta_cuerpo_parcialmente_dentro_del_cono(self):
        camara = Camara((0, 0), 0)
        posicion = (80 * math.cos(math.radians(33)), 80 * math.sin(math.radians(33)))
        ubicar(self.nivel.prisionero, posicion)
        self.assertFalse(dentro_de_vision((0, 0), posicion, 0, 95, math.pi / 3, []))
        self.assertTrue(camara.detectar(self.nivel.prisionero, []))
        self.assertFalse(camara.detectar(self.nivel.prisionero, [(20, -100, 10, 200)]))

    def test_patrulla_comienza_mirando_hacia_su_ruta(self):
        from src.personajes import Guardia
        guardia = Guardia(self.nivel, [(100, 100), (50, 100)])
        self.assertAlmostEqual(abs(guardia.angulo), math.pi)
        with self.assertRaises(ValueError):
            Guardia(self.nivel, [(100, 100)])

    def test_poligono_de_alerta_no_atraviesa_muros(self):
        puntos = poligono_vision((100, 100), 0, 42, math.tau, [(115, 50, 10, 100)])
        self.assertTrue(all(x <= 115.001 for x, _ in puntos))


if __name__ == "__main__":
    unittest.main(verbosity=2)
