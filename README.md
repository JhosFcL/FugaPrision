# Fuga de la Prisión — proyecto parcial.

Prototipo 2D en Python y Pygame. El prisionero y el guardia se dibujan como stickmen.

## Ejecutar.

Desde esta carpeta, en PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Controles: WASD o flechas para mover; Shift para correr; P o Escape para pausar; R para reiniciar después de ganar o perder.

## Material del parcial.

- `entrega/Informe_Parcial_Fuga_Prision.pdf`: informe para presentar.
- `docs/diagramas/modelo_parcial.mmd` y `modelo_parcial.png`: UML de nueve clases, en Mermaid y como imagen.
- `docs/evidencias/`: capturas de inicio, pausa, victoria y derrota, salida de pruebas e historial Git revisado.
- `docs/03_guion_exposicion.md`: apoyo para la explicación oral.
- `main.py` y `src/`: juego y clases.
- `tests/` y `tools/verificar.py`: pruebas y generación reproducible de capturas.

Para comprobar el avance después de instalar las dependencias:

```powershell
.venv\Scripts\python.exe tools\verificar.py
```
