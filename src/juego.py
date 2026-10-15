import math
from .puntuacion import Puntaje, PanelPuntaje
from .nivel import Nivel
from .estados import Jugando


class Juego:
    def __init__(self):
        self.puntaje = Puntaje()
        self.panel = PanelPuntaje()
        self.puntaje.suscribir(self.panel)
        self.iniciar_partida()

    def iniciar_partida(self):
        self.puntaje.reiniciar()
        self.indice_nivel = 0
        self.puntos_inicio_nivel = 0
        self._cargar_nivel()

    def _cargar_nivel(self):
        self.nivel = Nivel(self.puntaje, self.indice_nivel)
        self.estado = Jugando(self)

    def siguiente_nivel(self):
        if self.nivel.terminado and self.indice_nivel < self.nivel.total_niveles - 1:
            self.indice_nivel += 1
            self.puntos_inicio_nivel = self.puntaje.get_valor()
            self._cargar_nivel()

    def reintentar_nivel(self):
        self.puntaje.set_valor(self.puntos_inicio_nivel)
        self._cargar_nivel()

    def cambiar_estado(self, estado):
        self.estado = estado

    def manejar_entrada(self, tecla):
        self.estado.manejar_entrada(tecla)

    def actualizar(self, dt, teclas):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("El tiempo debe ser finito y no negativo.")
        # Una demora de la ventana no debe provocar saltos en la simulación.
        self.estado.actualizar(min(dt, 0.05), teclas)
