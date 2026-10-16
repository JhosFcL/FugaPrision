"""Los pasos emiten ruido y los guardias registrados lo escuchan."""


class SistemaRuido:
    def __init__(self, mapa):
        self.mapa = mapa
        self.oyentes = []

    def registrar(self, oyente):
        if oyente not in self.oyentes:
            self.oyentes.append(oyente)

    def emitir(self, posicion, alcance):
        if alcance <= 0:
            return
        for oyente in self.oyentes:
            recorrido = self.mapa.distancia_camino(posicion, oyente.get_posicion())
            if recorrido <= alcance:
                oyente.escuchar(posicion)
