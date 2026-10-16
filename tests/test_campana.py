"""Regresiones de campaña y combate sin depender de la ventana."""
import math
import unittest
from collections import deque
from src.combate import Proyectil
from src.estados import Jugando, NivelCompletado, Derrota, Victoria
from src.juego import Juego
from src.nivel import Nivel
from src.mapa import centro, COLUMNAS, FILAS
from src.puntuacion import Puntaje
from tests.test_juego import ubicar


def llegar_a_arena():
    juego = Juego()
    for _ in range(3):
        nivel = juego.nivel
        ubicar(nivel.prisionero, nivel.llave.posicion)
        juego.actualizar(0, set())
        ubicar(nivel.prisionero, nivel.salida.posicion)
        juego.actualizar(0, set())
        assert isinstance(juego.estado, NivelCompletado)
        juego.manejar_entrada("continuar")
    return juego


def caminar(juego, casillas):
    for casilla in casillas:
        objetivo = centro(*casilla)
        for _ in range(1800):
            jugador = juego.nivel.prisionero
            dx = objetivo[0] - jugador.get_posicion()[0]
            dy = objetivo[1] - jugador.get_posicion()[1]
            if math.hypot(dx, dy) < 2 or isinstance(juego.estado, (NivelCompletado, Victoria)):
                break
            teclas = set()
            if abs(dx) > 1.3:
                teclas.add("derecha" if dx > 0 else "izquierda")
            if abs(dy) > 1.3:
                teclas.add("abajo" if dy > 0 else "arriba")
            juego.actualizar(1 / 120, teclas)
            if isinstance(juego.estado, Derrota):
                raise AssertionError("La ruta terminó en captura.")
        else:
            raise AssertionError(f"No se pudo alcanzar {casilla}.")


def vencer_alcaide(juego, observar=None):
    """Combate real: moverse por la arena y disparar, sin modificar al jefe."""
    ruta = [(700, 414), (700, 90), (164, 90), (164, 414)]
    objetivo = 0
    for fotograma in range(3600):
        x, y = juego.nivel.prisionero.get_posicion()
        tx, ty = ruta[objetivo]
        if math.hypot(tx - x, ty - y) < 6:
            objetivo = (objetivo + 1) % len(ruta)
            tx, ty = ruta[objetivo]
        teclas = {"disparar"}
        if abs(tx - x) > 2:
            teclas.add("derecha" if tx > x else "izquierda")
        if abs(ty - y) > 2:
            teclas.add("abajo" if ty > y else "arriba")
        juego.actualizar(1 / 60, teclas)
        if observar:
            observar(juego)
        if isinstance(juego.estado, Derrota):
            raise AssertionError("La ruta de combate terminó en derrota.")
        if juego.nivel.combate.jefe.derrotado:
            return fotograma + 1
    raise AssertionError("No se pudo vencer al Alcaide en 60 segundos.")


def escapar_arena(juego):
    """Camina por casillas transitables hasta la llave y la salida."""
    nivel = juego.nivel
    for destino in (nivel.configuracion["llave"], nivel.configuracion["salida"]):
        x, y = nivel.prisionero.get_posicion()
        inicio = int(x // 36), int(y // 36)
        pendientes = deque([inicio])
        anteriores = {inicio: None}
        while pendientes:
            casilla = pendientes.popleft()
            if casilla == destino:
                break
            cx, cy = casilla
            for vecina in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if vecina not in anteriores and nivel.posicion_valida(*centro(*vecina), 10):
                    anteriores[vecina] = casilla
                    pendientes.append(vecina)
        ruta = []
        casilla = destino
        while casilla is not None:
            ruta.append(casilla)
            casilla = anteriores[casilla]
        caminar(juego, list(reversed(ruta)))


class PruebasCampana(unittest.TestCase):
    def test_mapas_conectados_y_entidades_en_suelo(self):
        mapas = []
        for indice in range(4):
            nivel = Nivel(Puntaje(), indice)
            mapas.append(set(nivel.mapa.muros))
            inicio = nivel.configuracion["inicio"]
            pendientes = deque([inicio])
            visitadas = {inicio}
            while pendientes:
                x, y = pendientes.popleft()
                for vecino in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if vecino in visitadas or not (0 <= vecino[0] < COLUMNAS and 0 <= vecino[1] < FILAS):
                        continue
                    if nivel.posicion_valida(*centro(*vecino), nivel.prisionero.radio):
                        visitadas.add(vecino)
                        pendientes.append(vecino)
            for clave in ("llave", "salida"):
                self.assertIn(nivel.configuracion[clave], visitadas)
            for guardia in nivel.guardias:
                self.assertTrue(nivel.posicion_valida(*guardia.get_posicion(), guardia.radio))
                for _ in range(800):
                    nivel.dt = 0.05
                    guardia.update()
                    self.assertTrue(nivel.posicion_valida(*guardia.get_posicion(), guardia.radio))
        self.assertEqual(len({frozenset(m) for m in mapas}), 4)

    def test_rutas_nuevas_sin_teletransporte_ni_desactivar_guardias(self):
        from tests.recorridos import recorrer
        for indice in (1, 2):
            juego = Juego()
            juego.indice_nivel = indice
            juego._cargar_nivel()
            recorrer(juego)
            self.assertIsInstance(juego.estado, NivelCompletado)
            self.assertEqual(juego.panel.valor, 600)

    def test_transicion_conserva_puntos_y_no_avanza_dos_veces(self):
        juego = llegar_a_arena()
        self.assertEqual(juego.indice_nivel, 3)
        self.assertEqual(juego.panel.valor, 1800)
        juego.manejar_entrada("continuar")
        self.assertEqual(juego.indice_nivel, 3)
        self.assertIsInstance(juego.estado, Jugando)
        self.assertFalse(juego.nivel.llave.disponible)

    def test_salida_bloqueada_hasta_matar_jefe(self):
        juego = llegar_a_arena()
        nivel = juego.nivel
        nivel.prisionero.recoger_llave()
        ubicar(nivel.prisionero, nivel.salida.posicion)
        juego.actualizar(0, set())
        self.assertIsInstance(juego.estado, Jugando)

    def test_disparos_reales_derrotan_jefe_y_desbloquean_victoria(self):
        juego = llegar_a_arena()
        nivel = juego.nivel
        fotogramas = vencer_alcaide(juego)
        self.assertGreater(fotogramas, 60)
        self.assertGreater(nivel.combate.vida, 0)
        self.assertTrue(nivel.combate.jefe.derrotado)
        self.assertTrue(nivel.llave.disponible)
        self.assertEqual(juego.panel.valor, 2800)
        juego.actualizar(0, set())
        self.assertEqual(juego.panel.valor, 2800)
        escapar_arena(juego)
        self.assertIsInstance(juego.estado, Victoria)
        self.assertEqual(juego.panel.valor, 3400)
        juego.manejar_entrada("reiniciar")
        self.assertEqual(juego.indice_nivel, 0)
        self.assertEqual(juego.panel.valor, 0)

    def test_patrones_fase_dos_y_aviso_antes_de_atacar(self):
        nivel = llegar_a_arena().nivel
        combate = nivel.combate
        jefe = combate.jefe
        jefe.espera = 0
        jefe.actualizar(combate, 0.01)
        self.assertGreater(jefe.aviso, 0)
        self.assertEqual(combate.proyectiles, [])
        jefe.actualizar(combate, 1)
        self.assertEqual(len(combate.proyectiles), 12)
        combate.proyectiles.clear()
        jefe.vida = 30
        self.assertEqual(jefe.fase, 2)
        jefe.patron = 0
        jefe._atacar(combate)
        self.assertEqual(len(combate.proyectiles), 18)
        combate.proyectiles.clear()
        jefe.patron = 1
        jefe._atacar(combate)
        self.assertEqual(len(combate.proyectiles), 7)
        jefe.patron = 2
        jefe.objetivo = (198, 414)
        jefe._atacar(combate)
        for _ in range(200):
            jefe.actualizar(combate, 0.01)
            self.assertTrue(nivel.posicion_valida(*jefe.posicion, jefe.radio))

    def test_dano_inmunidad_y_derrota(self):
        juego = llegar_a_arena()
        combate = juego.nivel.combate
        for _ in range(4):
            combate.recibir_dano()
        self.assertEqual(combate.vida, 4)
        for _ in range(4):
            combate.inmune = 0
            combate.recibir_dano()
        juego.actualizar(0, set())
        self.assertIsInstance(juego.estado, Derrota)
        juego.manejar_entrada("reiniciar")
        self.assertEqual(juego.indice_nivel, 3)
        self.assertEqual(juego.panel.valor, 1800)
        self.assertEqual(juego.nivel.combate.vida, 5)
        self.assertEqual(juego.nivel.combate.jefe.vida, 72)
        juego.cambiar_estado(Derrota(juego))
        juego.manejar_entrada("nueva_partida")
        self.assertEqual(juego.indice_nivel, 0)
        self.assertEqual(juego.panel.valor, 0)

    def test_proyectiles_rapidos_no_atraviesan_jugador_ni_muros(self):
        juego = llegar_a_arena()
        combate = juego.nivel.combate
        combate.proyectiles = [Proyectil(400, 414, 2000, 0)]
        juego.actualizar(0.05, set())
        self.assertEqual(combate.vida, 4)
        # La columna en (5, 8) bloquea el tiro antes de tocar al jugador.
        ubicar(juego.nivel.prisionero, (250, 306))
        combate.inmune = 0
        combate.proyectiles = [Proyectil(150, 306, 4000, 0)]
        juego.actualizar(0.05, set())
        self.assertEqual(combate.vida, 4)
        self.assertEqual(combate.proyectiles, [])

    def test_pausa_congela_jefe_disparos_vida_y_recargas(self):
        juego = llegar_a_arena()
        juego.actualizar(0.05, {"disparar"})
        combate = juego.nivel.combate
        antes = (combate.jefe.posicion, combate.jefe.espera, combate.recarga,
                 [(p.posicion, p.duracion) for p in combate.proyectiles], combate.vida)
        juego.manejar_entrada("pausa")
        for _ in range(120):
            juego.actualizar(0.05, {"disparar", "arriba"})
        despues = (combate.jefe.posicion, combate.jefe.espera, combate.recarga,
                   [(p.posicion, p.duracion) for p in combate.proyectiles], combate.vida)
        self.assertEqual(antes, despues)
