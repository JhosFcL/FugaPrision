# Fuga de la Prisión — La última fuga

Juego 2D en Python y Pygame con una campaña de cuatro niveles. Los tres primeros
combinan sigilo, llaves, patrullas y cámaras; el último es una arena contra un jefe
original inspirado en los patrones de proyectiles de The Binding of Isaac.

## Campaña

1. **Pabellón de celdas:** empiezas encerrado. Acércate a los barrotes y mantén E durante dos segundos para forzar la puerta; después busca la llave evitando dos patrullas y una cámara.
2. **Lavandería:** un mapa nuevo con coberturas, dos patrullas y dos cámaras.
3. **Patio de vigilancia:** tres galerías horizontales, tres patrullas y tres cámaras. La llave del ala norte abre atajos para volver a la salida; el recorrido cambia tras recogerla.
4. **El Alcaide:** cinco puntos de vida para enfrentarte al jefe. Lanza coronas de
   lágrimas, ráfagas dirigidas y embestidas que avisa antes de atacar. Al agotar
   una capa de vida comienza una fase mucho más intensa. Tiene tres capas de 72 puntos: las coronas pasan de 12 a 40 y a 84 proyectiles; estos aceleran y las esperas se reducen. Los cambios de capa se anuncian durante 1,1 segundos. Derrótalo, recoge la
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
| Forzar la puerta de la celda inicial | Mantener E cerca de los barrotes durante 2 s |
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
que escuchan; si te ven o una cámara les avisa, te persiguen rodeando las paredes. Las cámaras están ancladas a las paredes y la alarma alerta a todos los guardias; no provoca derrota instantánea.
Solo te capturan al alcanzarte. Si rompes la visión, buscan en la última posición
conocida y después regresan a patrullar. `?` indica investigación o búsqueda y
`!` indica persecución. La interfaz muestra el ruido y la alerta actual.

Los planos tienen perímetro cerrado y divisiones con pasos definidos, sin huecos
aislados ni una ruta libre alrededor de todo el borde. Las colisiones recortan el
movimiento ante la primera pared, incluso en diagonal o con un desplazamiento grande.

## Material del parcial

- `entrega/Informe_Parcial_Fuga_Prision.pdf`: informe para presentar.
- `docs/diagramas/modelo_parcial.mmd` y `modelo_parcial.png`: UML de las 25 clases del juego, en Mermaid y como imagen generada desde el mismo modelo.
- `docs/evidencias/`: catorce capturas de la campaña, salida de las 54 pruebas e historial Git revisado.
- `docs/03_guion_exposicion.md`: apoyo para la explicación oral.
- `docs/Explicacion_de_clases.md`: explicación de las 25 clases, sus conceptos POO y su código completo; también explica los símbolos del UML.
- `main.py` y `src/`: juego y clases.
- `tests/` y `tools/verificar.py`: pruebas de regresión, campaña y combate.
  La verificación completa la campaña con movimientos y disparos reales, sin
  teletransportes ni desactivar enemigos, y genera catorce capturas del juego.

Para comprobar el avance después de instalar las dependencias:

```powershell
.venv\Scripts\python.exe tools\verificar.py
```
