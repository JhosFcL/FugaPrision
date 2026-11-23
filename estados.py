"""Patrón State para gestionar el flujo de la partida."""
from abc import ABC, abstractmethod

import pygame


class EstadoJuego(ABC):
    def __init__(self, juego):
        self._juego = juego

    @abstractmethod
    def manejar_evento(self, evento):
        ...

    @abstractmethod
    def update(self, dt):
        ...


class Jugando(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_p, pygame.K_ESCAPE):
            self._juego.cambiar_estado(Pausa(self._juego))

    def update(self, dt):
        pulsadas = pygame.key.get_pressed()
        dx = int(pulsadas[pygame.K_d] or pulsadas[pygame.K_RIGHT]) - int(
            pulsadas[pygame.K_a] or pulsadas[pygame.K_LEFT]
        )
        dy = int(pulsadas[pygame.K_s] or pulsadas[pygame.K_DOWN]) - int(
            pulsadas[pygame.K_w] or pulsadas[pygame.K_UP]
        )
        self._juego.get_nivel().get_prisionero().set_direccion(dx, dy)
        self._juego.actualizar_nivel(dt)


class Pausa(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_p, pygame.K_ESCAPE):
            self._juego.cambiar_estado(Jugando(self._juego))

    def update(self, dt):
        pass


class Derrota(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            self._juego.reiniciar_nivel()

    def update(self, dt):
        pass


class Victoria(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            self._juego.reiniciar_partida()

    def update(self, dt):
        pass
