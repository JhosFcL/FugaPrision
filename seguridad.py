"""Objetos interactivos y de seguridad del escenario."""

DURACION_PANEL = 6.0


class Camara:
    def __init__(self, zona):
        self.__zona = zona.copy()
        self.__activa = True

    def detectar(self, rect):
        return self.__activa and self.__zona.colliderect(rect)

    def activar(self):
        self.__activa = True

    def desactivar(self):
        self.__activa = False

    def get_zona(self):
        return self.__zona.copy()


class Llave:
    def __init__(self, rect):
        self.__rect = rect.copy()
        self.__recogida = False

    def get_rect(self):
        return self.__rect.copy()

    def recoger(self):
        if self.__recogida:
            return False
        self.__recogida = True
        return True

    def esta_recogida(self):
        return self.__recogida


class Puerta:
    def __init__(self, rect):
        self.__rect = rect.copy()
        self.__abierta = False

    def get_rect(self):
        return self.__rect.copy()

    def abrir(self):
        self.__abierta = True

    def esta_abierta(self):
        return self.__abierta


class PanelSeguridad:
    """Agrega referencias a cámaras del nivel para apagarlas temporalmente."""

    def __init__(self, rect, camaras):
        self.__rect = rect.copy()
        self.__utilizado = False
        self.__tiempo_restante = 0.0
        self.__camaras = list(camaras)

    def get_rect(self):
        return self.__rect.copy()

    def activar(self):
        if self.__utilizado:
            return False
        self.__utilizado = True
        self.__tiempo_restante = DURACION_PANEL
        for camara in self.__camaras:
            camara.desactivar()
        return True

    def update(self, dt):
        if dt <= 0 or self.__tiempo_restante <= 0:
            return
        self.__tiempo_restante = max(0.0, self.__tiempo_restante - dt)
        if self.__tiempo_restante == 0.0:
            for camara in self.__camaras:
                camara.activar()

    def esta_activo(self):
        return self.__tiempo_restante > 0
