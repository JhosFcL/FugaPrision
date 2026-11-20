"""Comportamiento de las colisiones de la versión sencilla."""
import unittest

from pygame import Rect

from mapa import Mapa
from sistema_colisiones import SistemaColisiones


class PruebasSistemaColisiones(unittest.TestCase):
    def setUp(self):
        self.mapa = Mapa([
            "########",
            "#......#",
            "#..##..#",
            "#......#",
            "########",
        ])
        self.colisiones = SistemaColisiones(self.mapa)

    def test_movimiento_libre_conserva_el_rectangulo_original(self):
        original = Rect(50, 50, 20, 20)
        self.assertTrue(self.colisiones.puede_mover(original, 10, 5))
        resultado = self.colisiones.mover(original, 10, 5)
        self.assertEqual(resultado, Rect(60, 55, 20, 20))
        self.assertEqual(original, Rect(50, 50, 20, 20))
        self.assertIsNot(resultado, original)

    def test_desplazamiento_grande_se_detiene_en_la_pared_mas_cercana(self):
        casos = [
            (Rect(50, 90, 20, 20), 1000, 0, Rect(100, 90, 20, 20)),
            (Rect(220, 90, 20, 20), -1000, 0, Rect(200, 90, 20, 20)),
            (Rect(130, 50, 20, 20), 0, 1000, Rect(130, 60, 20, 20)),
            (Rect(130, 130, 20, 20), 0, -1000, Rect(130, 120, 20, 20)),
        ]
        for original, dx, dy, esperado in casos:
            with self.subTest(original=original, dx=dx, dy=dy):
                resultado = self.colisiones.mover(original, dx, dy)
                self.assertEqual(resultado, esperado)
                self.assertFalse(self.colisiones.puede_mover(original, dx, dy))
                self.assertEqual(resultado.collidelist(self.mapa.get_muros()), -1)

    def test_rechaza_cruzar_una_pared_aunque_el_destino_este_libre(self):
        original = Rect(50, 90, 20, 20)
        self.assertEqual(original.move(200, 0).collidelist(self.mapa.get_muros()), -1)
        self.assertFalse(self.colisiones.puede_mover(original, 200, 0))

    def test_movimiento_diagonal_permite_deslizarse_junto_a_la_pared(self):
        self.assertEqual(
            self.colisiones.mover(Rect(90, 90, 20, 20), 100, 40),
            Rect(100, 130, 20, 20),
        )
        self.assertEqual(
            self.colisiones.mover(Rect(90, 50, 20, 20), 40, 70),
            Rect(130, 60, 20, 20),
        )

    def test_respeta_los_limites_incluso_en_un_plano_sin_perimetro(self):
        colisiones = SistemaColisiones(Mapa(["....", "....", "...."]))
        self.assertEqual(colisiones.mover(Rect(50, 50, 20, 20), -500, -500),
                         Rect(0, 0, 20, 20))
        self.assertEqual(colisiones.mover(Rect(50, 50, 20, 20), 500, 500),
                         Rect(140, 100, 20, 20))

    def test_bordes_adyacentes_no_cuentan_como_superposicion(self):
        a = Rect(50, 50, 20, 20)
        self.assertFalse(self.colisiones.toca(a, Rect(70, 50, 20, 20)))
        self.assertTrue(self.colisiones.toca(a, Rect(69, 50, 20, 20)))

    def test_desplazamientos_se_aplican_en_pixeles_enteros(self):
        original = Rect(50, 50, 20, 20)
        self.assertEqual(self.colisiones.mover(original, 3.9, -2.9),
                         Rect(53, 48, 20, 20))
