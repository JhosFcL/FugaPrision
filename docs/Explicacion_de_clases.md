# Qué hace cada clase de Fuga de la Prisión

Esta guía explica las 18 clases del código actual. En cada apartado aparece primero la explicación y después el bloque completo de la clase, copiado de su archivo original.

main.py abre la ventana, lee el teclado y ejecuta el ciclo del juego. geometria.py aporta funciones de distancia, colisiones y visión. Ninguno declara una clase, por eso no forma parte de las 18.

Los bloques de abajo muestran clases aisladas para estudiar. Para ejecutar el juego se usan los archivos originales, que también incluyen importaciones, constantes y funciones auxiliares.

## 1. Juego

**Archivo original:** [src/juego.py](../src/juego.py#L7-L29)

**Qué hace.** Coordina una partida. Conserva el puntaje, el panel que muestra los puntos, el nivel actual y el estado actual. No dibuja la pantalla ni calcula por sí mismo la ruta del guardia.

**Cómo funciona:**

- __init__ crea el puntaje y el panel, conecta ambos mediante suscribir y comienza una partida.
- iniciar_partida pone el puntaje en cero, crea un nivel nuevo y deja el estado en Jugando. Se usa al iniciar y al reiniciar.
- cambiar_estado reemplaza el estado actual; manejar_entrada entrega la orden del teclado a ese estado.
- actualizar rechaza tiempos inválidos, limita una demora grande a 0,05 segundos y deja que el estado actual actualice la partida.

**Clase completa en el código:**

```python
class Juego:
    def __init__(self):
        self.puntaje = Puntaje()
        self.panel = PanelPuntaje()
        self.puntaje.suscribir(self.panel)
        self.iniciar_partida()

    def iniciar_partida(self):
        self.puntaje.reiniciar()
        self.nivel = Nivel(self.puntaje)
        self.estado = Jugando(self)

    def cambiar_estado(self, estado):
        self.estado = estado

    def manejar_entrada(self, tecla):
        self.estado.manejar_entrada(tecla)

    def actualizar(self, dt, teclas):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("El tiempo debe ser finito y no negativo.")
        # Una demora de la ventana no debe provocar saltos en la simulación.
        self.estado.actualizar(min(dt, 0.05), teclas)
```

## 2. EstadoJuego

**Archivo original:** [src/estados.py](../src/estados.py#L4-L16)

**Qué hace.** Es la base común de los estados del juego. Guarda una referencia a Juego y define las dos acciones que cada estado debe resolver. Al ser abstracta, no representa una partida concreta por sí sola.

**Cómo funciona:**

- nombre es la etiqueta que después se muestra en pantalla.
- __init__ guarda el juego para que el estado pueda cambiarlo o consultar su nivel.
- manejar_entrada y actualizar son métodos abstractos: Jugando, Pausa, Derrota y Victoria deben definirlos.

**Clase completa en el código:**

```python
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
```

## 3. Jugando

**Archivo original:** [src/estados.py](../src/estados.py#L19-L33)

**Qué hace.** Representa la partida activa. Es el estado en el que el nivel avanza, los personajes se mueven y se comprueba si el jugador gana o pierde.

**Cómo funciona:**

- manejar_entrada cambia a Pausa cuando llega la orden pausa; con carrera intenta activar la habilidad del prisionero.
- actualizar llama al nivel. Si el nivel devuelve derrota o victoria, cambia al estado correspondiente.

**Clase completa en el código:**

```python
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
```

## 4. Pausa

**Archivo original:** [src/estados.py](../src/estados.py#L36-L44)

**Qué hace.** Representa la partida detenida temporalmente. Permite volver a jugar sin crear otro nivel.

**Cómo funciona:**

- manejar_entrada regresa a Jugando cuando recibe la orden pausa.
- actualizar contiene pass a propósito: no mueve personajes ni aumenta el tiempo mientras está en pausa.

**Clase completa en el código:**

```python
class Pausa(EstadoJuego):
    nombre = "PAUSA"

    def manejar_entrada(self, tecla):
        if tecla == "pausa":
            self.juego.cambiar_estado(Jugando(self.juego))

    def actualizar(self, dt, teclas):
        pass
```

## 5. Derrota

**Archivo original:** [src/estados.py](../src/estados.py#L47-L55)

**Qué hace.** Representa una partida terminada porque el guardia o la cámara detectó al prisionero.

**Cómo funciona:**

- manejar_entrada crea una partida nueva cuando recibe reiniciar.
- actualizar no hace nada: el nivel queda detenido hasta que el usuario reinicie.

**Clase completa en el código:**

```python
class Derrota(EstadoJuego):
    nombre = "DERROTA"

    def manejar_entrada(self, tecla):
        if tecla == "reiniciar":
            self.juego.iniciar_partida()

    def actualizar(self, dt, teclas):
        pass
```

## 6. Victoria

**Archivo original:** [src/estados.py](../src/estados.py#L58-L66)

**Qué hace.** Representa una partida terminada porque el prisionero llegó a la salida con la llave.

**Cómo funciona:**

- manejar_entrada crea una partida nueva cuando recibe reiniciar.
- actualizar no hace nada: la partida ganada permanece en pantalla hasta el reinicio.

**Clase completa en el código:**

```python
class Victoria(EstadoJuego):
    nombre = "VICTORIA"

    def manejar_entrada(self, tecla):
        if tecla == "reiniciar":
            self.juego.iniciar_partida()

    def actualizar(self, dt, teclas):
        pass
```

## 7. Nivel

**Archivo original:** [src/nivel.py](../src/nivel.py#L47-L117)

**Qué hace.** Contiene las reglas del pabellón. Guarda el mapa, el tiempo, las teclas, los personajes, la cámara, la llave y la salida. Recibe el mismo objeto Puntaje que creó Juego.

**Cómo funciona:**

- __init__ prepara el mapa y crea los objetos del nivel: prisionero, guardia, cámara, llave y puerta de salida.
- _crear_muros recorre las casillas y añade bordes, divisiones y obstáculos según sus coordenadas.
- posicion_valida comprueba que un personaje no salga de los límites ni atraviese un muro.
- actualizar guarda el tiempo y las teclas, llama a update de cada personaje y después revisa las interacciones. Si el nivel ya terminó, no continúa.
- resolver_interacciones comprueba primero la detección: si ocurre, devuelve derrota. Si no, permite recoger la llave por 100 puntos y, al llegar con ella a la salida, suma 500 y devuelve victoria.

**Clase completa en el código:**

```python
class Nivel:
    def __init__(self, puntaje):
        self.puntaje = puntaje
        self.dt = 0.0
        self.tiempo = 0.0
        self.teclas = set()
        self.terminado = False
        self.muros = []
        self._crear_muros()
        self.prisionero = Prisionero(self, *centro(2, 11))
        self.guardia = Guardia(self, [centro(9, 7), centro(17, 7)])
        self.personajes = [self.prisionero, self.guardia]
        # Montada bajo el muro horizontal: vigila el pasillo central.
        self.camaras = [Camara(centro(15, 5))]
        self.llave = Llave(centro(8, 2))
        self.salida = PuertaSalida(centro(21, 2))

    def _crear_muros(self):
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                borde = fila in (0, FILAS - 1) or columna in (0, COLUMNAS - 1)
                horizontal = fila in (4, 9) and 5 <= columna <= 18 and columna not in (11, 12)
                vertical = columna == 5 and fila in (5, 6, 8)
                divisiones = ((columna == 5 and fila in (1, 2)) or
                              (columna == 10 and 1 <= fila <= 3) or
                              (columna == 19 and 1 <= fila <= 3) or
                              (columna == 18 and 10 <= fila <= 12) or
                              (columna == 8 and 5 <= fila <= 7))
                coberturas = ((fila == 6 and 10 <= columna <= 13) or
                              (fila == 5 and 1 <= columna <= 4 and columna != 3) or
                              (fila == 8 and 1 <= columna <= 4 and columna != 2) or
                              (fila == 7 and 20 <= columna <= 22 and columna != 20) or
                              (fila == 4 and 20 <= columna <= 22 and columna != 22))
                if borde or horizontal or vertical or divisiones or coberturas:
                    self.muros.append((columna * TAMANO, fila * TAMANO, TAMANO, TAMANO))

    def posicion_valida(self, x, y, radio):
        if x < radio or y < radio or x > COLUMNAS * TAMANO - radio or y > FILAS * TAMANO - radio:
            return False
        for muro in self.muros:
            if circulo_toca_rectangulo(x, y, radio, muro):
                return False
        return True

    def actualizar(self, dt, teclas):
        if self.terminado:
            return None
        self.dt = dt
        self.teclas = set(teclas)
        self.tiempo += dt
        for personaje in self.personajes:
            personaje.update()
        return self.resolver_interacciones()

    def resolver_interacciones(self):
        if self.terminado:
            return None
        detectado = self.guardia.puede_detectar(self.prisionero)
        for camara in self.camaras:
            detectado = detectado or camara.detectar(self.prisionero, self.muros)
        # La captura tiene prioridad sobre la llave y la salida.
        if detectado:
            self.terminado = True
            return "derrota"
        if self.llave.recoger(self.prisionero):
            self.puntaje.sumar(100)
        if self.salida.puede_salir(self.prisionero):
            self.terminado = True
            self.puntaje.sumar(500)
            return "victoria"
        return None
```

## 8. Personaje

**Archivo original:** [src/personajes.py](../src/personajes.py#L39-L63)

**Qué hace.** Es la base abstracta del prisionero y el guardia. Reúne lo que ambos comparten: nivel, posición, velocidad, tamaño para colisiones y movimiento.

**Cómo funciona:**

- __init__ guarda esos datos; los atributos que comienzan con guion bajo se tratan como internos en Python.
- get_posicion devuelve las coordenadas actuales.
- mover divide el desplazamiento en pasos pequeños y pregunta al nivel si cada paso es válido. Así no cruza muros por moverse rápido.
- update es abstracto: cada clase hija decide cómo se mueve en su propia versión.

**Clase completa en el código:**

```python
class Personaje(ABC):
    def __init__(self, nivel, x, y, velocidad):
        self.nivel = nivel
        self._x = float(x)
        self._y = float(y)
        self._velocidad = velocidad
        self.radio = 10

    def get_posicion(self):
        return self._x, self._y

    def mover(self, dx, dy):
        # Pasos pequeños evitan atravesar muros a velocidades altas.
        pasos = max(1, math.ceil(max(abs(dx), abs(dy)) / 4))
        for _ in range(pasos):
            nuevo_x = self._x + dx / pasos
            if self.nivel.posicion_valida(nuevo_x, self._y, self.radio):
                self._x = nuevo_x
            nuevo_y = self._y + dy / pasos
            if self.nivel.posicion_valida(self._x, nuevo_y, self.radio):
                self._y = nuevo_y

    @abstractmethod
    def update(self):
        pass
```

## 9. Prisionero

**Archivo original:** [src/personajes.py](../src/personajes.py#L66-L86)

**Qué hace.** Es el personaje controlado por el jugador. Hereda el movimiento de Personaje, recuerda si recogió la llave y posee una HabilidadCarrera.

**Cómo funciona:**

- __init__ fija su velocidad normal, inicia sin llave y crea la habilidad de correr.
- tiene_llave consulta si ya consiguió la llave; recoger_llave cambia ese dato a verdadero.
- update lee las direcciones guardadas por Nivel, normaliza el movimiento diagonal para no ganar velocidad extra, aplica la carrera si está activa y actualiza su duración o recarga.

**Clase completa en el código:**

```python
class Prisionero(Personaje):
    def __init__(self, nivel, x, y):
        super().__init__(nivel, x, y, 145)
        self._tiene_llave = False
        self.carrera = HabilidadCarrera()

    def tiene_llave(self):
        return self._tiene_llave

    def recoger_llave(self):
        self._tiene_llave = True

    def update(self):
        teclas = self.nivel.teclas
        dx = int("derecha" in teclas) - int("izquierda" in teclas)
        dy = int("abajo" in teclas) - int("arriba" in teclas)
        norma = math.hypot(dx, dy)
        if norma > 0:
            avance = self._velocidad * self.carrera.get_multiplicador() * self.nivel.dt
            self.mover(dx / norma * avance, dy / norma * avance)
        self.carrera.actualizar(self.nivel.dt)
```

## 10. Guardia

**Archivo original:** [src/personajes.py](../src/personajes.py#L89-L116)

**Qué hace.** Es el enemigo que patrulla. Hereda posición y movimiento de Personaje y añade una ruta y un campo de visión.

**Cómo funciona:**

- __init__ recibe la ruta, se coloca en su primer punto y define velocidad, ángulo, alcance y apertura visual.
- update camina hacia el siguiente punto de la ruta, gira hacia donde se mueve y vuelve al inicio cuando termina el recorrido.
- puede_detectar devuelve verdadero si toca al prisionero o si este está dentro de su campo visual sin un muro de por medio.

**Clase completa en el código:**

```python
class Guardia(Personaje):
    def __init__(self, nivel, ruta):
        super().__init__(nivel, ruta[0][0], ruta[0][1], 65)
        self.ruta = ruta
        self._objetivo = 1
        self.angulo = 0.0
        self.alcance = 155
        self.apertura = math.radians(65)

    def update(self):
        objetivo = self.ruta[self._objetivo]
        largo = distancia(self.get_posicion(), objetivo)
        if largo < 0.01:
            self._objetivo = (self._objetivo + 1) % len(self.ruta)
            objetivo = self.ruta[self._objetivo]
            largo = distancia(self.get_posicion(), objetivo)
        if largo > 0:
            dx = objetivo[0] - self._x
            dy = objetivo[1] - self._y
            self.angulo = math.atan2(dy, dx)
            avance = min(largo, self._velocidad * self.nivel.dt)
            self.mover(dx / largo * avance, dy / largo * avance)

    def puede_detectar(self, prisionero):
        if distancia(self.get_posicion(), prisionero.get_posicion()) <= self.radio + prisionero.radio:
            return True
        return dentro_de_vision(self.get_posicion(), prisionero.get_posicion(),
                               self.angulo, self.alcance, self.apertura, self.nivel.muros)
```

## 11. HabilidadCarrera

**Archivo original:** [src/personajes.py](../src/personajes.py#L6-L36)

**Qué hace.** Controla el impulso de velocidad del prisionero. Existe como objeto propio de Prisionero para que la duración y la recarga no se mezclen con las reglas generales de movimiento.

**Cómo funciona:**

- __init__ empieza con duración y recarga en cero.
- activar funciona solo si la habilidad está libre; inicia dos segundos de carrera y devuelve si pudo activarse.
- actualizar descuenta el tiempo de carrera y luego el de recarga; la recarga dura hasta cinco segundos.
- get_multiplicador devuelve 1,5 mientras corre y 1,0 en los demás casos.
- get_estado prepara el texto que la pantalla muestra: activa, recargando o lista.

**Clase completa en el código:**

```python
class HabilidadCarrera:
    def __init__(self):
        self._duracion = 0.0
        self._recarga = 0.0

    def activar(self):
        if self._duracion > 0 or self._recarga > 0:
            return False
        self._duracion = 2.0
        return True

    def actualizar(self, dt):
        if self._duracion > 0:
            sobrante = max(0.0, dt - self._duracion)
            self._duracion = max(0.0, self._duracion - dt)
            if self._duracion == 0:
                self._recarga = max(0.0, 5.0 - sobrante)
        else:
            self._recarga = max(0.0, self._recarga - dt)

    def get_multiplicador(self):
        if self._duracion > 0:
            return 1.5
        return 1.0

    def get_estado(self):
        if self._duracion > 0:
            return f"ACTIVA  {self._duracion:.1f} s"
        if self._recarga > 0:
            return f"RECARGA  {self._recarga:.1f} s"
        return "LISTA  [SHIFT]"
```

## 12. Camara

**Archivo original:** [src/nivel.py](../src/nivel.py#L14-L23)

**Qué hace.** Es un dispositivo fijo que vigila una zona. A diferencia del guardia, no patrulla ni hereda de Personaje.

**Cómo funciona:**

- __init__ guarda su posición y define hacia dónde mira, hasta dónde alcanza y cuánto abre su visión.
- detectar usa los cálculos de geometria.py para saber si ve al prisionero; los muros pueden bloquear la visión.

**Clase completa en el código:**

```python
class Camara:
    def __init__(self, posicion):
        self.posicion = posicion
        self.angulo = math.pi / 2
        self.alcance = 95
        self.apertura = math.radians(60)

    def detectar(self, prisionero, muros):
        return dentro_de_vision(self.posicion, prisionero.get_posicion(),
                               self.angulo, self.alcance, self.apertura, muros)
```

## 13. Llave

**Archivo original:** [src/nivel.py](../src/nivel.py#L26-L36)

**Qué hace.** Representa el objeto que el prisionero debe recoger antes de escapar.

**Cómo funciona:**

- __init__ guarda su lugar en el mapa y la deja disponible.
- recoger comprueba que todavía exista y que el prisionero esté cerca. Si la recoge, la desactiva, avisa al prisionero y devuelve verdadero. Así no puede recogerse dos veces.

**Clase completa en el código:**

```python
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
```

## 14. PuertaSalida

**Archivo original:** [src/nivel.py](../src/nivel.py#L39-L44)

**Qué hace.** Representa el punto de escape. Solo comprueba si el prisionero puede salir; Nivel es quien decide terminar la partida y sumar puntos.

**Cómo funciona:**

- __init__ guarda la posición de la puerta.
- puede_salir devuelve verdadero únicamente si el prisionero tiene la llave y está cerca de la salida.

**Clase completa en el código:**

```python
class PuertaSalida:
    def __init__(self, posicion):
        self.posicion = posicion

    def puede_salir(self, prisionero):
        return prisionero.tiene_llave() and distancia(self.posicion, prisionero.get_posicion()) < 22
```

## 15. Puntaje

**Archivo original:** [src/puntuacion.py](../src/puntuacion.py#L18-L52)

**Qué hace.** Guarda los puntos de la partida y avisa a quienes muestran ese valor. Juego crea este objeto y Nivel lo usa para sumar puntos.

**Cómo funciona:**

- __init__ empieza en cero y crea la lista de observadores; get_valor permite consultar los puntos.
- set_valor acepta solo enteros no negativos y notifica el cambio. Esto evita guardar un puntaje inválido.
- suscribir registra un observador una sola vez y le envía el valor actual; desuscribir lo retira.
- sumar acepta solo cantidades enteras positivas y usa set_valor para actualizar; reiniciar vuelve a cero.
- _notificar llama a actualizar_puntaje en cada observador. Usa una copia de la lista para recorrerla de forma segura.

**Clase completa en el código:**

```python
class Puntaje:
    def __init__(self):
        self._valor = 0
        self._observadores = []

    def get_valor(self):
        return self._valor

    def set_valor(self, valor):
        """Cambia el puntaje sin permitir valores inválidos y avisa al panel."""
        if type(valor) is not int or valor < 0:
            raise ValueError("El puntaje debe ser un entero no negativo.")
        self._valor = valor
        self._notificar()

    def suscribir(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)
            observador.actualizar_puntaje(self._valor)

    def desuscribir(self, observador):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def sumar(self, cantidad):
        if type(cantidad) is not int or cantidad <= 0:
            raise ValueError("Los puntos deben ser un entero positivo.")
        self.set_valor(self._valor + cantidad)

    def reiniciar(self):
        self.set_valor(0)

    def _notificar(self):
        for observador in tuple(self._observadores):
            observador.actualizar_puntaje(self._valor)
```

## 16. ObservadorPuntaje

**Archivo original:** [src/puntuacion.py](../src/puntuacion.py#L4-L7)

**Qué hace.** Es la base abstracta de cualquier objeto que quiera recibir avisos cuando cambien los puntos.

**Cómo funciona:**

- actualizar_puntaje es el método que una clase hija debe implementar para recibir el valor nuevo.

**Clase completa en el código:**

```python
class ObservadorPuntaje(ABC):
    @abstractmethod
    def actualizar_puntaje(self, valor):
        pass
```

## 17. PanelPuntaje

**Archivo original:** [src/puntuacion.py](../src/puntuacion.py#L10-L15)

**Qué hace.** Es el observador concreto del puntaje. Guarda el valor que Vista mostrará en pantalla.

**Cómo funciona:**

- __init__ empieza con valor cero.
- actualizar_puntaje recibe el nuevo número desde Puntaje y lo guarda. Vista lee después juego.panel.valor para dibujarlo.

**Clase completa en el código:**

```python
class PanelPuntaje(ObservadorPuntaje):
    def __init__(self):
        self.valor = 0

    def actualizar_puntaje(self, valor):
        self.valor = valor
```

## 18. Vista

**Archivo original:** [src/vista.py](../src/vista.py#L12-L135)

**Qué hace.** Dibuja lo que el jugador ve con Pygame. Lee datos de Juego y Nivel, pero no decide si hubo victoria, derrota o puntos ganados. Aquí se dibujan los personajes como stickmen.

**Cómo funciona:**

- __init__ guarda la superficie de dibujo y prepara los tamaños de letra.
- texto dibuja una cadena en la pantalla; punto traslada una posición del mapa a una posición visible en la ventana.
- _dibujar_stickman forma cabeza, cuerpo, brazos y piernas con círculos y líneas.
- _dibujar_vision dibuja el cono transparente del guardia o la cámara y lo corta donde hay muros.
- dibujar arma la pantalla completa: título, puntos, tiempo, mapa, muros, visión, llave, salida, cámara, guardia y prisionero.
- _dibujar_panel_estado coloca encima el mensaje de pausa, victoria o derrota con la tecla para continuar.

**Clase completa en el código:**

```python
class Vista:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("segoeui", 18)
        self.pequena = pygame.font.SysFont("segoeui", 15)
        self.titulo = pygame.font.SysFont("segoeui", 32, bold=True)
        self.mediana = pygame.font.SysFont("segoeui", 23, bold=True)

    def texto(self, texto, x, y, color=(225, 234, 242), fuente=None):
        imagen = (fuente or self.fuente).render(texto, True, color)
        self.pantalla.blit(imagen, (x, y))

    def punto(self, posicion):
        return round(posicion[0] + ORIGEN[0]), round(posicion[1] + ORIGEN[1])

    def _dibujar_stickman(self, posicion, color, paso=0):
        x, y = posicion
        pygame.draw.ellipse(self.pantalla, (15, 25, 33), (x - 11, y + 12, 22, 6))

        cabeza = (x, y - 11)
        torso = ((x, y - 5), (x, y + 5))
        brazo_izquierdo = ((x, y - 2), (x - 9, y + 3))
        brazo_derecho = ((x, y - 2), (x + 9, y + 3))
        pierna_izquierda = ((x, y + 5), (x - 7 + paso, y + 15))
        pierna_derecha = ((x, y + 5), (x + 7 - paso, y + 15))

        for inicio, fin in (torso, brazo_izquierdo, brazo_derecho,
                            pierna_izquierda, pierna_derecha):
            pygame.draw.line(self.pantalla, (14, 27, 35), inicio, fin, 7)
            pygame.draw.line(self.pantalla, color, inicio, fin, 4)

        pygame.draw.circle(self.pantalla, (14, 27, 35), cabeza, 7)
        pygame.draw.circle(self.pantalla, color, cabeza, 5)

    def _dibujar_vision(self, origen, angulo, alcance, apertura, muros, color):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        puntos = [self.punto(origen)]
        for indice in range(61):
            direccion = angulo - apertura / 2 + apertura * indice / 60
            destino = (origen[0] + math.cos(direccion) * alcance,
                       origen[1] + math.sin(direccion) * alcance)
            puntos.append(self.punto(extremo_visible(origen, destino, muros)))
        pygame.draw.polygon(capa, (*color, 55), puntos)
        pygame.draw.lines(capa, (*color, 120), False, puntos[1:], 1)
        self.pantalla.blit(capa, (0, 0))

    def dibujar(self, juego):
        nivel = juego.nivel
        self.pantalla.fill((13, 21, 31))
        self.texto("FUGA DE LA PRISIÓN", 68, 24, fuente=self.titulo)
        self.texto("PROTOTIPO PARCIAL  /  PABELLÓN 01", 70, 66, (139, 159, 178), self.pequena)
        self.texto(f"PUNTOS  {juego.panel.valor:04d}", 738, 28, (111, 226, 188), self.mediana)
        self.texto(f"TIEMPO  {nivel.tiempo:05.1f} s", 740, 62, (139, 159, 178), self.pequena)
        llave = "LLAVE OBTENIDA · BUSCA LA SALIDA" if nivel.prisionero.tiene_llave() else "OBJETIVO · CONSIGUE LA LLAVE Y ESCAPA"
        self.texto(llave, 70, 110, (236, 205, 117), self.pequena)
        self.texto("CARRERA  " + nivel.prisionero.carrera.get_estado(), 651, 110, (164, 201, 232), self.pequena)
        area = pygame.Rect(*ORIGEN, COLUMNAS * TAMANO, FILAS * TAMANO)
        pygame.draw.rect(self.pantalla, (28, 42, 53), area)
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                rect = pygame.Rect(ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO, TAMANO, TAMANO)
                pygame.draw.rect(self.pantalla, (33, 48, 60), rect, 1)
        for camara in nivel.camaras:
            self._dibujar_vision(camara.posicion, camara.angulo, camara.alcance, camara.apertura, nivel.muros, (241, 184, 79))
        guardia = nivel.guardia
        self._dibujar_vision(guardia.get_posicion(), guardia.angulo, guardia.alcance, guardia.apertura, nivel.muros, (242, 102, 113))
        for muro in nivel.muros:
            rect = pygame.Rect(muro[0] + ORIGEN[0], muro[1] + ORIGEN[1], muro[2], muro[3])
            pygame.draw.rect(self.pantalla, (62, 78, 90), rect)
            pygame.draw.rect(self.pantalla, (77, 94, 107), rect, 1)
            pygame.draw.line(self.pantalla, (90, 104, 116), rect.topleft, rect.topright)
        salida = self.punto(nivel.salida.posicion)
        color_salida = (103, 222, 176) if nivel.prisionero.tiene_llave() else (93, 126, 117)
        pygame.draw.rect(self.pantalla, color_salida, (salida[0] - 14, salida[1] - 15, 28, 30), 3, border_radius=3)
        self.texto("SALIDA", salida[0] - 27, salida[1] + 20, color_salida, self.pequena)
        if nivel.llave.disponible:
            x, y = self.punto(nivel.llave.posicion)
            pygame.draw.circle(self.pantalla, (246, 210, 102), (x - 5, y), 6, 3)
            pygame.draw.line(self.pantalla, (246, 210, 102), (x, y), (x + 13, y), 4)
            pygame.draw.line(self.pantalla, (246, 210, 102), (x + 10, y), (x + 10, y + 6), 3)
            self.texto("LLAVE", x - 22, y + 18, (246, 210, 102), self.pequena)
        for camara in nivel.camaras:
            x, y = self.punto(camara.posicion)
            pygame.draw.line(self.pantalla, (152, 169, 179), (x, y - 18), (x, y - 7), 3)
            pygame.draw.rect(self.pantalla, (244, 190, 93), (x - 10, y - 8, 20, 12), border_radius=3)
            pygame.draw.circle(self.pantalla, (37, 43, 48), (x, y + 2), 5)
            pygame.draw.circle(self.pantalla, (101, 159, 180), (x, y + 2), 2)
            self.texto("CÁMARA", x - 30, y - 42, (244, 190, 93), self.pequena)
        gx, gy = self.punto(guardia.get_posicion())
        paso_guardia = round(math.sin(nivel.tiempo * 11) * 3)
        self._dibujar_stickman((gx, gy), (242, 102, 113), paso_guardia)
        px, py = self.punto(nivel.prisionero.get_posicion())
        paso_prisionero = round(math.sin(nivel.tiempo * 14) * 3) if nivel.teclas else 0
        self._dibujar_stickman((px, py), (101, 234, 204), paso_prisionero)
        self.texto("WASD / FLECHAS  Mover     SHIFT  Correr     P / ESC  Pausa", 69, 680, fuente=self.pequena)
        self.texto("Evita las zonas de visión. Los muros te ocultan. Contactar al guardia también te captura.", 69, 709, (139, 159, 178), self.pequena)
        if juego.estado.nombre != "JUGANDO":
            self._dibujar_panel_estado(juego)

    def _dibujar_panel_estado(self, juego):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((5, 10, 18, 195))
        self.pantalla.blit(capa, (0, 0))
        pygame.draw.rect(self.pantalla, (26, 40, 53), (245, 250, 510, 235), border_radius=16)
        nombre = juego.estado.nombre
        if nombre == "PAUSA":
            titulo = "PARTIDA EN PAUSA"
            detalle = "La vigilancia y tu habilidad están detenidas."
            accion = "P o ESC para continuar"
            color = (182, 212, 242)
        elif nombre == "VICTORIA":
            titulo = "¡ESCAPASTE DEL PABELLÓN!"
            detalle = f"Nivel completado · {juego.panel.valor} puntos"
            accion = "R para volver a jugar"
            color = (111, 226, 188)
        else:
            titulo = "TE HAN DETECTADO"
            detalle = "Busca otra ruta y observa la vigilancia."
            accion = "R para intentarlo de nuevo"
            color = (250, 142, 147)
        self.texto(titulo, 275, 286, color, self.mediana)
        self.texto(detalle, 275, 343)
        self.texto(accion, 275, 398, (236, 205, 117))
        self.texto("Cierra la ventana para salir", 275, 438, (139, 159, 178), self.pequena)
```
