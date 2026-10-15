# Qué hace cada clase de Fuga de la Prisión

El juego tiene 22 clases en src y todas aparecen en el UML. Cada apartado explica una clase y muestra su código actual completo. main.py y geometria.py contienen funciones; las clases de tests sirven para comprobar el juego.

## Cómo leer el UML

Cada caja tiene tres partes: nombre, atributos y métodos. Los atributos que guardan otros objetos indican su clase: por ejemplo, carrera: HabilidadCarrera o jefe: Alcaide. Los atributos heredados se muestran en la clase base; las propiedades de consulta aparecen como atributos. Se omiten los constructores en el UML, pero se incluyen en el código completo de abajo. Si una clase no tiene atributos propios, ese compartimento queda vacío.

- Rombo negro (*--): composición. La clase junto al rombo crea sus partes.
- Rombo blanco (o--): agregación. Utiliza objetos creados fuera de ella.
- Triángulo vacío (<|--): herencia. Apunta a la clase base.
- Flecha continua (-->): asociación. Guarda una referencia al otro objeto.
- Flecha discontinua (..>): dependencia. Recibe o utiliza la otra clase.
- 1, 0..1 y 0..*: uno, ninguno o uno, y ninguno o varios, respectivamente.
- + indica acceso público; # marca datos o métodos internos por convención de Python. Optional indica que el valor también puede ser None. Las clases abstractas no se instancian directamente.

La rúbrica pide asociación, agregación, composición, encapsulamiento, herencia y polimorfismo. Las notas siguientes señalan dónde se aplican. State y Observer son patrones de diseño y se nombran aparte.

El [modelo Mermaid](diagramas/modelo_parcial.mmd) es la fuente del [diagrama como imagen](diagramas/modelo_parcial.png). Los bloques de código son para estudiar; para ejecutar se usan los archivos originales con sus importaciones y funciones auxiliares.

## 1. Juego

**Archivo original:** [src/juego.py](../src/juego.py#L7)

**Qué hace.** Coordina la campaña, los niveles, los puntos y el estado de la partida.

**Cómo funciona.** iniciar_partida empieza desde cero; siguiente_nivel conserva los puntos y avanza. reintentar_nivel restaura los puntos que había al entrar al nivel. actualizar valida el tiempo y delega en el estado activo.

**POO que demuestra.** Composición: crea Nivel, Puntaje, PanelPuntaje y los estados de la partida. Polimorfismo: usa manejar_entrada y actualizar del EstadoJuego activo. Aquí se coordina el patrón State.

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
```

## 2. EstadoJuego

**Archivo original:** [src/estados.py](../src/estados.py#L4)

**Qué hace.** Define las operaciones comunes de los estados de la partida.

**Cómo funciona.** Guarda el Juego que recibe. Sus métodos abstractos obligan a las clases hijas a definir la entrada y la actualización.

**POO que demuestra.** Abstracción y herencia: es la base de los cinco estados concretos. Asociación: guarda Juego sin crearlo. Forma parte de State.

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

**Archivo original:** [src/estados.py](../src/estados.py#L19)

**Qué hace.** Mantiene activa la simulación del nivel.

**Cómo funciona.** Permite pausar o activar la carrera. Actualiza el nivel y cambia a Derrota, Victoria o NivelCompletado según su resultado.

**POO que demuestra.** Herencia de EstadoJuego y polimorfismo: implementa sus dos operaciones con el comportamiento de una partida activa.

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
        elif resultado == "nivel_completado":
            self.juego.cambiar_estado(NivelCompletado(self.juego))
```

## 4. Pausa

**Archivo original:** [src/estados.py](../src/estados.py#L38)

**Qué hace.** Detiene la simulación hasta que el jugador continúa.

**Cómo funciona.** La entrada de pausa vuelve a Jugando. actualizar no mueve personajes ni modifica temporizadores, disparos o vida.

**POO que demuestra.** Herencia de EstadoJuego y polimorfismo: recibe las mismas llamadas que Jugando, pero no actualiza el nivel.

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

**Archivo original:** [src/estados.py](../src/estados.py#L49)

**Qué hace.** Espera la decisión del jugador después de perder.

**Cómo funciona.** R repite el nivel actual; N comienza una campaña nueva. Mientras se muestra este estado, el nivel permanece detenido.

**POO que demuestra.** Herencia de EstadoJuego y polimorfismo: redefine la entrada para reintentar o comenzar desde cero.

**Clase completa en el código:**

```python
class Derrota(EstadoJuego):
    nombre = "DERROTA"

    def manejar_entrada(self, tecla):
        if tecla == "reiniciar":
            self.juego.reintentar_nivel()
        elif tecla == "nueva_partida":
            self.juego.iniciar_partida()

    def actualizar(self, dt, teclas):
        pass
```

## 6. Victoria

**Archivo original:** [src/estados.py](../src/estados.py#L62)

**Qué hace.** Representa el final de la campaña completada.

**Cómo funciona.** Mantiene detenido el nivel final y permite comenzar otra campaña con R.

**POO que demuestra.** Herencia de EstadoJuego y polimorfismo: responde a la misma interfaz con el comportamiento de victoria.

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

## 7. NivelCompletado

**Archivo original:** [src/estados.py](../src/estados.py#L73)

**Qué hace.** Separa el final de un nivel del final de toda la campaña.

**Cómo funciona.** Enter llama a siguiente_nivel; N reinicia la campaña. El siguiente nivel no empieza hasta recibir la orden.

**POO que demuestra.** Herencia de EstadoJuego y polimorfismo. Es el quinto estado concreto del patrón State.

**Clase completa en el código:**

```python
class NivelCompletado(EstadoJuego):
    nombre = "NIVEL_COMPLETADO"

    def manejar_entrada(self, tecla):
        if tecla == "continuar":
            self.juego.siguiente_nivel()
        elif tecla == "nueva_partida":
            self.juego.iniciar_partida()

    def actualizar(self, dt, teclas):
        pass
```

## 8. Nivel

**Archivo original:** [src/nivel.py](../src/nivel.py#L63)

**Qué hace.** Reúne el mapa y los objetos de uno de los cuatro niveles.

**Cómo funciona.** Su configuración establece inicio, llave, salida, patrullas y cámaras. Actualiza los personajes y, en la arena, el combate. resolver_interacciones da prioridad a la derrota, concede los premios una sola vez y decide si el nivel o la campaña terminó.

**POO que demuestra.** Composición: crea Prisionero, guardias, cámaras, Llave, PuertaSalida y, solo en el último nivel, Combate. Agregación: recibe un Puntaje creado por Juego. Polimorfismo: llama update a los personajes sin distinguir su clase.

**Clase completa en el código:**

```python
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
        self.muros = []
        self._crear_muros()
        self.prisionero = Prisionero(self, *centro(*self.configuracion["inicio"]))
        self.guardias = [Guardia(self, [centro(*p) for p in ruta])
                         for ruta in self.configuracion["rutas"]]
        self.personajes = [self.prisionero, *self.guardias]
        self.camaras = [Camara(centro(*posicion), angulo)
                        for posicion, angulo in self.configuracion["camaras"]]
        self.llave = Llave(centro(*self.configuracion["llave"]))
        self.salida = PuertaSalida(centro(*self.configuracion["salida"]))
        self.combate = Combate(self) if self.es_final else None
        if self.es_final:
            self.llave.disponible = False

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
                original = horizontal or vertical or divisiones or coberturas
                lavanderia = ((columna in (6, 17) and fila in (2, 3, 4, 8, 9, 10)) or
                              (fila in (4, 9) and 9 <= columna <= 14) or
                              (columna in (3, 20) and fila in (5, 8)))
                patio = ((columna in (5, 18) and fila in (2, 3, 7, 11)) or
                         (fila in (3, 7, 11) and columna in (9, 10, 13, 14)) or
                         (fila == 9 and columna in (3, 4, 20, 21)))
                arena = columna in (5, 18) and fila in (5, 8)
                interior = (original, lavanderia, patio, arena)[self.indice]
                if borde or interior:
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
        if self.combate:
            self.combate.actualizar(dt, self.teclas)
        return self.resolver_interacciones()

    def resolver_interacciones(self):
        if self.terminado:
            return None
        detectado = any(g.puede_detectar(self.prisionero) for g in self.guardias)
        for camara in self.camaras:
            detectado = detectado or camara.detectar(self.prisionero, self.muros)
        # La captura tiene prioridad sobre la llave y la salida.
        if detectado or (self.combate and self.combate.vida <= 0):
            self.terminado = True
            return "derrota"
        if self.combate and self.combate.jefe.derrotado and not self.combate.premiado:
            self.combate.premiado = True
            self.puntaje.sumar(1000)
            self.llave.disponible = True
        if self.llave.recoger(self.prisionero):
            self.puntaje.sumar(100)
        if self.salida.puede_salir(self.prisionero) and (not self.combate or self.combate.jefe.derrotado):
            self.terminado = True
            self.puntaje.sumar(500)
            return "victoria" if self.es_final else "nivel_completado"
        return None
```

## 9. Personaje

**Archivo original:** [src/personajes.py](../src/personajes.py#L39)

**Qué hace.** Reúne la posición y el movimiento compartidos por los personajes.

**Cómo funciona.** get_posicion consulta la posición; mover comprueba los muros en pasos pequeños. update es abstracto y cada clase hija debe implementarlo.

**POO que demuestra.** Abstracción y herencia: base de Prisionero y Guardia. Encapsulamiento: _x, _y y _velocidad son datos internos por convención. Asociación: conserva el Nivel recibido.

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

## 10. Prisionero

**Archivo original:** [src/personajes.py](../src/personajes.py#L66)

**Qué hace.** Es el personaje controlado por el jugador.

**Cómo funciona.** Lee las acciones de movimiento del nivel, normaliza la diagonal y aplica la carrera. Consulta o recoge la llave mediante métodos.

**POO que demuestra.** Herencia de Personaje y polimorfismo en update. Composición: crea HabilidadCarrera. Encapsulamiento: cambia _tiene_llave con recoger_llave y lo consulta con tiene_llave.

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

## 11. Guardia

**Archivo original:** [src/personajes.py](../src/personajes.py#L89)

**Qué hace.** Patrulla una ruta y detecta al prisionero.

**Cómo funciona.** update lo mueve hacia el siguiente punto y orienta su visión. puede_detectar combina un cono frontal de 155 píxeles con una alerta cercana de 32 píxeles en todas direcciones. Considera el cuerpo del jugador y los muros bloquean ambos campos.

**POO que demuestra.** Herencia de Personaje y polimorfismo en update. Dependencia: puede_detectar recibe al Prisionero para comprobarlo, sin guardarlo.

**Clase completa en el código:**

```python
class Guardia(Personaje):
    def __init__(self, nivel, ruta):
        if len(ruta) < 2:
            raise ValueError("La patrulla necesita al menos dos posiciones.")
        super().__init__(nivel, ruta[0][0], ruta[0][1], 65)
        self.ruta = ruta
        self._objetivo = 1
        self.angulo = math.atan2(ruta[1][1] - ruta[0][1], ruta[1][0] - ruta[0][0])
        self.alcance = 155
        self.apertura = math.radians(65)
        self.radio_alerta = 32

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
        posicion = self.get_posicion()
        objetivo = prisionero.get_posicion()
        # Cerca del guardia no se puede permanecer a su lado ni a su espalda.
        if dentro_de_vision(posicion, objetivo, self.angulo, self.radio_alerta,
                            math.tau, self.nivel.muros, prisionero.radio):
            return True
        return dentro_de_vision(posicion, objetivo, self.angulo, self.alcance,
                               self.apertura, self.nivel.muros, prisionero.radio)
```

## 12. HabilidadCarrera

**Archivo original:** [src/personajes.py](../src/personajes.py#L6)

**Qué hace.** Controla el aumento temporal de velocidad del prisionero.

**Cómo funciona.** activar permite correr durante dos segundos si la habilidad está lista. actualizar descuenta la duración y luego los cinco segundos de recarga. Los métodos de consulta devuelven el multiplicador y el texto de estado.

**POO que demuestra.** Encapsulamiento: _duracion y _recarga se gestionan mediante métodos. Composición: cada Prisionero crea su propia habilidad.

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

## 13. Camara

**Archivo original:** [src/nivel.py](../src/nivel.py#L30)

**Qué hace.** Vigila una zona fija del mapa.

**Cómo funciona.** Recibe su posición y orientación. detectar comprueba el cuerpo visible del prisionero dentro de su cono de 95 píxeles; los muros lo ocultan. La lente dibujada apunta en esa misma dirección.

**POO que demuestra.** Composición: Nivel crea sus cámaras. Dependencia: detectar recibe al Prisionero, sin conservarlo.

**Clase completa en el código:**

```python
class Camara:
    def __init__(self, posicion, angulo=math.pi / 2):
        self.posicion = posicion
        self.angulo = angulo
        self.alcance = 95
        self.apertura = math.radians(60)

    def detectar(self, prisionero, muros):
        return dentro_de_vision(self.posicion, prisionero.get_posicion(),
                               self.angulo, self.alcance, self.apertura, muros, prisionero.radio)
```

## 14. Llave

**Archivo original:** [src/nivel.py](../src/nivel.py#L42)

**Qué hace.** Es el objeto que habilita la salida.

**Cómo funciona.** recoger comprueba la cercanía y que todavía esté disponible. La entrega al prisionero y devuelve True una sola vez para que Nivel conceda los puntos.

**POO que demuestra.** Composición: Nivel crea su Llave. Dependencia: recoger utiliza el Prisionero recibido.

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

## 15. PuertaSalida

**Archivo original:** [src/nivel.py](../src/nivel.py#L55)

**Qué hace.** Representa el lugar por el que se termina un nivel.

**Cómo funciona.** puede_salir devuelve si el prisionero tiene la llave y está cerca. Nivel comprueba además que el jefe esté derrotado cuando se trata de la arena.

**POO que demuestra.** Composición: Nivel crea su salida. Dependencia: consulta al Prisionero recibido.

**Clase completa en el código:**

```python
class PuertaSalida:
    def __init__(self, posicion):
        self.posicion = posicion

    def puede_salir(self, prisionero):
        return prisionero.tiene_llave() and distancia(self.posicion, prisionero.get_posicion()) < 22
```

## 16. Puntaje

**Archivo original:** [src/puntuacion.py](../src/puntuacion.py#L18)

**Qué hace.** Conserva los puntos y avisa cuando cambian.

**Cómo funciona.** get_valor consulta el valor; set_valor valida un entero no negativo y notifica a los observadores. sumar valida el incremento. suscribir evita suscripciones repetidas y desuscribir permite retirarlas.

**POO que demuestra.** Encapsulamiento: _valor se administra mediante métodos. Agregación: guarda observadores creados fuera de esta clase. En Observer es el objeto observado. Nivel utiliza este mismo Puntaje por agregación.

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

## 17. ObservadorPuntaje

**Archivo original:** [src/puntuacion.py](../src/puntuacion.py#L4)

**Qué hace.** Define cómo debe recibir los cambios un observador del puntaje.

**Cómo funciona.** actualizar_puntaje es abstracto. Una clase que herede de esta base debe implementar esa operación.

**POO que demuestra.** Abstracción y herencia: es la base de PanelPuntaje dentro del patrón Observer.

**Clase completa en el código:**

```python
class ObservadorPuntaje(ABC):
    @abstractmethod
    def actualizar_puntaje(self, valor):
        pass
```

## 18. PanelPuntaje

**Archivo original:** [src/puntuacion.py](../src/puntuacion.py#L10)

**Qué hace.** Conserva el último puntaje notificado para mostrarlo en pantalla.

**Cómo funciona.** actualizar_puntaje recibe el nuevo valor. Juego lo suscribe a Puntaje y Vista lee su valor para dibujarlo.

**POO que demuestra.** Herencia de ObservadorPuntaje y polimorfismo en actualizar_puntaje. Es el observador concreto de Observer.

**Clase completa en el código:**

```python
class PanelPuntaje(ObservadorPuntaje):
    def __init__(self):
        self.valor = 0

    def actualizar_puntaje(self, valor):
        self.valor = valor
```

## 19. Proyectil

**Archivo original:** [src/combate.py](../src/combate.py#L7)

**Qué hace.** Guarda la posición, velocidad, tamaño y duración de un disparo.

**Cómo funciona.** dataclass genera su constructor. La propiedad posicion devuelve sus coordenadas. avanzar mueve el disparo, descuenta su duración y devuelve el segmento recorrido para comprobar impactos, incluso si el disparo es rápido.

**POO que demuestra.** Composición: Combate crea y conserva los proyectiles. Agrupa los datos y el movimiento de cada disparo en un objeto.

**Clase completa en el código:**

```python
@dataclass
class Proyectil:
    x: float
    y: float
    vx: float
    vy: float
    enemigo: bool = True
    radio: float = 6
    duracion: float = 7

    @property
    def posicion(self):
        return self.x, self.y

    def avanzar(self, dt):
        inicio = self.posicion
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.duracion -= dt
        return inicio, self.posicion
```

## 20. Alcaide

**Archivo original:** [src/combate.py](../src/combate.py#L47)

**Qué hace.** Controla al jefe del último nivel.

**Cómo funciona.** Alterna un aviso previo y tres ataques: corona de lágrimas, ráfaga y embestida. Al bajar a la mitad de vida cambia de fase. La embestida fija su destino y se detiene ante los muros.

**POO que demuestra.** Composición: Combate crea su Alcaide. Dependencia: actualizar y _atacar reciben Combate para emitir disparos y consultar el mapa. Las propiedades posicion, fase y derrotado permiten consultar su situación.

**Clase completa en el código:**

```python
class Alcaide:
    nombre = "EL ALCAIDE"
    vida_maxima = 72
    radio = 28

    def __init__(self):
        self.x, self.y = 450.0, 126.0
        self.vida = self.vida_maxima
        self.espera = 2.0  # Tiempo para leer los controles al entrar.
        self.aviso = 0.0
        self.patron = 0
        self.objetivo = (450.0, 414.0)
        self.destino = None
        self.golpe = 0.0

    @property
    def posicion(self):
        return self.x, self.y

    @property
    def derrotado(self):
        return self.vida <= 0

    @property
    def fase(self):
        return 1 if self.vida > self.vida_maxima / 2 else 2

    @property
    def ataque(self):
        return ("CORONA DE LÁGRIMAS", "RÁFAGA DIRIGIDA", "EMBESTIDA")[self.patron % 3]

    def actualizar(self, combate, dt):
        if self.derrotado:
            return
        self.golpe = max(0, self.golpe - dt)
        if self.destino is not None:
            largo = distancia(self.posicion, self.destino)
            avance = min(largo, (280 if self.fase == 1 else 335) * dt)
            if largo > 0:
                self.x += (self.destino[0] - self.x) / largo * avance
                self.y += (self.destino[1] - self.y) / largo * avance
            if largo <= avance + 0.01:
                self.destino = None
                self.patron += 1
                self.espera = 1.1
            return
        if self.aviso > 0:
            self.aviso = max(0, self.aviso - dt)
            if self.aviso == 0:
                self._atacar(combate)
            return
        self.espera = max(0, self.espera - dt)
        if self.espera == 0:
            self.objetivo = combate.nivel.prisionero.get_posicion()
            self.aviso = 0.95 if self.fase == 1 else 0.75

    def _atacar(self, combate):
        angulo = math.atan2(self.objetivo[1] - self.y, self.objetivo[0] - self.x)
        tipo = self.patron % 3
        if tipo == 0:
            cantidad = 12 if self.fase == 1 else 18
            for i in range(cantidad):
                combate.emitir(self.posicion, angulo + i * math.tau / cantidad,
                               115 if self.fase == 1 else 145)
        elif tipo == 1:
            cantidad = 5 if self.fase == 1 else 7
            for i in range(cantidad):
                combate.emitir(self.posicion, angulo + (i - cantidad // 2) * 0.20, 185)
        else:
            # La embestida fija su destino al comenzar el aviso, se puede esquivar.
            destino = (max(80, min(784, self.objetivo[0])),
                       max(80, min(424, self.objetivo[1])))
            fraccion = min((fraccion_interseccion(self.posicion, destino,
                            (x - self.radio, y - self.radio,
                             w + 2 * self.radio, h + 2 * self.radio))
                            for x, y, w, h in combate.nivel.muros), default=1.0)
            fraccion = max(0, fraccion - 0.005)
            self.destino = (self.x + (destino[0] - self.x) * fraccion,
                            self.y + (destino[1] - self.y) * fraccion)
            return
        self.patron += 1
        self.espera = 1.45 if self.fase == 1 else 0.9
```

## 21. Combate

**Archivo original:** [src/combate.py](../src/combate.py#L131)

**Qué hace.** Resuelve los ataques, los proyectiles y la vida en la arena.

**Cómo funciona.** Crea al jefe y los disparos. Actualiza los ataques y comprueba cada segmento de proyectil contra muros y objetivos. recibir_dano respeta la inmunidad temporal. Al terminar el combate se retiran los proyectiles.

**POO que demuestra.** Composición: crea Alcaide y Proyectil; a su vez, Nivel crea el Combate. Asociación: guarda el Nivel recibido. Separa estas reglas del dibujo de Vista.

**Clase completa en el código:**

```python
class Combate:
    vida_maxima = 5

    def __init__(self, nivel):
        self.nivel = nivel
        self.jefe = Alcaide()
        self.proyectiles = []
        self.vida = self.vida_maxima
        self.inmune = 0.0
        self.recarga = 0.0
        self.premiado = False

    def emitir(self, origen, angulo, velocidad, enemigo=True):
        self.proyectiles.append(Proyectil(*origen, math.cos(angulo) * velocidad,
                                         math.sin(angulo) * velocidad, enemigo,
                                         6 if enemigo else 5))

    def recibir_dano(self):
        if self.inmune > 0 or self.jefe.derrotado:
            return
        self.vida = max(0, self.vida - 1)
        self.inmune = 1.1

    def actualizar(self, dt, teclas):
        self.inmune = max(0, self.inmune - dt)
        self.recarga = max(0, self.recarga - dt)
        if self.jefe.derrotado or self.vida <= 0:
            self.proyectiles.clear()
            return
        jugador = self.nivel.prisionero
        posicion_anterior = self.jefe.posicion
        self.jefe.actualizar(self, dt)
        if contacto_segmento(posicion_anterior, self.jefe.posicion, jugador.get_posicion(),
                             jugador.radio + self.jefe.radio) is not None:
            self.recibir_dano()
        dx = int("tiro_derecha" in teclas) - int("tiro_izquierda" in teclas)
        dy = int("tiro_abajo" in teclas) - int("tiro_arriba" in teclas)
        if self.recarga == 0 and (dx or dy or "disparar" in teclas):
            if not (dx or dy):
                dx = self.jefe.x - jugador.get_posicion()[0]
                dy = self.jefe.y - jugador.get_posicion()[1]
            self.emitir(jugador.get_posicion(), math.atan2(dy, dx), 430, enemigo=False)
            self.recarga = 0.18
        vivos = []
        for tiro in self.proyectiles:
            inicio, fin = tiro.avanzar(dt)
            # Se expande cada muro por el radio del proyectil.
            muro = min((fraccion_interseccion(inicio, fin,
                        (x - tiro.radio, y - tiro.radio, w + 2 * tiro.radio, h + 2 * tiro.radio))
                        for x, y, w, h in self.nivel.muros), default=1.0)
            objetivo = jugador.get_posicion() if tiro.enemigo else self.jefe.posicion
            radio = jugador.radio if tiro.enemigo else self.jefe.radio
            impacto = contacto_segmento(inicio, fin, objetivo, radio + tiro.radio)
            if impacto is not None and impacto <= muro:
                if tiro.enemigo:
                    self.recibir_dano()
                else:
                    self.jefe.vida = max(0, self.jefe.vida - 1)
                    self.jefe.golpe = 0.08
                continue
            if muro < 1.0 or tiro.duracion <= 0:
                continue
            vivos.append(tiro)
        self.proyectiles = [] if self.jefe.derrotado else vivos
```

## 22. Vista

**Archivo original:** [src/vista.py](../src/vista.py#L12)

**Qué hace.** Dibuja el juego con Pygame.

**Cómo funciona.** dibujar ordena el encabezado, mapa, objetos, personajes, combate y controles. Los métodos de apoyo dibujan cada parte. Los conos y los círculos de alerta se recortan con la misma geometría de muros usada por la detección.

**POO que demuestra.** Dependencia: recibe Juego, Nivel y Camara para consultar y dibujar sus datos. No crea ni actualiza las reglas de la partida.

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
        puntos = [self.punto(punto) for punto in
                  poligono_vision(origen, angulo, alcance, apertura, muros)]
        pygame.draw.polygon(capa, (*color, 55), puntos)
        pygame.draw.lines(capa, (*color, 120), False, puntos[1:], 1)
        self.pantalla.blit(capa, (0, 0))

    def dibujar(self, juego):
        nivel = juego.nivel
        self.pantalla.fill((13, 21, 31))
        self._dibujar_encabezado(juego)
        self._dibujar_mapa(nivel)
        self._dibujar_objetivos(nivel)
        for camara in nivel.camaras:
            self._dibujar_camara(camara)
        paso_guardia = round(math.sin(nivel.tiempo * 11) * 3)
        for guardia in nivel.guardias:
            self._dibujar_stickman(self.punto(guardia.get_posicion()), (242, 102, 113), paso_guardia)
        if nivel.combate:
            self._dibujar_combate(nivel)
        paso_prisionero = round(math.sin(nivel.tiempo * 14) * 3) if nivel.teclas else 0
        if not nivel.combate or nivel.combate.inmune <= 0 or int(nivel.tiempo * 12) % 2 == 0:
            self._dibujar_stickman(self.punto(nivel.prisionero.get_posicion()),
                                  (101, 234, 204), paso_prisionero)
        self._dibujar_controles(nivel)
        if juego.estado.nombre != "JUGANDO":
            self._dibujar_panel_estado(juego)

    def _dibujar_encabezado(self, juego):
        nivel = juego.nivel
        self.texto("FUGA DE LA PRISIÓN", 68, 24, fuente=self.titulo)
        self.texto(f"NIVEL {nivel.indice + 1} / {nivel.total_niveles}  ·  {nivel.nombre.upper()}",
                   70, 66, (139, 159, 178), self.pequena)
        self.texto(f"PUNTOS  {juego.panel.valor:04d}", 738, 28, (111, 226, 188), self.mediana)
        self.texto(f"TIEMPO  {nivel.tiempo:05.1f} s", 740, 62, (139, 159, 178), self.pequena)
        llave = "LLAVE OBTENIDA · BUSCA LA SALIDA" if nivel.prisionero.tiene_llave() else "OBJETIVO · CONSIGUE LA LLAVE Y ESCAPA"
        if nivel.combate and not nivel.combate.jefe.derrotado:
            llave = "DERROTA AL ALCAIDE · ESPACIO o IJKL para disparar"
        self.texto(llave, 70, 110, (236, 205, 117), self.pequena)
        self.texto("CARRERA  " + nivel.prisionero.carrera.get_estado(), 651, 110, (164, 201, 232), self.pequena)

    def _dibujar_mapa(self, nivel):
        area = pygame.Rect(*ORIGEN, COLUMNAS * TAMANO, FILAS * TAMANO)
        pygame.draw.rect(self.pantalla, (45, 31, 43) if nivel.es_final else (28, 42, 53), area)
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                rect = pygame.Rect(ORIGEN[0] + columna * TAMANO, ORIGEN[1] + fila * TAMANO, TAMANO, TAMANO)
                pygame.draw.rect(self.pantalla, (33, 48, 60), rect, 1)
        for camara in nivel.camaras:
            self._dibujar_vision(camara.posicion, camara.angulo, camara.alcance, camara.apertura, nivel.muros, (241, 184, 79))
        for guardia in nivel.guardias:
            self._dibujar_vision(guardia.get_posicion(), guardia.angulo, guardia.radio_alerta,
                                 math.tau, nivel.muros, (242, 102, 113))
            self._dibujar_vision(guardia.get_posicion(), guardia.angulo, guardia.alcance, guardia.apertura, nivel.muros, (242, 102, 113))
        for muro in nivel.muros:
            rect = pygame.Rect(muro[0] + ORIGEN[0], muro[1] + ORIGEN[1], muro[2], muro[3])
            pygame.draw.rect(self.pantalla, (62, 78, 90), rect)
            pygame.draw.rect(self.pantalla, (77, 94, 107), rect, 1)
            pygame.draw.line(self.pantalla, (90, 104, 116), rect.topleft, rect.topright)

    def _dibujar_objetivos(self, nivel):
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

    def _dibujar_camara(self, camara):
        x, y = self.punto(camara.posicion)
        dx, dy = math.cos(camara.angulo), math.sin(camara.angulo)
        lente = (round(x + dx * 9), round(y + dy * 9))
        pygame.draw.circle(self.pantalla, (244, 190, 93), (x, y), 10)
        pygame.draw.line(self.pantalla, (37, 43, 48), (x, y), lente, 9)
        pygame.draw.circle(self.pantalla, (101, 159, 180), lente, 3)
        self.texto("CÁMARA", x - 30, y - 34, (244, 190, 93), self.pequena)

    def _dibujar_controles(self, nivel):
        self.texto("WASD / FLECHAS  Mover     SHIFT  Correr     P / ESC  Pausa" +
                   ("     ESPACIO / IJKL  Disparar" if nivel.es_final else ""), 69, 680, fuente=self.pequena)
        consejo = "Cono: visión frontal. Círculo: alerta cercana en todas direcciones. Los muros te ocultan."
        if nivel.es_final:
            consejo = "Espacio apunta al jefe; IJKL fija la dirección. Esquiva los avisos rojos. Tras vencerlo, recoge la llave."
        self.texto(consejo, 69, 709, (139, 159, 178), self.pequena)

    def _dibujar_combate(self, nivel):
        combate = nivel.combate
        jefe = combate.jefe
        self.texto(f"VIDA  {combate.vida} / {combate.vida_maxima}", 70, 86, (255, 147, 161), self.pequena)
        self.texto("ALCAIDE" if not jefe.derrotado else "DERROTADO", 360, 86, (216, 167, 198), self.pequena)
        pygame.draw.rect(self.pantalla, (65, 42, 60), (452, 91, 480, 10), border_radius=5)
        ancho = round(480 * jefe.vida / jefe.vida_maxima)
        if ancho:
            pygame.draw.rect(self.pantalla, (240, 100, 133), (452, 91, ancho, 10), border_radius=5)
        if not jefe.derrotado:
            x, y = self.punto(jefe.posicion)
            if jefe.aviso > 0:
                color = (255, 178, 104)
                pygame.draw.circle(self.pantalla, color, (x, y), jefe.radio + 12, 2)
                if jefe.patron % 3 == 2:
                    destino = self.punto(jefe.objetivo)
                    pygame.draw.line(self.pantalla, (243, 96, 122), (x, y), destino, 3)
                    pygame.draw.circle(self.pantalla, color, destino, 23, 2)
                self.texto(jefe.ataque, 360, 661, color, self.pequena)
            else:
                self.texto(f"FASE {jefe.fase} / 2  ·  " + ("¡EMBESTIDA!" if jefe.destino else "EL ALCAIDE"),
                           360, 661, (216, 167, 198), self.pequena)
            # Un alcaide monstruoso original: gorra, lágrimas y uniforme de rayas.
            pygame.draw.ellipse(self.pantalla, (20, 17, 27), (x - 36, y + 20, 72, 16))
            piel = (255, 230, 232) if jefe.golpe > 0 else ((190, 111, 147) if jefe.fase == 1 else (227, 105, 128))
            pygame.draw.ellipse(self.pantalla, (28, 22, 38), (x - 29, y - 12, 58, 49))
            pygame.draw.ellipse(self.pantalla, piel, (x - 27, y - 33, 54, 54))
            for lado in (-1, 1):
                pygame.draw.circle(self.pantalla, (23, 22, 38), (x + lado * 11, y - 10), 7)
                pygame.draw.line(self.pantalla, (106, 194, 226), (x + lado * 11, y - 4), (x + lado * 14, y + 12), 4)
                pygame.draw.circle(self.pantalla, (239, 218, 227), (x + lado * 12, y - 12), 2)
                pygame.draw.circle(self.pantalla, piel, (x + lado * 30, y + 12), 9)
            pygame.draw.ellipse(self.pantalla, (49, 22, 39), (x - 7, y + 4, 14, 10))
            pygame.draw.rect(self.pantalla, (39, 49, 71), (x - 27, y - 38, 54, 13), border_radius=4)
            pygame.draw.rect(self.pantalla, (226, 190, 102), (x - 5, y - 36, 10, 8), border_radius=2)
            for fila in range(3):
                pygame.draw.line(self.pantalla, (141, 146, 171), (x - 18, y + 20 + fila * 6), (x + 18, y + 20 + fila * 6), 3)
        for tiro in combate.proyectiles:
            x, y = self.punto(tiro.posicion)
            color = (255, 112, 145) if tiro.enemigo else (109, 234, 244)
            pygame.draw.circle(self.pantalla, (22, 17, 33), (x, y), round(tiro.radio + 2))
            pygame.draw.circle(self.pantalla, color, (x, y), round(tiro.radio))
            pygame.draw.circle(self.pantalla, (255, 235, 240), (x - 2, y - 2), 2)

    def _dibujar_panel_estado(self, juego):
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((5, 10, 18, 195))
        self.pantalla.blit(capa, (0, 0))
        pygame.draw.rect(self.pantalla, (26, 40, 53), (220, 250, 560, 250), border_radius=16)
        nombre = juego.estado.nombre
        if nombre == "PAUSA":
            titulo = "PARTIDA EN PAUSA"
            detalle = "La vigilancia y tu habilidad están detenidas."
            accion = "P o ESC para continuar"
            color = (182, 212, 242)
        elif nombre == "VICTORIA":
            titulo = "¡ERES LIBRE!"
            detalle = f"4 niveles y el Alcaide vencidos · {juego.panel.valor} puntos"
            accion = "R para volver a jugar"
            color = (111, 226, 188)
        elif nombre == "NIVEL_COMPLETADO":
            titulo = f"¡NIVEL {juego.indice_nivel + 1} COMPLETADO!"
            detalle = f"Siguiente: {juego.nivel.configuracion_siguiente}"
            accion = "ENTER para continuar · N para empezar de cero"
            color = (111, 226, 188)
        else:
            titulo = "EL ALCAIDE TE DERROTÓ" if juego.nivel.es_final else "TE HAN DETECTADO"
            detalle = "Esquiva los avisos y usa la carrera." if juego.nivel.es_final else "Busca otra ruta y observa la vigilancia."
            accion = "R: reintentar este nivel · N: empezar de cero"
            color = (250, 142, 147)
        self.texto(titulo, 247, 286, color, self.mediana)
        self.texto(detalle, 247, 343)
        self.texto(accion, 247, 398, (236, 205, 117), self.pequena)
        self.texto("Cierra la ventana para salir", 247, 448, (139, 159, 178), self.pequena)
```
