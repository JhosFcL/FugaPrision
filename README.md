# Fuga de la Prisión — proyecto parcial

Juego 2D del proyecto parcial de Programación Orientada a Objetos. El prisionero y el guardia se dibujan como stickmen.

## Dónde está cada cosa

| Carpeta o archivo | Contenido |
| --- | --- |
| `main.py`, `src/` | Juego ejecutable y clases de POO. |
| `tests/`, `tools/verificar.py` | Pruebas del avance y generación de capturas. |
| `docs/diagramas/modelo_parcial.mmd` y `.png` | UML principal de 9 clases, editable en Mermaid y visible en el informe. |
| `docs/diagramas/modelo_completo.mmd` | Modelo ampliado de 11 clases. |
| `docs/03_guion_exposicion.md` | Guion para mostrar el juego y explicar el código. |
| `docs/evidencias/` | Capturas actuales, resultados JSON y salida de las pruebas. |
| `entrega/` | Informe parcial en Markdown, Word y PDF. |
| `.git/` | Historial local real del proyecto. |

## Ejecutar

Desde esta carpeta, en PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Controles: WASD o flechas para mover; Shift para correr; P o Escape para pausar; R para reiniciar después de ganar o perder.

Para ejecutar las pruebas después de instalar las dependencias:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools\verificar.py
```

## Estado de entrega

El primer nivel tiene movimiento, colisiones, guardia, cámara, llave, salida, puntaje, pausa y reinicio. State y Observer están implementados. El informe está en `entrega/` y el UML en `docs/diagramas/`. Las 21 pruebas automáticas pasan. Aún faltan la prueba manual en el equipo de exposición y los aportes reales de Git de los demás integrantes; el historial actual no demuestra trabajo en equipo al 100 %.
