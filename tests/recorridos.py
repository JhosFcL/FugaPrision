import heapq
import math
from src.mapa import centro, TAMANO
from src.geometria import distancia, dentro_de_vision


def abrir_celda(juego):
    celda = juego.nivel.celda
    if not celda or celda.abierta:
        return
    for _ in range(30):
        if juego.nivel.prisionero.get_posicion()[0] >= 125:
            break
        juego.actualizar(.05, {"derecha"})
    for _ in range(41):
        juego.actualizar(.05, {"interactuar"})
    assert celda.abierta, "La puerta no se abrió manteniendo E junto a ella."


def acercarse_haciendo_ruido(juego):
    """Recorre la zona inicial corriendo hasta que una patrulla escucha los pasos."""
    for _ in range(20):
        juego.actualizar(.05, set())
    abrir_celda(juego)
    for punto in (centro(5, 11), centro(5, 7), centro(5, 6), centro(6, 6), centro(8, 6)):
        for _ in range(250):
            jugador = juego.nivel.prisionero
            dx, dy = punto[0] - jugador.get_posicion()[0], punto[1] - jugador.get_posicion()[1]
            if max(abs(dx), abs(dy)) < 1:
                break
            teclas = set()
            if abs(dx) > 1:
                teclas.add("derecha" if dx > 0 else "izquierda")
            elif abs(dy) > 1:
                teclas.add("abajo" if dy > 0 else "arriba")
            juego.manejar_entrada("carrera")
            dt = min(.05, max(abs(dx), abs(dy)) / (145 * jugador.carrera.get_multiplicador()))
            juego.actualizar(dt, teclas)
            if any(g.modo == "INVESTIGA" for g in juego.nivel.guardias):
                return
    raise AssertionError("La patrulla no escuchó el recorrido de pasos.")


def ruta_segura(nivel, destino):
    origen = nivel.prisionero.get_posicion()
    inicio = (int(origen[0] // TAMANO), int(origen[1] // TAMANO))
    final = (int(destino[0] // TAMANO), int(destino[1] // TAMANO))
    pendientes = [(0, inicio)]
    coste = {inicio: 0}
    anteriores = {inicio: None}
    peligros = {}
    while pendientes:
        precio, actual = heapq.heappop(pendientes)
        if precio != coste[actual]:
            continue
        if actual == final:
            break
        x, y = actual
        for vecina in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            pos = centro(*vecina)
            if not nivel.posicion_valida(*pos, nivel.prisionero.radio):
                continue
            if vecina not in peligros:
                peligro = 0
                for guardia in nivel.guardias:
                    d = distancia(guardia.get_posicion(), pos)
                    peligro += max(0, 100-d) * .4
                    if dentro_de_vision(guardia.get_posicion(),pos,guardia.angulo,
                                        guardia.alcance,guardia.apertura,nivel.mapa.muros,nivel.prisionero.radio):
                        peligro += 35
                for camara in nivel.camaras:
                    if dentro_de_vision(camara.posicion,pos,camara.angulo,
                                        camara.alcance,camara.apertura,nivel.mapa.muros,nivel.prisionero.radio):
                        peligro += 45
                peligros[vecina] = peligro
            nuevo = precio + 1 + peligros[vecina]
            if nuevo < coste.get(vecina, math.inf):
                coste[vecina] = nuevo
                anteriores[vecina] = actual
                heapq.heappush(pendientes,(nuevo,vecina))
    ruta = []
    actual = final
    while actual != inicio:
        ruta.append(centro(*actual))
        actual = anteriores[actual]
    ruta.reverse()
    return ruta or [destino]


def recorrer(juego, observar=None):
    """Valida el nivel con movimiento, sigilo, espera y carrera; los enemigos siguen activos."""
    nivel = juego.nivel
    abrir_celda(juego)
    for _ in range((120, 40, 20)[nivel.indice]):
        juego.actualizar(.05, set())
    ruta = []
    recalculo = 0
    detenido = 0.0
    for fotograma in range(7000):
        jugador = nivel.prisionero
        pos = jugador.get_posicion()
        destino = nivel.salida.posicion if jugador.tiene_llave() else nivel.llave.posicion
        if fotograma >= recalculo or not ruta:
            ruta = ruta_segura(nivel,destino)
            recalculo = fotograma + 15
        while len(ruta)>1 and distancia(pos,ruta[0])<2:
            ruta.pop(0)
        dx,dy = ruta[0][0]-pos[0],ruta[0][1]-pos[1]
        teclas = set()
        if abs(dx)>1:
            teclas.add('derecha' if dx>0 else 'izquierda')
        elif abs(dy)>1:
            teclas.add('abajo' if dy>0 else 'arriba')
        cerca = min(distancia(pos,g.get_posicion()) for g in nivel.guardias)
        perseguido = any(g.modo == 'PERSIGUE' for g in nivel.guardias)
        esperar = (not perseguido and any(
            not g.puede_detectar(jugador) and dentro_de_vision(
                g.get_posicion(), ruta[0], g.angulo, g.alcance, g.apertura, nivel.mapa.muros)
            for g in nivel.guardias))
        if cerca<180 and not perseguido:
            teclas.add('sigilo')
        if perseguido:
            juego.manejar_entrada('carrera')
        velocidad=145*(.55 if 'sigilo' in teclas else jugador.carrera.get_multiplicador())
        dt=min(.05,max(abs(dx),abs(dy),.01)/velocidad)
        if esperar:
            teclas = set()
            dt = .05
        juego.actualizar(dt,teclas)
        detenido = detenido + dt if distancia(pos,jugador.get_posicion()) < .01 else 0
        if detenido > 12:
            raise AssertionError(f'La ruta espera demasiado en {pos}.')
        if observar:
            observar(juego)
        if juego.estado.nombre == 'DERROTA':
            raise AssertionError(f'Captura nivel {nivel.indice} t={nivel.tiempo:.1f} {pos}')
        if juego.estado.nombre == 'NIVEL_COMPLETADO':
            return fotograma+1
    raise AssertionError(f'Ruta no completada nivel {nivel.indice} t={nivel.tiempo:.1f} pos={pos}, key={jugador.tiene_llave()}')
