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
from src.estados import Pausa, Jugando, Victoria, Derrota
from src.vista import Vista, ANCHO, ALTO
from tests.test_juego import recorrer_ruta, ubicar
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
    assert isinstance(juego.estado, Victoria)
    captura("03_victoria.png")
    tiempo = juego.nivel.tiempo
    procesar_eventos(juego, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)])
    assert isinstance(juego.estado, Jugando) and juego.panel.valor == 0
    ubicar(juego.nivel.prisionero, juego.nivel.guardia.get_posicion())
    juego.actualizar(0, set())
    assert isinstance(juego.estado, Derrota)
    captura("04_derrota.png")
    assert not procesar_eventos(juego, [pygame.event.Event(pygame.QUIT)])
    pygame.quit()
    print(f"{resultado.testsRun} pruebas sin fallos; ruta de {fotogramas} fotogramas en {tiempo:.3f} s; 4 capturas generadas.")


if __name__ == "__main__":
    ejecutar()
