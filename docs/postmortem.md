# Postmortem — *Punto 81* v1.0

Una semana de 2026 reconstruyendo un POKER de 1978.

## Qué se ganó

El dominio quedó tan limpio que sería trivial añadirle un segundo
oponente o una variante (*stud*, *omaha cerrado*) sin tocar la
presentación. La inyección del RNG abre el modo `--demo`, los tests
deterministas y abre la puerta a tournaments reproducibles. Los tipos
estrictos atraparon una decena de bugs antes de la primera ejecución
y el evaluador testeado con *hypothesis* sobre el espacio de manos da
una confianza que el original no podía dar.

## Qué se perdió

La intimidad. El POKER original cabía en una sola pantalla: 250 líneas
con todo dentro, y un adolescente con una semana libre podía entenderlo
de cabo a rabo. Aquí hay capas, ADRs, *protocols* y un sistema de
diseño. La curva para llegar al *evaluator* desde un `git clone` es más
larga, aunque el viaje sea más placentero.

También se pierde la sorpresa de los bugs. El original tenía un
shuffle imperfecto y una IA que ocasionalmente "hacía trampa"; cada
partida tenía su pequeña anomalía. La versión 2026 es predecible,
auditable y, por eso mismo, un poco menos viva.

## Qué dice el ejercicio

En cuarenta años el oficio cambió de programar contra una máquina a
programar contra la entropía de un sistema. Steve North necesitaba
conocer su BASIC, su microprocesador y poco más. Aquí necesitamos
ergonomía de tipos, dependencias, accesibilidad, CI, persistencia
portable, y aun así apenas hemos arañado lo que un juego comercial
moderno pide. Hemos ganado fiabilidad y disciplina a cambio de
cercanía. El programa de 1978 *era* el código; el de 2026 está en
algún lugar entre el código, la arquitectura, los ADRs y la batería
de tests. Ninguno de los dos es mejor — son herramientas distintas
para audiencias distintas, separadas por cuatro décadas de oficio
acumulado.
