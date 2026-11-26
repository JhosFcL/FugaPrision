"""Punto de entrada del juego Fuga de la Prisión."""
import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from src.juego.juego import Juego
from src.juego.vista import ALTO, ANCHO, Vista


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Fuga de la Prisión")
    reloj = pygame.time.Clock()

    pista_actual = None
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.set_volume(0.20)
    except pygame.error:
        pass

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

        if not ejecutando or juego.quiere_salir():
            break

        juego.update(dt)

        config = juego.get_config_nivel() or {}
        pista_nivel = config.get("audio", "nivel_1_prision.wav")
        if pygame.mixer.get_init() and pista_nivel != pista_actual:
            archivo_musica = os.path.join(os.path.dirname(__file__), "audio", pista_nivel)
            pygame.mixer.music.load(archivo_musica)
            pygame.mixer.music.play(-1)
            pista_actual = pista_nivel

        juego.dibujar()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
