# Fuga de la Prisión

Videojuego 2D de sigilo y escape en Python y Pygame.  
**UPCH** · Programación Orientada a Objetos (2026-II).

## Ejecución

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Estructura

- `main.py`: punto de entrada, ventana Pygame y música.
- `src/entidades/`: `Personaje`, `Prisionero`, `Guardia`, `GuardiaPatrulla`, `GuardiaCentinela`.
- `src/escenario/`: `Mapa`, `SistemaColisiones`, `Camara`, `Llave`, `Puerta`, `PanelSeguridad`, `Nivel`.
- `src/patrones/`: **Factory Method** (`creadores.py`) y **State** (`estados.py`).
- `src/juego/`: `Juego`, `Puntaje`, `Vista`.
- `data/niveles.json`: configuración de los 7 niveles (2 secciones por sector + Boss Run final contra el Alcaide).
- `img/` y `audio/`: sprites y música del juego.
- `diagramas_uml/`: `UML_Fuga_Prision_v1.pdf` y archivos editables `.drawio`.

## Controles

- **Menú:** `↑ / ↓` (`W / S`) o ratón + `Enter` / clic
- **Mover:** `WASD` o flechas
- **Saltar cinemática:** `Enter` o `Espacio`
- **Pausa:** `P` o `Esc` · **Volver al menú:** `M` · **Reintentar:** `R` · **Pantalla completa:** `F11`
