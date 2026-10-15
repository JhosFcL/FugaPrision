from abc import ABC, abstractmethod


class EstadoJuego(ABC):
    nombre = ""

    def __init__(self, juego):
        self.juego = juego

    @abstractmethod
    def manejar_entrada(self, tecla):
        pass

    @abstractmethod
    def actualizar(self, dt, teclas):
        pass


class Jugando(EstadoJuego):
    nombre = "JUGANDO"

    def manejar_entrada(self, tecla):
        if tecla == "pausa":
            self.juego.cambiar_estado(Pausa(self.juego))
        elif tecla == "carrera":
            self.juego.nivel.prisionero.carrera.activar()

    def actualizar(self, dt, teclas):
        resultado = self.juego.nivel.actualizar(dt, teclas)
        if resultado == "derrota":
            self.juego.cambiar_estado(Derrota(self.juego))
        elif resultado == "victoria":
            self.juego.cambiar_estado(Victoria(self.juego))
        elif resultado == "nivel_completado":
            self.juego.cambiar_estado(NivelCompletado(self.juego))


class Pausa(EstadoJuego):
    nombre = "PAUSA"

    def manejar_entrada(self, tecla):
        if tecla == "pausa":
            self.juego.cambiar_estado(Jugando(self.juego))

    def actualizar(self, dt, teclas):
        pass


class Derrota(EstadoJuego):
    nombre = "DERROTA"

    def manejar_entrada(self, tecla):
        if tecla == "reiniciar":
            self.juego.reintentar_nivel()
        elif tecla == "nueva_partida":
            self.juego.iniciar_partida()

    def actualizar(self, dt, teclas):
        pass


class Victoria(EstadoJuego):
    nombre = "VICTORIA"

    def manejar_entrada(self, tecla):
        if tecla == "reiniciar":
            self.juego.iniciar_partida()

    def actualizar(self, dt, teclas):
        pass


class NivelCompletado(EstadoJuego):
    nombre = "NIVEL_COMPLETADO"

    def manejar_entrada(self, tecla):
        if tecla == "continuar":
            self.juego.siguiente_nivel()
        elif tecla == "nueva_partida":
            self.juego.iniciar_partida()

    def actualizar(self, dt, teclas):
        pass
