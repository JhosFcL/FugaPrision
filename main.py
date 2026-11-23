"""Punto de entrada del juego Fuga de la Prisión."""
import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from juego import Juego
from vista import ALTO, ANCHO, Vista


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Fuga de la Prisión")
    reloj = pygame.time.Clock()

    vista = Vista(pantalla)
    juego = Juego(vista)

    ejecutando = True
    while ejecutando:
        dt = min(reloj.tick(60) / 1000.0, 0.05)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
                break
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                continue
            juego.procesar_evento(evento)

        if not ejecutando:
            break

        juego.update(dt)
        juego.dibujar()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
