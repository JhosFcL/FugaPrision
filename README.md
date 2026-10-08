# Fuga de la Prisión

Entregable parcial de Programación Orientada a Objetos, ciclo 2026-2. Tema 13, Python. Entrega: **16 de octubre de 2026**. Versión 0.1, comprobada el 8 de octubre.

## Integrantes

- JOSE FERNANDO CHAVEZ LOZANO
- MICKELE CARLOS TORRES VELAZCO
- RICHARD AARON SORIANO CORDOVA
- PIERO CEMEI ROMERO MEZA

## Qué incluye

- [Informe en PDF](entrega/Informe_Parcial_Fuga_Prision.pdf) y [Word editable](entrega/Informe_Parcial_Fuga_Prision.docx).
- Prototipo con un nivel, vigilancia, llave, salida, puntuación, pausa, reinicio y carrera temporal.
- UML y evidencias en `docs/`.
- [Guion de exposición](docs/03_guion_exposicion.md).
- 20 pruebas automatizadas y capturas de los estados.
- Git local; el paquete distribuible añade `historial_git.bundle` para recuperar el historial.

La propuesta inicial permanece en `docs/01_planificacion_y_documentacion.md` como antecedente. El estado vigente se describe en el informe parcial; se implementó también la carrera que inicialmente figuraba como ampliación.

## Ejecutar en Windows

Entorno validado: Python 3.12.14 y Pygame 2.6.1. Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Si es necesario, reemplazar el primer `python` por `py -3.12`. La instalación de Pygame necesita Internet; jugar no lo necesita. No copiar el entorno `.venv` de otra computadora.

En macOS o Linux se utilizan los mismos archivos; los ejecutables del entorno están en `.venv/bin/` en lugar de `.venv/Scripts/`. Estas plataformas no se han comprobado en esta entrega.

## Controles

| Control | Acción |
|---|---|
| WASD o flechas | Mover al prisionero |
| Shift | Correr durante 2 s; recarga de 5 s |
| P o Escape | Pausar o reanudar |
| R | Reiniciar después de perder o ganar |
| Cerrar ventana | Salir |

Recoge la llave para conseguir 100 puntos y desbloquear la salida. Completar el pabellón suma 500 más. Los conos muestran vigilancia; un muro bloquea la visión. El contacto con el guardia también provoca derrota. Si detección y salida coinciden, prevalece derrota.

## Verificar

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools\verificar.py
```

La primera orden prueba reglas sin ventana. La segunda también comprueba eventos Pygame y regenera cuatro capturas, `docs/evidencias/pruebas.txt` y `resultados.json`. Resultado al corte: **20/20**, sin fallos; ruta completa de 872 actualizaciones y 600 puntos. Las capturas usan SDL sin ventana y fueron inspeccionadas. Falta el ensayo humano con teclado en el equipo de exposición.

## Dónde explicar POO

- Herencia, abstracción y polimorfismo: `src/personajes.py` y el bucle de `Nivel.actualizar()`.
- Composición: `Nivel` crea sus elementos; `Prisionero` crea su `HabilidadCarrera`.
- Dependencia: `PuertaSalida.puede_salir(prisionero)` consulta su parámetro.
- Encapsulamiento: `Puntaje.sumar()` valida valores; `Personaje.mover()` controla colisiones.
- State: `src/estados.py` y la delegación de `Juego`.
- Observer: `src/puntuacion.py`, con suscripción del panel en `Juego`.

## Alcance y pendientes

Este es un **avance parcial de un nivel**. Quedan para el final los niveles adicionales y su progresión. La API no está implementada: el PDF la titula sugerencia pero su cuerpo dice debe; confirmar con el docente. La consigna tampoco fija los entregables concretos del parcial. Confirmar sección, docente y criterios de esa entrega antes de presentar.

## Historial y edición del informe

El ZIP contiene código legible y un Git bundle. Para recuperar el historial en otra carpeta:

```powershell
git clone entrega/historial_git.bundle Fuga_con_historial
```

El informe Word es editable. `tools/crear_informe.py` genera el documento y los diagramas; es una herramienta de autoría para Windows y requiere `python-docx`, `Pillow` y fuentes Arial. No se necesita para jugar. `tools/exportar_word.ps1` exporta el DOCX usando Microsoft Word. Esas dependencias de autoría se mantienen separadas del juego.

Los gráficos del juego y diagramas se generan mediante código propio. Referencias técnicas: [Pygame](https://www.pygame.org/docs/) y [clases abstractas de Python](https://docs.python.org/3/library/abc.html). La consigna es el PDF proporcionado para el curso.
