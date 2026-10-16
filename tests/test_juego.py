import math
import unittest
from unittest.mock import patch
from src.juego import Juego
from src.estados import Jugando, Pausa, Derrota, Victoria, NivelCompletado
from src.personajes import Personaje, HabilidadCarrera
from src.puntuacion import Puntaje, ObservadorPuntaje
from src.geometria import dentro_de_vision
from src.mapa import centro, TAMANO


def ubicar(personaje, posicion):
    """Preparación de escenarios de prueba; no se expone como control del juego."""
    personaje._x = posicion[0]
    personaje._y = posicion[1]


def recorrer_ruta(juego):
    from tests.recorridos import recorrer
    return recorrer(juego)


class RegistroPuntaje(ObservadorPuntaje):
    def __init__(self):
        self.valores = []

    def actualizar_puntaje(self, valor):
        self.valores.append(valor)


class PruebasJuego(unittest.TestCase):
    def setUp(self):
        self.juego = Juego()

    def test_personaje_es_abstracto(self):
        with self.assertRaises(TypeError):
            Personaje(None, 0, 0, 1)

    def test_colision_con_cuatro_bordes(self):
        for desplazamiento in [(2000, 0), (-2000, 0), (0, 2000), (0, -2000)]:
            jugador = Juego().nivel.prisionero
            jugador.mover(*desplazamiento)
            self.assertTrue(jugador.nivel.posicion_valida(*jugador.get_posicion(), jugador.radio))
            x, y = jugador.get_posicion()
            self.assertGreaterEqual(x, 46)
            self.assertLessEqual(x, 818)
            self.assertGreaterEqual(y, 46)
            self.assertLessEqual(y, 458)

    def test_colision_muro_interior_sin_atravesarlo(self):
        jugador = self.juego.nivel.prisionero
        jugador.mover(1000, 0)
        self.assertEqual(jugador.get_posicion()[0], 6 * TAMANO - jugador.radio)

    def test_velocidad_diagonal_normalizada(self):
        distancias = []
        for teclas in [{"derecha"}, {"derecha", "arriba"}]:
            juego = Juego()
            inicio = juego.nivel.prisionero.get_posicion()
            juego.actualizar(0.05, teclas)
            final = juego.nivel.prisionero.get_posicion()
            distancias.append(math.dist(inicio, final))
        self.assertAlmostEqual(distancias[0], distancias[1], places=6)

    def test_cono_y_muro_bloquean_vision(self):
        argumentos = ((0, 0), (100, 0), 0, 150, math.pi / 2)
        self.assertTrue(dentro_de_vision(*argumentos, []))
        self.assertFalse(dentro_de_vision(*argumentos, [(40, -20, 10, 40)]))
        self.assertFalse(dentro_de_vision((0, 0), (-30, 0), 0, 150, math.pi / 2, []))
        self.assertFalse(dentro_de_vision((0, 0), (200, 0), 0, 150, math.pi / 2, []))

    def test_camara_detecta(self):
        nivel = self.juego.nivel
        camara = nivel.camaras[0]
        x, y = camara.posicion
        ubicar(nivel.prisionero, (x, y + 40))
        self.juego.actualizar(0, set())
        self.assertTrue(camara.activa)
        self.assertTrue(all(g.modo == "PERSIGUE" for g in nivel.guardias))
        self.assertIsInstance(self.juego.estado, Jugando)
        ubicar(nivel.prisionero, (x, y - 40))
        self.juego.actualizar(0, set())
        self.assertFalse(camara.activa)

    def test_atajo_superior_bloqueado(self):
        prisionero = self.juego.nivel.prisionero
        ubicar(prisionero, centro(8, 1))
        prisionero.mover(400, 0)
        self.assertLess(prisionero.get_posicion()[0], 12 * TAMANO)

    def test_guardia_detecta_y_patrulla(self):
        nivel = self.juego.nivel
        posicion = nivel.guardias[0].get_posicion()
        self.juego.actualizar(0.05, set())
        self.assertNotEqual(posicion, nivel.guardias[0].get_posicion())
        guardia = nivel.guardias[0]
        ubicar(guardia, centro(2, 10))
        guardia.angulo = math.pi / 2
        self.juego.actualizar(0, set())
        self.assertEqual(guardia.modo, "PERSIGUE")
        self.assertIsInstance(self.juego.estado, Jugando)

    def test_contacto_por_detras_captura(self):
        nivel = self.juego.nivel
        x, y = nivel.guardias[0].get_posicion()
        ubicar(nivel.prisionero, (x - 15, y))
        self.juego.actualizar(0, set())
        self.assertIsInstance(self.juego.estado, Derrota)

    def test_llave_puntua_una_vez(self):
        ubicar(self.juego.nivel.prisionero, self.juego.nivel.llave.posicion)
        for _ in range(5):
            self.juego.actualizar(0, set())
        self.assertEqual(self.juego.panel.valor, 100)
        self.assertFalse(self.juego.nivel.llave.disponible)

    def test_salida_exige_llave_y_no_duplica_premio(self):
        nivel = self.juego.nivel
        ubicar(nivel.prisionero, nivel.salida.posicion)
        self.juego.actualizar(0, set())
        self.assertIsInstance(self.juego.estado, Jugando)
        ubicar(nivel.prisionero, nivel.llave.posicion)
        self.juego.actualizar(0, set())
        ubicar(nivel.prisionero, nivel.salida.posicion)
        for _ in range(3):
            self.juego.actualizar(0, set())
        self.assertIsInstance(self.juego.estado, NivelCompletado)
        self.assertEqual(self.juego.panel.valor, 600)

    def test_derrota_tiene_prioridad(self):
        nivel = self.juego.nivel
        nivel.prisionero.recoger_llave()
        ubicar(nivel.prisionero, nivel.salida.posicion)
        ubicar(nivel.guardias[0], nivel.salida.posicion)
        self.juego.actualizar(0, set())
        self.assertIsInstance(self.juego.estado, Derrota)
        self.assertEqual(self.juego.panel.valor, 0)

    def test_pausa_congela_todo_y_reanuda(self):
        self.juego.manejar_entrada("carrera")
        self.juego.manejar_entrada("pausa")
        nivel = self.juego.nivel
        antes = (nivel.prisionero.get_posicion(), nivel.guardias[0].get_posicion(), nivel.tiempo,
                 nivel.prisionero.carrera.get_estado())
        for _ in range(120):
            self.juego.actualizar(0.05, {"arriba"})
        despues = (nivel.prisionero.get_posicion(), nivel.guardias[0].get_posicion(), nivel.tiempo,
                   nivel.prisionero.carrera.get_estado())
        self.assertEqual(antes, despues)
        self.assertIsInstance(self.juego.estado, Pausa)
        self.juego.manejar_entrada("pausa")
        self.juego.actualizar(0.05, {"arriba"})
        self.assertNotEqual(antes[0], nivel.prisionero.get_posicion())

    def test_reinicio_restaura_nivel_puntaje_y_habilidad(self):
        nivel_anterior = self.juego.nivel
        self.juego.puntaje.sumar(100)
        self.juego.manejar_entrada("carrera")
        self.juego.cambiar_estado(Derrota(self.juego))
        self.juego.manejar_entrada("reiniciar")
        self.assertIsNot(nivel_anterior, self.juego.nivel)
        self.assertEqual(self.juego.panel.valor, 0)
        self.assertTrue(self.juego.nivel.llave.disponible)
        self.assertFalse(self.juego.nivel.prisionero.tiene_llave())
        self.assertIn("LISTA", self.juego.nivel.prisionero.carrera.get_estado())
        self.assertEqual(self.juego.nivel.prisionero.get_posicion(), centro(2, 11))

    def test_observer_suscripcion_unica_y_retiro(self):
        puntaje = Puntaje()
        registro = RegistroPuntaje()
        puntaje.suscribir(registro)
        puntaje.suscribir(registro)
        puntaje.sumar(100)
        puntaje.reiniciar()
        self.assertEqual(registro.valores, [0, 100, 0])
        puntaje.desuscribir(registro)
        puntaje.sumar(500)
        self.assertEqual(registro.valores, [0, 100, 0])

    def test_puntaje_rechaza_valores_invalidos(self):
        for valor in [-1, 0, 0.5, True, "100"]:
            with self.assertRaises(ValueError):
                self.juego.puntaje.sumar(valor)

    def test_setter_puntaje_valida_y_notifica(self):
        for valor in [-1, 1.5, True, "100"]:
            with self.assertRaises(ValueError):
                self.juego.puntaje.set_valor(valor)
        self.assertEqual(self.juego.puntaje.get_valor(), 0)
        self.juego.puntaje.set_valor(250)
        self.assertEqual(self.juego.puntaje.get_valor(), 250)
        self.assertEqual(self.juego.panel.valor, 250)

    def test_actualizacion_polimorfica(self):
        nivel = self.juego.nivel
        with patch.object(nivel.prisionero, "update", wraps=nivel.prisionero.update) as principal:
            with patch.object(nivel.guardias[0], "update", wraps=nivel.guardias[0].update) as secundario:
                self.juego.actualizar(0.01, set())
                principal.assert_called_once_with()
                secundario.assert_called_once_with()

    def test_habilidad_duracion_recarga_y_activacion(self):
        habilidad = HabilidadCarrera()
        self.assertTrue(habilidad.activar())
        self.assertFalse(habilidad.activar())
        self.assertEqual(habilidad.get_multiplicador(), 1.5)
        habilidad.actualizar(2)
        self.assertEqual(habilidad.get_multiplicador(), 1)
        self.assertFalse(habilidad.activar())
        habilidad.actualizar(5)
        self.assertTrue(habilidad.activar())

    def test_habilidad_aumenta_velocidad_sin_cruzar_muros(self):
        normal = Juego()
        rapido = Juego()
        rapido.manejar_entrada("carrera")
        inicio = normal.nivel.prisionero.get_posicion()
        normal.actualizar(0.05, {"derecha"})
        rapido.actualizar(0.05, {"derecha"})
        distancia_normal = math.dist(inicio, normal.nivel.prisionero.get_posicion())
        distancia_rapida = math.dist(inicio, rapido.nivel.prisionero.get_posicion())
        self.assertAlmostEqual(distancia_rapida, distancia_normal * 1.5)
        for _ in range(150):
            rapido.actualizar(0.05, {"abajo"})
        self.assertLessEqual(rapido.nivel.prisionero.get_posicion()[1], 458)

    def test_tiempo_invalido_y_demoras(self):
        for dt in [-1, float("inf"), float("nan")]:
            with self.assertRaises(ValueError):
                self.juego.actualizar(dt, set())
        self.juego.actualizar(10, set())
        self.assertEqual(self.juego.nivel.tiempo, 0.05)

    def test_ruta_completa_sin_teletransportes(self):
        fotogramas = recorrer_ruta(self.juego)
        self.assertGreater(fotogramas, 100)
        self.assertIsInstance(self.juego.estado, NivelCompletado)
        self.assertEqual(self.juego.panel.valor, 600)


if __name__ == "__main__":
    unittest.main(verbosity=2)
