# Cómo leer el UML

El diagrama para el informe es `modelo_parcial.mmd` (fuente Mermaid.js) y `modelo_parcial.png` (lámina para imprimir). Muestra nueve clases clave del código. `modelo_completo.mmd` amplía el modelo a once clases, incluida `Vista` y `HabilidadCarrera`.

Cada clase tiene tres partes: **nombre**, **atributos** y **métodos**. Se incluyen solo los miembros necesarios para explicar el diseño; no es un inventario de cada línea del programa. `+` significa acceso público; `#` indica uso interno/protegido en el modelo. En Python el guion bajo es una convención, no una barrera absoluta. `Optional[str]` representa que `Nivel.actualizar()` y `resolver_interacciones()` pueden devolver `"victoria"`, `"derrota"` o `None`.

| Símbolo | Significado | Ejemplo comprobable |
| --- | --- | --- |
| Triángulo vacío `<\|--` | Herencia | `Prisionero` y `Guardia` derivan de `Personaje`. |
| Rombo negro `*--` | Composición | `Nivel` crea los objetos de su pabellón. |
| Rombo blanco `o--` | Agregación | `Nivel` recibe el `Puntaje` creado por `Juego`. |
| Flecha continua `-->` | Asociación navegable | `Personaje` guarda una referencia a `Nivel`. |
| Flecha discontinua `..>` | Dependencia | `Camara.detectar()` usa el `Prisionero` recibido. |
| `"1"` | Multiplicidad | En este prototipo hay un objeto de cada tipo representado en el extremo. |

El rombo se coloca **junto al todo**: en `Nivel o-- Puntaje`, el rombo blanco está junto a `Nivel`; en `Nivel *-- Camara`, el negro está junto a `Nivel`. Los nombres de las relaciones se explican aquí para no llenar el gráfico de palabras. Esta notación sigue las sesiones 1, 3 y 4 del curso; la rúbrica exige que las relaciones del diagrama sean claras.

El archivo `.mmd` es la fuente editable en Mermaid.js y la imagen PNG permite consultar el diagrama sin abrir un editor.
