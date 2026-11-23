# Fuga de la Prisión — La última fuga

## Avance de la versión sencilla

El diseño está en [diagramas_uml/LEEME.md](diagramas_uml/LEEME.md). La primera clase implementada es [mapa.py](mapa.py): convierte cada `#` del plano en una pared de 40 × 40 píxeles. Sus atributos son privados y sus dos métodos públicos coinciden con el UML.

Ejemplo para ejecutar en la consola de Python desde esta carpeta, con Pygame instalado:

```python
from mapa import Mapa

plano = [
    "########",
    "#......#",
    "#..##..#",
    "#......#",
    "########",
]

mapa = Mapa(plano)
print(mapa.get_dimensiones())  # (320, 200)
print(len(mapa.get_muros()))   # 24 paredes
```

La segunda clase es [sistema_colisiones.py](sistema_colisiones.py). Recibe un `Mapa` y conserva esa referencia en el atributo privado `__mapa`.

| Método | Trabajo |
|---|---|
| `puede_mover(rect, dx, dy)` | Indica si se puede completar el desplazamiento solicitado. |
| `mover(rect, dx, dy)` | Devuelve un nuevo rectángulo con el desplazamiento permitido, deteniéndose en la primera pared y respetando los límites del mapa. |
| `toca(a, b)` | Indica si los dos rectángulos se superponen. |

Con el mismo mapa del ejemplo:

```python
from pygame import Rect
from sistema_colisiones import SistemaColisiones

colisiones = SistemaColisiones(mapa)
personaje = Rect(50, 90, 20, 20)
print(colisiones.puede_mover(personaje, 200, 0))  # False
print(colisiones.mover(personaje, 200, 0))      # <rect(100, 90, 20, 20)>
```

La pared interior comienza en `x = 120`. Como el personaje mide 20 píxeles de ancho, se detiene en `x = 100`. Primero se resuelve el movimiento horizontal y luego el vertical; así puede deslizarse junto a una pared. El rectángulo original se conserva y se devuelve una copia con la posición resultante. El rectángulo inicial debe estar dentro del mapa, en un espacio libre y tener dimensiones positivas.

Los desplazamientos se aplican en píxeles enteros. Dos bordes apoyados entre sí no cuentan como superposición, según el comportamiento de [pygame.Rect](https://www.pygame.org/docs/ref/rect.html).

Para comprobar las colisiones en Linux:

```bash
PYGAME_HIDE_SUPPORT_PROMPT=1 .venv/bin/python -m unittest tests.test_sistema_colisiones -v
```

El dibujo (`Vista`), los personajes y el resto de clases del UML se incorporarán en los siguientes pasos. Los sprites y tiles preparados en `img/` (prisionero, guardias y escenarios) se reutilizarán en la nueva `Vista` escalados al tamaño de celda (`40 × 40` píxeles).

## Instalación y pruebas

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYGAME_HIDE_SUPPORT_PROMPT=1 .venv/bin/python -m unittest discover -s tests -v
```

En PowerShell (Windows):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
