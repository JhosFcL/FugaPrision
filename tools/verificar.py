"""Pruebas y capturas reales del renderizador en modo SDL sin ventana."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import io
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import pygame
from src.juego import Juego
from src.estados import Pausa, Jugando, Victoria, Derrota, NivelCompletado
from src.vista import Vista, ANCHO, ALTO
from tests.test_juego import recorrer_ruta, ubicar
from tests.test_campana import caminar, vencer_alcaide, escapar_arena
from main import procesar_eventos


def ejecutar():
    evidencias = RAIZ / "docs" / "evidencias"
    evidencias.mkdir(parents=True, exist_ok=True)
    salida = io.StringIO()
    pruebas = unittest.defaultTestLoader.discover(str(RAIZ / "tests"), top_level_dir=str(RAIZ))
    resultado = unittest.TextTestRunner(stream=salida, verbosity=2).run(pruebas)
    (evidencias / "pruebas.txt").write_text(salida.getvalue(), encoding="utf-8")
    print(salida.getvalue())
    if not resultado.wasSuccessful():
        raise SystemExit(1)
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    vista = Vista(pantalla)
    juego = Juego()

    def captura(nombre):
        vista.dibujar(juego)
        pygame.display.flip()
        pygame.image.save(pantalla, str(evidencias / nombre))

    captura("01_inicio.png")
    procesar_eventos(juego, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)])
    assert isinstance(juego.estado, Pausa)
    captura("02_pausa.png")
    procesar_eventos(juego, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
    assert isinstance(juego.estado, Jugando)
    procesar_eventos(juego, [pygame.event.Event(pygame.WINDOWFOCUSLOST)])
    assert isinstance(juego.estado, Pausa)
    procesar_eventos(juego, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)])
    fotogramas = recorrer_ruta(juego)
    assert isinstance(juego.estado, NivelCompletado)
    captura("09_nivel_completado.png")
    procesar_eventos(juego, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
    assert juego.indice_nivel == 1 and juego.panel.valor == 600
    captura("05_lavanderia.png")
    caminar(juego, [(2, 1), (22, 1), (22, 11), (21, 11), (22, 11), (22, 2), (21, 2)])
    procesar_eventos(juego, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
    assert juego.indice_nivel == 2 and juego.panel.valor == 1200
    captura("06_patio.png")
    caminar(juego, [(2, 2), (3, 2), (2, 2), (2, 1), (22, 1), (22, 11), (21, 11)])
    procesar_eventos(juego, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
    assert juego.indice_nivel == 3 and juego.panel.valor == 1800
    captura("07_jefe.png")
    capturadas = set()

    def observar(partida):
        combate = partida.nivel.combate
        if combate.jefe.aviso > 0 and "aviso" not in capturadas:
            captura("08_jefe_aviso.png")
            capturadas.add("aviso")
        lagrimas = [p for p in combate.proyectiles if p.enemigo and
                    ((p.x - combate.jefe.x) ** 2 + (p.y - combate.jefe.y) ** 2) > 45 ** 2]
        if combate.jefe.fase == 2 and len(lagrimas) > 10 and "fase2" not in capturadas:
            captura("10_jefe_fase2.png")
            capturadas.add("fase2")

    combate_frames = vencer_alcaide(juego, observar)
    assert juego.nivel.combate.jefe.derrotado and juego.nivel.combate.vida > 0
    escapar_arena(juego)
    assert isinstance(juego.estado, Victoria) and juego.panel.valor == 3400
    captura("03_victoria.png")
    procesar_eventos(juego, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)])
    assert isinstance(juego.estado, Jugando) and juego.panel.valor == 0 and juego.indice_nivel == 0
    gx, gy = juego.nivel.guardias[0].get_posicion()
    ubicar(juego.nivel.prisionero, (gx, gy + 35))
    juego.actualizar(0, set())
    assert isinstance(juego.estado, Derrota)
    captura("04_derrota.png")
    assert not procesar_eventos(juego, [pygame.event.Event(pygame.QUIT)])
    pygame.quit()
    assert capturadas == {"aviso", "fase2"}
    print(f"{resultado.testsRun} pruebas sin fallos; campaña completa de 4 niveles, "
          f"ruta inicial de {fotogramas} fotogramas y jefe vencido en {combate_frames / 60:.2f} s; 10 capturas generadas.")


if __name__ == "__main__":
    ejecutar()
