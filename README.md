# Fuga de la Prisión — La última fuga

Juego 2D en Python y Pygame con una campaña de cuatro niveles. Los tres primeros
combinan sigilo, llaves, patrullas y cámaras; el último es una arena contra un jefe
original inspirado en los patrones de proyectiles de The Binding of Isaac.

## Campaña

1. **Pabellón de celdas:** cuatro sectores comunicados por puertas, dos patrullas y una cámara.
2. **Lavandería:** un mapa nuevo con coberturas, dos patrullas y dos cámaras.
3. **Patio de vigilancia:** otro mapa con dos patrullas y tres cámaras.
4. **El Alcaide:** cinco puntos de vida para enfrentarte al jefe. Lanza coronas de
   lágrimas, ráfagas dirigidas y embestidas que avisa antes de atacar. Al bajar de
   la mitad de vida entra en una segunda fase más intensa. Derrótalo, recoge la
   llave que aparece en la arena y alcanza la salida para completar la campaña.

El puntaje se acumula: 100 por llave, 500 por nivel y 1000 por derrotar al jefe
(3400 al completar la campaña). Al perder puedes repetir el nivel actual:
conservas los puntos de niveles anteriores y se restablece el nivel completo.

## Ejecutar.

Desde esta carpeta, en PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

## Controles

| Acción | Tecla |
| --- | --- |
| Mover | WASD o flechas |
| Correr | Shift (2 s de duración, 5 s de recarga) |
| Caminar en sigilo | Mantener Ctrl (menos velocidad y menos ruido) |
| Disparar hacia el jefe, en la arena | Mantener Espacio |
| Disparar en una dirección, en la arena | I arriba, J izquierda, K abajo, L derecha |
| Pausar / continuar | P o Escape |
| Pasar al siguiente nivel | Enter, tras completar el actual |
| Reintentar el nivel tras perder | R |
| Empezar desde el primer nivel tras perder o entre niveles | N |
| Nueva campaña tras ganar | R |

En la arena, los muros bloquean proyectiles y dispones de un breve período de
inmunidad tras recibir daño. La pausa y la pérdida de foco detienen toda la simulación.

Los pasos generan ruido: Ctrl produce poco, caminar produce más y correr se oye
desde más lejos. El sonido llega siguiendo los pasillos y las puertas. Quedarte
quieto o empujar una pared no genera pasos. Los guardias investigan la posición
que escuchan; si te ven o una cámara les avisa, te persiguen rodeando las paredes.
Solo te capturan al alcanzarte. Si rompes la visión, buscan en la última posición
conocida y después regresan a patrullar. `?` indica investigación o búsqueda y
`!` indica persecución. La interfaz muestra el ruido y la alerta actual.

Los planos tienen perímetro cerrado y divisiones con pasos definidos, sin huecos
aislados ni una ruta libre alrededor de todo el borde. Las colisiones recortan el
movimiento ante la primera pared, incluso en diagonal o con un desplazamiento grande.

## Material del parcial

- `entrega/Informe_Parcial_Fuga_Prision.pdf`: informe para presentar.
- `docs/diagramas/modelo_parcial.mmd` y `modelo_parcial.png`: UML de las 24 clases del juego, en Mermaid y como imagen generada desde el mismo modelo.
- `docs/evidencias/`: doce capturas de la campaña, salida de las 47 pruebas e historial Git revisado.
- `docs/03_guion_exposicion.md`: apoyo para la explicación oral.
- `docs/Explicacion_de_clases.md`: explicación de las 24 clases, sus conceptos POO y su código completo; también explica los símbolos del UML.
- `main.py` y `src/`: juego y clases.
- `tests/` y `tools/verificar.py`: pruebas de regresión, campaña y combate.
  La verificación completa la campaña con movimientos y disparos reales, sin
  teletransportes ni desactivar enemigos, y genera doce capturas del juego.

Para comprobar el avance después de instalar las dependencias:

```powershell
.venv\Scripts\python.exe tools\verificar.py
```
