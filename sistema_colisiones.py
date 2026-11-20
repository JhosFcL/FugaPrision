"""Controla el movimiento de rectángulos frente a las paredes del mapa."""


class SistemaColisiones:
    def __init__(self, mapa):
        self.__mapa = mapa

    def puede_mover(self, rect, dx, dy):
        destino = rect.move(int(dx), int(dy))
        return self.mover(rect, dx, dy) == destino

    def mover(self, rect, dx, dy):
        """Devuelve la posición permitida, avanzando primero en X y después en Y."""
        destino = rect.copy()
        muros = self.__mapa.get_muros()
        ancho, alto = self.__mapa.get_dimensiones()
        dx = int(dx)
        dy = int(dy)

        # Movimiento horizontal: detenerse en la primera pared del recorrido.
        dx = max(-destino.left, min(dx, ancho - destino.right))
        for muro in muros:
            if destino.bottom > muro.top and destino.top < muro.bottom:
                if dx > 0 and destino.right <= muro.left:
                    dx = min(dx, muro.left - destino.right)
                elif dx < 0 and destino.left >= muro.right:
                    dx = max(dx, muro.right - destino.left)
        destino.x += dx

        # Movimiento vertical: usar la posición horizontal ya corregida.
        dy = max(-destino.top, min(dy, alto - destino.bottom))
        for muro in muros:
            if destino.right > muro.left and destino.left < muro.right:
                if dy > 0 and destino.bottom <= muro.top:
                    dy = min(dy, muro.top - destino.bottom)
                elif dy < 0 and destino.top >= muro.bottom:
                    dy = max(dy, muro.bottom - destino.top)
        destino.y += dy

        return destino

    def toca(self, a, b):
        return a.colliderect(b)
