# Fuga de la Prisión

Videojuego 2D en Python y Pygame desarrollado aplicando los pilares de POO (asociación, agregación, composición, encapsulamiento, herencia y polimorfismo), principios SOLID y dos patrones de diseño (**Factory Method** y **State**).

El diseño completo de las **23 clases** está en [diagramas_uml/LEEME.md](diagramas_uml/LEEME.md) y [diagramas_uml/UML_Fuga_Prision_v1.pdf](diagramas_uml/UML_Fuga_Prision_v1.pdf).

## Estructura del proyecto

| Archivo | Clases | Rol |
|---|---|---|
| `mapa.py` | `Mapa` | Plano de texto y muros de `40 × 40` píxeles. |
| `sistema_colisiones.py` | `SistemaColisiones` | Movimiento acotado contra muros y detección de contacto (`Rect`). |
| `personajes.py` | `Personaje`, `Prisionero`, `Guardia`, `GuardiaPatrulla`, `GuardiaCentinela` | Jerarquía abstracta y actualización polimórfica `update(dt)`. |
| `seguridad.py` | `Camara`, `Llave`, `Puerta`, `PanelSeguridad` | Vigilancia, objetivos y agregación del panel sobre cámaras. |
| `puntaje.py` | `Puntaje` | Control encapsulado del puntaje y restauración al reintentar. |
| `creadores.py` | `CreadorGuardia`, `CreadorPatrulla`, `CreadorCentinela` | Patrón **Factory Method** para crear e incorporar guardias. |
| `nivel.py` | `Nivel` | Composición de todas las entidades de un escenario. |
| `estados.py` | `EstadoJuego`, `Jugando`, `Pausa`, `Derrota`, `Victoria` | Patrón **State** para el flujo de la partida. |
| `juego.py` | `Juego` | Coordinador general y definición de los 3 niveles. |
| `vista.py` | `Vista` | Renderizado en Pygame con los tiles y sprites animados de `img/`. |
| `main.py` | — | Punto de entrada y bucle principal de Pygame. |

## Ejecutar el juego

En Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

En PowerShell (Windows):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

## Controles

| Acción | Tecla |
|---|---|
| Mover al prisionero | `WASD` o flechas |
| Pausar / continuar | `P` o `Esc` |
| Pantalla completa / ventana | `F11` |
| Reintentar nivel (en Derrota) / Nueva partida (en Victoria) | `R` |

## Reglas de la campaña (3 niveles)

1. **Pabellón de celdas**, **Lavandería** y **Patio de vigilancia**.
2. Recoge la **llave** (`+100` puntos) y llega a la **puerta de salida** (`+500` puntos) para avanzar al siguiente nivel.
3. Las **cámaras activas** alertan a los guardias hacia tu posición; solo el contacto con un guardia te captura.
4. El **panel de seguridad** (recuadro azul) apaga temporalmente las cámaras del nivel (`6 s`), a cambio de alertar a los guardias. Solo puede usarse una vez por nivel.
5. Si pierdes, al presionar `R` se reinicia el nivel actual y se restaura el puntaje que tenías al comenzarlo.

## Comprobar colisiones

```bash
PYGAME_HIDE_SUPPORT_PROMPT=1 .venv/bin/python -m unittest discover -s tests -v
```
