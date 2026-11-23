# Fuga de la Prisión: propuesta UML v1

Fecha de la propuesta: 19 de noviembre de 2026.

Este modelo describe el diseño que estamos implementando desde cero en la raíz del proyecto (`Mapa` y `SistemaColisiones` ya están implementados; las demás clases se irán incorporando junto con los sprites de `img/`).

## Archivos

- [UML_Fuga_Prision_v1.pdf](UML_Fuga_Prision_v1.pdf): las cinco láminas para consultar o imprimir.
- `drawio/`: un archivo editable por cada lámina del PDF.
- `LEEME.md`: este documento, con la explicación del diseño.

| Página del PDF | Archivo editable |
|---|---|
| 1. Estructura principal | [01_estructura_principal.drawio](drawio/01_estructura_principal.drawio) |
| 2. Personajes y seguridad | [02_personajes_y_seguridad.drawio](drawio/02_personajes_y_seguridad.drawio) |
| 3. Factory Method | [03_factory_method.drawio](drawio/03_factory_method.drawio) |
| 4. State: clases | [04_state_clases.drawio](drawio/04_state_clases.drawio) |
| 5. State: transiciones | [05_state_transiciones.drawio](drawio/05_state_transiciones.drawio) |

### Abrir y editar

1. Descarga el `.drawio` desde GitHub con **Download raw file**.
2. En [app.diagrams.net](https://app.diagrams.net/), elige **Archivo → Abrir desde → Dispositivo** y selecciona el archivo.
3. Ajusta el zoom. La distribución ya está preparada.
4. Para mover una clase completa, selecciona su grupo. Para cambiar un atributo o método, entra en el grupo y edita su texto. Las multiplicidades y etiquetas de relación son textos independientes.

El modelo tiene **23 clases distintas**. Las láminas presentan vistas complementarias del mismo diseño. `Juego` y `Nivel` se repiten resumidos donde solo se necesita mostrar el patrón; su definición completa está en la lámina 01. La distribución por láminas permite consultar todas las clases sin convertir el UML en una imagen gigante.

La simplificación consiste en reducir reglas, responsabilidades mezcladas y dependencias. State y Factory Method requieren clases de tamaño pequeño, por lo que el número de clases por sí solo no mide la dificultad del proyecto.

## Decisiones del diseño

1. **State y Factory Method son los dos patrones elegidos.**
2. `Juego` coordina la partida. Conserva el estado actual, el nivel, el puntaje y la vista. Sus estados delegan en sus operaciones públicas.
3. `Nivel` reúne los objetos de un escenario. No dibuja ni contiene el bucle general. Tampoco tiene una cadena de condicionales para decidir qué clase de guardia crear.
4. `Mapa` representa el plano y las paredes; `SistemaColisiones` calcula contactos y movimientos permitidos.
5. Los personajes reciben un `SistemaColisiones`, no el `Nivel` completo. Así evitan conocer cámaras, puntaje, teclas, estados y demás detalles del escenario.
6. `Prisionero`, `GuardiaPatrulla` y `GuardiaCentinela` implementan `update(dt)`. Todos pueden actualizarse mediante una misma llamada sobre la colección de personajes.
7. La entrada cambia la dirección del prisionero mediante `set_direccion()`. `update(dt)` aplica el movimiento.
8. `Vista` consulta el juego para dibujarlo. No decide capturas, puntos, apertura de puertas ni transiciones de partida.
9. Se retiran de este modelo el jefe, los proyectiles, el ruido avanzado y la carrera con recarga. La propuesta conserva el escape, la vigilancia y el panel de seguridad.
10. El modelo no introduce Logger, Singleton, Strategy ni Observer.

## Responsabilidades de las 23 clases

| Clase | Trabajo |
|---|---|
| Juego | Coordinar entrada, actualización, cambio de nivel y estado. |
| Nivel | Conservar las entidades y colaboradores de un escenario. |
| Mapa | Representar la distribución del escenario. |
| SistemaColisiones | Comprobar contacto y desplazamiento frente a las paredes. |
| Vista | Dibujar el juego y sus mensajes. |
| Puntaje | Mantener un entero no negativo y aplicar premios válidos. |
| Personaje | Definir posición, velocidad, movimiento y actualización común. |
| Prisionero | Ejecutar el movimiento indicado por el jugador y conservar la posesión de la llave. |
| Guardia | Reunir la alerta y la persecución compartidas por los guardias. |
| GuardiaPatrulla | Recorrer una ruta; reaccionar a la alerta. |
| GuardiaCentinela | Vigilar una posición; reaccionar a la alerta. |
| Camara | Detectar contacto del cuerpo del jugador con su zona de vigilancia cuando está activa. |
| Llave | Controlar su recogida una sola vez. |
| Puerta | Conservar su apertura; el juego comprueba previamente la posesión de la llave. |
| PanelSeguridad | Desactivar temporalmente sus cámaras y reactivarlas al terminar el tiempo. |
| CreadorGuardia | Definir el método fábrica y el procedimiento común para incorporar un guardia. |
| CreadorPatrulla | Construir un GuardiaPatrulla. |
| CreadorCentinela | Construir un GuardiaCentinela. |
| EstadoJuego | Definir la entrada y actualización comunes de los estados. |
| Jugando | Permitir que el nivel avance y resolver sus resultados mediante Juego. |
| Pausa | Conservar detenidos el nivel y sus temporizadores. |
| Derrota | Esperar y procesar el reinicio del nivel. |
| Victoria | Esperar y procesar una nueva partida. |

## Lectura de los símbolos

- `-`: privado. En el código propuesto se usará `self.__nombre` para estos atributos.
- `#`: protegido, para uso de la clase y sus subclases. `EstadoJuego.juego` es la única referencia protegida del catálogo y se implementaría como `self._juego`.
- `+`: operación pública.
- `«abstract»`: clase que no se instancia directamente. Las operaciones abstractas aparecen en cursiva.
- Triángulo vacío: herencia; apunta a la clase base.
- Rombo negro: composición; está junto al propietario de la parte.
- Rombo blanco: agregación; está junto al objeto que reúne referencias a partes con propietario independiente.
- Flecha continua: asociación navegable; el origen conserva una referencia al destino.
- Flecha discontinua: dependencia; el origen utiliza el destino en una operación.
- `1`, `0..1` y `0..*`: uno, cero o uno, y cero o varios.

`Rect`, `Surface` y `Event` son tipos de Pygame, no clases nuevas del dominio. `list<T>` expresa el tipo de sus elementos en el UML; en Python se empleará la sintaxis correspondiente a la versión elegida.

Los constructores `__init__` se omiten en esta vista conceptual, como ocurre en el modelo de Mario usado como referencia. Se implementarán cuando inicialicen datos necesarios. Un método heredado no se repite en cada clase hija salvo cuando se redefine.

## Justificación de las relaciones

### Composición

- `Juego` posee su `Nivel` actual, su `Puntaje`, su `Vista` y su `EstadoJuego` actual.
- Cada `Nivel` posee su `Mapa`, su `SistemaColisiones` y sus entidades. Al cargar otro nivel, se reemplaza ese conjunto de objetos.
- La colección de personajes contiene exactamente un prisionero y cero o más guardias. La relación con `Personaje` se muestra como `1..*`.
- Cada nivel tiene una llave y una puerta. Puede tener cero o más cámaras y, en esta propuesta, cero o un panel.

La composición representa pertenencia y ciclo de vida del modelo. No se justifica únicamente porque aparezca una llamada a un constructor dentro de otra clase.

### Agregación

`PanelSeguridad` reúne referencias a cámaras que ya pertenecen al `Nivel`. Quitar el panel no elimina las cámaras. Esta es la relación con rombo blanco de la lámina 02. Una cámara puede no estar vinculada a ningún panel; se permite como máximo uno por cámara en este diseño.

### Asociación y dependencia

- `SistemaColisiones` conserva el mapa que recibe; no crea otro mapa.
- `Personaje` conserva el sistema de colisiones que recibe, visible en sus atributos. Cada personaje sigue funcionando mediante operaciones de ese colaborador, sin guardar el nivel completo.
- `EstadoJuego` conserva la referencia al `Juego` recibido para llamar a sus operaciones públicas.
- `Vista.dibujar(juego)` usa el juego recibido durante la operación.
- `Juego.cargar_nivel()` usa los creadores de guardias. Los creadores utilizan el nivel para incorporar el producto.

## Demostración de los patrones

### Factory Method

Se conserva la estructura del ejemplo de notificaciones del curso:

| Ejemplo del curso | Prisión |
|---|---|
| Servicio | CreadorGuardia |
| notificar() | incorporar() |
| crear() | crear() |
| Notificacion | Guardia |
| ServicioCorreo / ServicioSMS | CreadorPatrulla / CreadorCentinela |
| Correo / SMS | GuardiaPatrulla / GuardiaCentinela |

`crear()` es abstracto en el creador base. `incorporar()` es concreto y se hereda: llama al método fábrica y agrega el resultado al nivel. Los creadores concretos redefinen `crear()`. El parámetro `datos` contiene una configuración sencilla de posición y, para la patrulla, su ruta. El sistema de colisiones llega como colaborador.

### State

`Juego.procesar_evento()` delega en `EstadoJuego.manejar_evento()` y `Juego.update()` delega en `EstadoJuego.update()`.

- Jugando actualiza el nivel mediante `Juego.actualizar_nivel()`.
- Pausa no actualiza el nivel ni consume el tiempo del panel.
- Derrota permite reiniciar el nivel.
- Victoria permite iniciar una nueva partida.

Las operaciones `update()` de Pausa, Derrota y Victoria mantienen intencionadamente detenido el escenario. El avance por una salida intermedia carga el siguiente nivel y permanece en Jugando.

## Mecánica del panel y reglas de coordinación

La propuesta consiste en apagar temporalmente las cámaras a cambio de alertar a los guardias. Cada panel se puede activar una vez por nivel. La duración se fijará al probar el primer escenario.

1. Juego detecta la interacción del prisionero con el panel.
2. `PanelSeguridad.activar()` devuelve si acaba de activarse y desactiva sus cámaras.
3. Juego utiliza ese resultado para llamar a `Guardia.alertar()` sobre los guardias del nivel. El panel no guarda referencias a guardias.
4. `PanelSeguridad.update(dt)` descuenta tiempo y vuelve a activar las cámaras cuando corresponde.

Las cámaras usan una zona rectangular de vigilancia situada en un pasillo despejado. Se evita añadir al primer prototipo la geometría avanzada de conos y rayos del proyecto anterior.

La captura se produce por contacto con un guardia. Una cámara activa alerta; no termina inmediatamente la partida. Juego comprueba la llave antes de abrir la puerta y premia cada recogida o salida una sola vez. Al entrar en un nivel, guarda `puntos_inicio_nivel`; al reintentarlo usa `Puntaje.restaurar()` con ese valor. Así conserva los premios de niveles terminados y evita acumular repetidamente la misma llave tras cada derrota. Los getters geométricos devuelven copias de los Rect; los cambios de posición pasan por `mover()`.

## Comprobaciones del modelo

- Las 23 clases aparecen en al menos una lámina.
- Las clases repetidas reutilizan el mismo catálogo de atributos y métodos.
- Los atributos de dominio son privados. La referencia al contexto de State es protegida y está justificada.
- Los productos concretos heredan de Guardia y los creadores concretos heredan de CreadorGuardia.
- El método fábrica es abstracto y el procedimiento que lo utiliza es concreto.
- Ningún Personaje guarda un Nivel.
- Mapa no dibuja ni resuelve colisiones.
- Se muestran los cuatro estados concretos y sus transiciones.

Este es un punto de partida para revisar el diseño con el equipo. Cuando se implemente, se deberán contrastar los diagramas con el código final antes de presentarlos como evidencia.
