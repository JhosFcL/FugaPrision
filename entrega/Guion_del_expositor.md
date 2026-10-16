# Guion de exposición — Fuga de la Prisión

Presentación de 16 diapositivas: 14 principales y 2 anexos. Duración de exposición sugerida: 8–10 minutos, con una demostración breve. Las dos últimas diapositivas se usan solo si hay preguntas.

El reparto de voces es una propuesta de ensayo. No atribuye autoría del código ni sustituye la evidencia de los aportes reales de cada integrante.

## Antes de exponer

- Abrir el PPTX y ensayar con las notas del presentador. El PDF es una copia visual de respaldo.
- Probar el juego con ventana en la computadora de exposición. Desde el repositorio: `.venv/bin/python main.py` en Linux o `.venv\Scripts\python.exe main.py` en Windows, con las dependencias instaladas.
- Preparar los aportes reales de cada integrante con cambios o commits que pueda explicar. El historial actual tiene 14 commits, pero tres nombres de autor configurados no identifican por sí solos el trabajo de cuatro personas.
- Mantener a mano las capturas y el UML original. No intentar completar toda la campaña en directo.

## Reparto sugerido

- Jose Fernando: diapositivas 1–3.
- Mickele Carlos: diapositivas 4–7.
- Richard Aaron: diapositivas 8–9.
- Piero Cemei: diapositivas 10–13.
- Cierre y preguntas: todo el equipo.

## 01. Presentación

**Voz sugerida:** Jose Fernando. **Tiempo:** 20 s.

Presentar a los cuatro integrantes y el nombre del proyecto. Abrir con una frase: «Nuestro reto fue convertir un escape de prisión en objetos que colaboran: personajes, mapa, estados y puntaje». El foco de la exposición será mostrar una regla del juego y la decisión de diseño que la sostiene. No leer todos los nombres ni explicar todavía el UML.

## 02. Objetivo y reglas

**Voz sugerida:** Jose Fernando. **Tiempo:** 35 s.

Explicar el objetivo académico: demostrar los fundamentos de POO y patrones mediante un juego funcional. En la captura, señalar al prisionero verde, la llave amarilla, las patrullas rojas y la salida. El prisionero comienza encerrado. Ver u oír al jugador inicia una respuesta de los guardias; la captura se produce por contacto. Las cámaras alertan a las patrullas, no provocan una derrota instantánea.

## 03. Campaña

**Voz sugerida:** Jose Fernando. **Tiempo:** 30 s.

Recorrer las cuatro capturas sin describir todos los obstáculos. Los tres primeros mapas trabajan el sigilo; la arena introduce combate. Destacar que el Patio cambia al recoger la llave porque se abren atajos en el mismo mapa usado para colisiones y caminos. El puntaje se conserva entre niveles: 400 de llaves, 2000 de salidas y 1000 del jefe, total 3400. Al reintentar un nivel se restauran los puntos que había al entrar en él.

## 04. Arquitectura

**Voz sugerida:** Mickele Carlos. **Tiempo:** 45 s.

Este es un recorte del UML, no la lista completa. Explicar primero Juego: mantiene la campaña y delega en un estado. Nivel coordina los componentes de cada mapa y recibe el Puntaje compartido. Combate existe solo en la arena. Vista consume los datos del juego para dibujar. El rombo negro de Juego a Nivel indica creación y composición; el rombo blanco de Nivel a Puntaje señala que Nivel recibe el objeto creado por Juego. La flecha discontinua de Vista representa una dependencia de uso. El UML íntegro de 25 clases queda en el anexo. Hablar de responsabilidades, no memorizar todos los atributos.

## 05. Asociación, agregación y composición

**Voz sugerida:** Mickele Carlos. **Tiempo:** 40 s.

Mostrar tres ejemplos reales. Asociación: Personaje conserva la referencia a su Nivel y consulta sus reglas de colisión. Agregación: cada Nivel recibe Puntaje; Juego conserva ese mismo objeto al cambiar de nivel. Composición: Nivel construye Mapa con su plano. En el diseño, el mapa es una parte del nivel. Los rombos se colocan del lado del objeto que contiene la parte. No afirmar que Python destruye automáticamente una parte en el mismo instante: los ejemplos explican responsabilidad y ciclo de vida en el diseño. Otros ejemplos de composición son Prisionero con HabilidadCarrera y Combate con Alcaide.

## 06. Herencia y polimorfismo

**Voz sugerida:** Mickele Carlos. **Tiempo:** 40 s.

Personaje es una clase abstracta y reúne posición y movimiento. Prisionero y Guardia heredan esos elementos e implementan update. El fragmento pertenece a Nivel.actualizar, invocado desde el bucle del juego por el estado Jugando. La llamada no pregunta qué tipo de personaje tiene delante: cada objeto resuelve su propia implementación. Distinguir herencia, que define la jerarquía, de polimorfismo, que permite usar una operación común. El triángulo vacío apunta a Personaje, la base.

## 07. Encapsulamiento y abstracción

**Voz sugerida:** Mickele Carlos. **Tiempo:** 35 s.

Leer solo la condición que rechaza datos inválidos y el llamado a _notificar. _valor es un atributo interno por convención; el guion bajo no impide físicamente el acceso en Python. Los métodos públicos controlan las operaciones válidas y evitan que la regla se repita en todos los consumidores. El getter permite consultar el valor. Conectar con abstracción: el resto del juego puede pedir sumar puntos sin conocer la lista interna de observadores. También Personaje y EstadoJuego definen contratos abstractos.

## 08. Patrón State

**Voz sugerida:** Richard Aaron. **Tiempo:** 40 s.

La caja de EstadoJuego indica la interfaz común; las otras cinco cajas son sus estados concretos. El esquema muestra transiciones de ejecución y no sustituye el diagrama de herencia. Jugando actualiza Nivel y examina el resultado. Pausa tiene una actualización vacía, por lo que el tiempo y las reglas de la simulación quedan detenidos. P o Escape alterna Jugando y Pausa. Enter después de NivelCompletado carga el siguiente nivel; R desde Derrota reintenta el nivel; R desde Victoria inicia otra campaña. La pérdida de foco también pausa. La ausencia de avance durante la pausa se comprueba en las pruebas.

## 09. Patrón Observer

**Voz sugerida:** Richard Aaron. **Tiempo:** 35 s.

Recorrer el caso de una llave. Nivel llama a Puntaje.sumar(100). Puntaje valida el cambio y recorre sus observadores para llamar a actualizar_puntaje. PanelPuntaje implementa esa operación y guarda el nuevo valor. Vista lee panel.valor y lo dibuja. El fragmento de suscripción está en Juego.__init__. Puntaje no necesita conocer las operaciones gráficas de Pygame. SistemaRuido emplea una comunicación semejante con sus guardias oyentes, pero el ejemplo formal de Observer es el sistema del puntaje.

## 10. Combate contra el Alcaide

**Voz sugerida:** Piero Cemei. **Tiempo:** 35 s.

La primera columna representa la fase y las coronas cuentan todos los proyectiles de ese patrón: 12, 40 y 84. La espera de la tabla es la que queda tras ejecutar el ataque; no es el tiempo de toda la secuencia. Además existen ráfagas dirigidas y embestidas. Cada cambio de capa retira proyectiles y se anuncia durante 1,1 segundos. Combate y Alcaide separan las reglas de ataque de la coordinación general de Nivel. Solo tras derrotarlo se conceden 1000 puntos y se habilita la llave; luego hay que recogerla y llegar a la salida.

## 11. Evidencia de funcionamiento

**Voz sugerida:** Piero Cemei. **Tiempo:** 35 s.

Durante la preparación del entorno se ejecutó tools/verificar.py en una copia temporal para no sobrescribir evidencias versionadas. Pasaron las 54 pruebas, se completaron los cuatro niveles y se generaron 14 capturas. El verificador usa movimiento y disparos del juego, sin teletransportar al jugador ni desactivar enemigos para completar la campaña. La derrota forzada posterior solo comprueba ese estado. La campaña termina con 3400 puntos. La validación automática fue sin ventana; también se comprobó el arranque del bucle de main.py y cierre por QUIT. Eso no reemplaza el ensayo con teclado del equipo.

## 12. Uso de Git y trabajo en equipo

**Voz sugerida:** Piero Cemei. **Tiempo:** 25 s.

El historial actual contiene 14 commits. El PDF técnico conserva una revisión anterior hasta 8eed979 con 13 commits; esta diapositiva refleja el HEAD 56f629f. Se observan tres nombres de autor configurados: JhosFcL con 12 commits, Simei con uno y shzjeud con uno. No se puede deducir de esos nombres la contribución de los cuatro integrantes. Antes de exponer, cada integrante debe preparar un cambio o commit que pueda explicar de forma veraz. El reparto de voces de estas notas es una propuesta de ensayo, no una atribución de trabajo. No afirmar que hay ramas, PR o revisiones de equipo si no se cuenta con evidencia.

## 13. Demostración breve

**Voz sugerida:** Piero Cemei. **Tiempo:** 60 s.

Reservar aproximadamente un minuto y ensayar el orden. Abrir main.py en la computadora con pantalla. Mantener E cerca de los barrotes y mostrar cómo se abre la celda. Empujar un muro para demostrar la colisión. Moverse con Ctrl y comparar con Shift sin prometer que una misma acción siempre evita toda captura. Pausar con P y volver con Escape: las patrullas no deben avanzar mientras está pausado. Si capturan al jugador, R restaura el nivel completo. No intentar completar toda la campaña en directo si eso consume el tiempo. Las capturas de las diapositivas 3 y 10 sirven como respaldo. En la nube la validación se hizo sin ventana, así que la demostración interactiva requiere el equipo de exposición.

## 14. Cierre

**Voz sugerida:** Equipo. **Tiempo:** 25 s.

Cerrar con la dificultad principal: hacer que puertas, paredes, sonido y rutas consulten un modelo coherente del mapa. El aprendizaje fue separar responsabilidades para poder probarlas. Recordar que la campaña y las pruebas son evidencia funcional, y que la defensa oral debe conectar cada concepto con una decisión concreta del código. Agradecer y abrir preguntas. Si preguntan por el porcentaje del parcial, la rúbrica pide demostrar un avance del 25 % pero no define una fórmula: describir las funciones que ya se pueden ejecutar sin inventar un porcentaje.

## 15. UML de consulta

**Anexo de consulta; fuera del tiempo principal.**

Anexo, fuera de los 8–10 minutos. La imagen completa queda incrustada en el PPT para ampliar durante las preguntas; no intentar leerla entera desde la proyección. Las diapositivas 4 a 9 ya presentan relaciones concretas con tamaño legible. Conservar el PNG original como recurso adicional si se necesita mayor ampliación. El modelo íntegro reúne las 25 clases; no incluye clases de los tests. El # refleja convención de uso interno en Python, no una restricción de acceso impuesta por el lenguaje.

## 16. Preguntas y controles

**Anexo de consulta; fuera del tiempo principal.**

Anexo, fuera del tiempo principal. Otras respuestas: si coinciden captura y salida, la derrota tiene prioridad. R tras perder reintenta el nivel con los puntos de entrada; N inicia una campaña desde cero. En la arena, Espacio apunta automáticamente al jefe e IJKL fija la dirección. Una misma tecla puede tener acciones diferentes según State. Las pruebas automáticas validan reglas; el ensayo con teclado valida que el equipo pueda presentar el juego con soltura. Fuentes: código del checkout main, README, informe parcial, rúbrica adjunta y verificador ejecutado durante la configuración del entorno.

## Fuentes y alcance

- Repositorio `JhosFcL/FugaPrision`, rama `main`, HEAD `56f629f`.
- `entrega/Informe_Parcial_Fuga_Prision.pdf`, `README.md`, código `src/` y `main.py`.
- Rúbrica y estructura del proyecto parcial adjuntada por el usuario.
- 54 pruebas y campaña completa verificadas en el entorno de nube el 16 de octubre de 2026. Las capturas incluidas son evidencias del repositorio.
- El contenido describe la implementación comprobada; no garantiza una nota ni presume aportes individuales.