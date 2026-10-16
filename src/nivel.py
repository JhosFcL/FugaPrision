import math
from .geometria import distancia, dentro_de_vision
from .personajes import Prisionero, Guardia
from .combate import Combate
from .mapa import Mapa, PLANOS, TAMANO, centro
from .ruido import SistemaRuido

# Cada pabellón tiene su propia distribución y vigilancia.
ETAPAS = (
    {"nombre": "Pabellón de celdas", "inicio": (2, 11), "llave": (8, 2),
     "salida": (21, 2), "rutas": [((9, 7), (10, 2)), ((15, 10), (16, 3))],
     "camaras": [((10, 1), math.pi / 2)]},
    {"nombre": "Lavandería", "inicio": (2, 11), "llave": (21, 11),
     "salida": (21, 2), "rutas": [((8, 3), (10, 10)), ((15, 10), (16, 5))],
     "camaras": [((4, 1), math.pi / 2), ((22, 6), math.pi)]},
    {"nombre": "Patio de vigilancia", "inicio": (2, 11), "llave": (3, 2),
     "salida": (21, 11),
     "atajos": [(4, 4), (5, 4), (20, 9), (21, 9)],
     "rutas": [((7, 7), (17, 7)), ((12, 2), (21, 2)), ((8, 10), (16, 10))],
     "camaras": [((1, 2), 0), ((20, 5), math.pi / 2), ((22, 12), math.pi)]},
    {"nombre": "El Alcaide", "inicio": (12, 11), "llave": (12, 3),
     "salida": (12, 1), "rutas": [], "camaras": []},
)


def posicion_camara(casilla, angulo):
    x, y = centro(*casilla)
    separacion = TAMANO / 2 - 4
    return x - math.cos(angulo) * separacion, y - math.sin(angulo) * separacion


class PuertaCelda:
    def __init__(self, posicion):
        self.posicion = posicion
        self.progreso = 0.0
        self.abierta = False

    def actualizar(self, dt, prisionero, interactuar):
        if self.abierta:
            return False
        if not interactuar or distancia(self.posicion, prisionero.get_posicion()) > 48:
            self.progreso = 0.0
            return False
        self.progreso = min(2.0, self.progreso + dt)
        if self.progreso >= 2.0:
            self.abierta = True
            return True
        return False


class Camara:
    def __init__(self, posicion, angulo=math.pi / 2):
        self.posicion = posicion
        self.angulo = angulo
        self.alcance = 95
        self.apertura = math.radians(60)
        self.activa = False

    def detectar(self, prisionero, muros):
        return dentro_de_vision(self.posicion, prisionero.get_posicion(),
                               self.angulo, self.alcance, self.apertura, muros, prisionero.radio)


class Llave:
    def __init__(self, posicion):
        self.posicion = posicion
        self.disponible = True

    def recoger(self, prisionero):
        if self.disponible and distancia(self.posicion, prisionero.get_posicion()) < 22:
            self.disponible = False
            prisionero.recoger_llave()
            return True
        return False


class PuertaSalida:
    def __init__(self, posicion):
        self.posicion = posicion

    def puede_salir(self, prisionero):
        return prisionero.tiene_llave() and distancia(self.posicion, prisionero.get_posicion()) < 22


class Nivel:
    total_niveles = len(ETAPAS)

    @property
    def configuracion_siguiente(self):
        return ETAPAS[min(self.indice + 1, self.total_niveles - 1)]["nombre"]

    def __init__(self, puntaje, indice=0):
        if not 0 <= indice < self.total_niveles:
            raise ValueError("Nivel inexistente.")
        self.indice = indice
        self.configuracion = ETAPAS[indice]
        self.nombre = self.configuracion["nombre"]
        self.es_final = indice == self.total_niveles - 1
        self.puntaje = puntaje
        self.dt = 0.0
        self.tiempo = 0.0
        self.teclas = set()
        self.terminado = False
        self.mapa = Mapa(PLANOS[indice])
        self.celda = PuertaCelda(centro(4, 11)) if indice == 0 else None
        self.ruidos = SistemaRuido(self.mapa)
        self.prisionero = Prisionero(self, *centro(*self.configuracion["inicio"]))
        self.guardias = [Guardia(self, [centro(*p) for p in ruta])
                         for ruta in self.configuracion["rutas"]]
        self.personajes = [self.prisionero, *self.guardias]
        for guardia in self.guardias:
            self.ruidos.registrar(guardia)
        self.camaras = [Camara(posicion_camara(posicion, angulo), angulo)
                        for posicion, angulo in self.configuracion["camaras"]]
        self.llave = Llave(centro(*self.configuracion["llave"]))
        self.salida = PuertaSalida(centro(*self.configuracion["salida"]))
        self.combate = Combate(self) if self.es_final else None
        if self.es_final:
            self.llave.disponible = False

    def posicion_valida(self, x, y, radio):
        return self.mapa.posicion_valida(x, y, radio)

    def actualizar(self, dt, teclas):
        if self.terminado:
            return None
        self.dt = dt
        self.teclas = set(teclas)
        self.tiempo += dt
        if self.celda and self.celda.actualizar(dt, self.prisionero, "interactuar" in self.teclas):
            self.mapa.abrir_puerta(self.celda.posicion)
            self.ruidos.emitir(self.celda.posicion, 260)
        for personaje in self.personajes:
            personaje.update()
        self._actualizar_camaras()
        if self.combate:
            self.combate.actualizar(dt, self.teclas)
        return self.resolver_interacciones()

    def resolver_interacciones(self):
        if self.terminado:
            return None
        capturado = any(g.puede_capturar(self.prisionero) for g in self.guardias)
        # Ver u oír provoca una respuesta; solamente el contacto causa la captura.
        if capturado or (self.combate and self.combate.vida <= 0):
            self.terminado = True
            return "derrota"
        if self.combate and self.combate.jefe.derrotado and not self.combate.premiado:
            self.combate.premiado = True
            self.puntaje.sumar(1000)
            self.llave.disponible = True
        if self.llave.recoger(self.prisionero):
            self.puntaje.sumar(100)
            for casilla in self.configuracion.get("atajos", []):
                self.mapa.abrir_puerta(centro(*casilla))
        if self.salida.puede_salir(self.prisionero) and (not self.combate or self.combate.jefe.derrotado):
            self.terminado = True
            self.puntaje.sumar(500)
            return "victoria" if self.es_final else "nivel_completado"
        return None

    def _actualizar_camaras(self):
        for camara in self.camaras:
            camara.activa = camara.detectar(self.prisionero, self.mapa.muros)
            if camara.activa:
                for guardia in self.guardias:
                    guardia.alertar(self.prisionero.get_posicion())
