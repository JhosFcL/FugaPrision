"""Ejecutar desde la carpeta del proyecto: python main.py."""
import os
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
from src.juego import Juego
from src.estados import Jugando
from src.vista import Vista, ANCHO, ALTO


def procesar_eventos(juego, eventos):
    for evento in eventos:
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.WINDOWFOCUSLOST and isinstance(juego.estado, Jugando):
            juego.manejar_entrada("pausa")
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_p, pygame.K_ESCAPE):
                juego.manejar_entrada("pausa")
            elif evento.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                juego.manejar_entrada("carrera")
            elif evento.key == pygame.K_r:
                juego.manejar_entrada("reiniciar")
    return True


def ejecutar():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Fuga de la Prisión | POO 2026-2")
    reloj = pygame.time.Clock()
    juego = Juego()
    vista = Vista(pantalla)
    activo = True
    while activo:
        dt = reloj.tick(60) / 1000
        activo = procesar_eventos(juego, pygame.event.get())
        if not activo:
            break
        pulsadas = pygame.key.get_pressed()
        teclas = set()
        if pulsadas[pygame.K_w] or pulsadas[pygame.K_UP]:
            teclas.add("arriba")
        if pulsadas[pygame.K_s] or pulsadas[pygame.K_DOWN]:
            teclas.add("abajo")
        if pulsadas[pygame.K_a] or pulsadas[pygame.K_LEFT]:
            teclas.add("izquierda")
        if pulsadas[pygame.K_d] or pulsadas[pygame.K_RIGHT]:
            teclas.add("derecha")
        juego.actualizar(dt, teclas)
        vista.dibujar(juego)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    ejecutar()
