# Análisis del programa original

## Encuadre

| Campo               | Valor                                                              |
|---------------------|--------------------------------------------------------------------|
| Nombre              | POKER                                                              |
| Autor               | Steve North                                                        |
| Publicación         | *BASIC Computer Games*, David H. Ahl (ed.), Creative Computing, 1978 |
| Lenguaje            | BASIC (Microsoft / Dartmouth genérico, 8 bits)                    |
| Plataforma típica   | Altair 8800, TRS-80 Mod I, Apple ][, Commodore PET / VIC-20       |
| Memoria asumida     | 8 KB de RAM (cabe holgado)                                         |
| Modo de interacción | Teletipo / terminal de 40 u 80 columnas, texto puro                |
| Año                 | 1978 (recopilación) — desarrollos previos en revistas 1973-1977    |
| Líneas              | ~250 (en esta reconstrucción)                                      |

## Sinopsis funcional

El jugador humano y la computadora son los dos únicos participantes en
partidas sucesivas de **5-card draw**:

1. Cada jugador empieza con **$200** [DATO].
2. Ronda tras ronda:
   1. **Antes** obligatorio de $5 por jugador.
   2. Reparto de 5 cartas a cada uno; la mano del humano se muestra
      ordenada de menor a mayor.
   3. **Primera ronda de apuestas** abierta por la computadora.
   4. **Fase de descarte**: humano puede descartar 0-3 cartas
      [DATO]; computadora descarta según una heurística basada en la
      fuerza de su mano pre-descarte.
   5. **Segunda ronda de apuestas** abierta por el humano (con la opción
      de *check* introduciendo `.5`).
   6. **Showdown**: se comparan manos y se reparte el bote.
3. Termina cuando uno de los dos se queda a cero.

## Lectura crítica

POKER es uno de los primeros programas de cartas con una IA que
**farolea** de manera no determinista. Su mérito principal no es el
evaluador (correcto pero rígido) sino la **caracterización del oponente**:
apuesta con cierta variabilidad, ocasionalmente sube manos débiles, se
retira ante subidas grandes si lleva basura.

Sus debilidades son las propias de la época:

- **UI textual mínima**: cartas escritas como `"ACE OF SPADES"`, sin
  agrupación visual.
- **Modelo monolítico**: lógica de juego, IO y RNG entrelazados con
  `GOTO`.
- **Variables crípticas de una letra** (M, N, P, V1, V2, K1, Z9...).
- **Sesgos en RNG**: la baraja se mezcla con un shuffle de Fisher-Yates
  rudimentario que en muchos dialectos BASIC tenía un `RND(1)` con
  período pobre — distribución no uniforme en estricto rigor.
- **IA que "hace trampa" ocasionalmente**: el comentario `"I CHEAT
  OCCASIONALLY, BUT YOU CAN'T."` ante un descarte ilegal del jugador
  delata cierto humor a costa de las reglas. Se preserva el guiño en
  la versión 2026 como easter egg, no como mecánica.

## Grafo de flujo (ASCII)

```
                  +----------------------+
                  |  INTRO / SALUDO      |
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | ¿M<=0 o N<=0?        |---> FIN PARTIDA
                  +----------+-----------+
                             | no
                             v
                  +----------+-----------+
                  | ANTE 5/5  P=P+10     |
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | SHUFFLE  (3000 loop) |
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | DEAL B[1..5] C[1..5] |
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | SORT C   GOSUB 3000  |
                  | SHOW C   GOSUB 3200  |
                  | EVAL C   GOSUB 3500  |--> V1, K1
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | CPU OPEN GOSUB 4000  |--> X
                  | print "I'LL OPEN..." |
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | INPUT Y              |
                  | Y=0 -> FOLD          |--> 2200
                  | Y>X -> RAISE         |--> 650
                  | Y=X -> CALL          |--> 700
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | DRAW: human Z cards  |
                  |       cpu Z9 cards   |
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | EVAL again -> V2,K1  |
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | HUMAN OPENS 2nd RND  |
                  |   .5 -> CHECK        |
                  |   0  -> FOLD  -> 2200|
                  |   y  -> CPU RESP 4800|
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | SHOWDOWN: compare V,K|
                  | reparte bote -> 2000 |
                  |               -> 2100|
                  |               -> 1400|
                  +----------+-----------+
                             |
                             v
                  +-- loop a 260 --+
```

## Inventario de variables

| Variable    | Tipo   | Uso                                                             |
|-------------|--------|-----------------------------------------------------------------|
| `A(52)`     | int[]  | Baraja barajada (índices de carta 1..52).                       |
| `B(5)`      | int[]  | Mano de la computadora.                                         |
| `C(5)`      | int[]  | Mano del humano.                                                |
| `D(5)/E(5)` | int[]  | Auxiliares de evaluación (rango y palo).                        |
| `K`         | int    | Posición actual en la baraja al servir.                         |
| `M`         | int    | Stake (dinero) de la computadora.                               |
| `N`         | int    | Stake del humano.                                               |
| `P`         | int    | Bote acumulado.                                                 |
| `X`         | int    | Apuesta abierta por la CPU.                                     |
| `Y`         | int    | Apuesta del humano.                                             |
| `Z`         | int    | Cartas que el humano descarta (0..3).                           |
| `Z9`        | int    | Cartas que la CPU descarta (0..3).                              |
| `V/V1/V2`   | int    | Rango de mano (1=carta alta, 9=escalera color).                 |
| `K1/KC/KP`  | int    | Carta alta de desempate.                                        |
| `P1,P2`     | int    | Rangos de las dos parejas detectadas.                           |
| `T3,Q1`     | int    | Rango de trío y póker detectados.                               |
| `FL,ST`     | int    | Flags: color, escalera.                                         |
| `I1`        | int    | Apuesta inicial calculada por la CPU.                           |
| `R2`        | int    | Subida (raise) de la CPU.                                       |
| `F1`        | int    | Decisión CPU 2.ª ronda: 1=fold, 2=call, 3=raise.                |
| `S$, U$`    | str    | Buffers de nombre de carta (rango y palo).                      |

## Inventario de subrutinas (GOSUB)

| Línea | Nombre interno         | Función                                                       |
|------:|------------------------|---------------------------------------------------------------|
| 3000  | SORT-PLAYER-HAND       | Ordena `C()` por rango usando burbuja.                        |
| 3200  | PRINT-HAND             | Imprime `C()` carta por carta.                                |
| 3300  | CARD-NAME              | Calcula `S$, U$` para `C(I)`.                                 |
| 3500  | EVAL-HAND              | Calcula `V`, `K1` de `C()`.                                   |
| 4000  | CPU-OPEN-BET           | Calcula `I1` según `V1`.                                      |
| 4500  | CPU-DRAW-STRATEGY      | Calcula `Z9` y reemplaza `B()`.                               |
| 4800  | CPU-RESPONSE           | Calcula `F1` en la 2.ª ronda según `V2`, `Y`, y un RNG.       |

## IO y dispositivos

- `PRINT` a salida estándar (teletipo o vídeo de texto).
- `INPUT` desde teclado para apuestas (`Y`), descarte (`Z`, `J`), y
  segunda apuesta (`Y2`).
- `RND(1)` como única fuente de aleatoriedad (sin `RANDOMIZE TIMER`
  garantizado en todos los dialectos — en Microsoft BASIC 8 bits el
  `RANDOMIZE` por si solo a veces requería input numérico).
- No hay persistencia entre partidas.

## Algoritmos identificados y nombrados

1. **Fisher-Yates ingenuo** (líneas 340-380): mezcla la baraja
   intercambiando `A(I)` con `A(INT(RND(1)*52)+1)`. La elección de
   índice no excluye `I`, por lo que el sesgo respecto al Fisher-Yates
   estricto es despreciable pero presente.
2. **Burbuja ascendente** (3000-3070): ordena la mano humana antes de
   mostrarla.
3. **Evaluador por conteo de duplicados** (3500-3750): cuenta
   ocurrencias de cada rango en bucle anidado `O(n²)`. Detecta color,
   escalera, póker, full, trío, doble pareja y pareja con `IF`
   anidados — sin tabla.
4. **Política de descarte heurística** (4500-4590): basada en el rango
   pre-descarte (`V1`), descarta 0, 1, 2 o 3 cartas. No mira las cartas
   individuales, solo el rango global, lo que produce decisiones
   subóptimas (p. ej. descarta cualquier cosa con un trío en lugar de
   las dos cartas peores).
5. **Política de respuesta a apuesta** (4800-4900): tabla `IF` con
   ruido controlado por `RND(1)` para introducir farol.

## Bugs y rarezas con número de línea

| Línea       | Bug / Rareza                                                                                                     | Tratamiento 2026         |
|-------------|------------------------------------------------------------------------------------------------------------------|--------------------------|
| 340-380     | Shuffle no es Fisher-Yates estricto: `R` puede ser igual a `I`; el sesgo es leve pero existe.                    | Sustituido por `random.shuffle` sobre RNG inyectado. |
| 1000-1030   | Bloque `IF ... THEN` multilínea en BASIC: muchos dialectos lo parsean mal; en MS-BASIC el `IF F1=2 THEN` ejecuta solo lo de la misma línea. | Reescrito con `match/case` claro. |
| 1100-1130   | Si el humano "no llama" al raise de la CPU, se considera fold pero no se aclara que perderá las fichas ya puestas. | Mensaje explícito en TUI. |
| 1230-1340   | Para evaluar las dos manos se intercambian `B()`/`C()` repetidamente. Funcional pero frágil; un error de paridad rompe el showdown. | Sustituido por evaluación pura sobre cada mano independiente. |
| 3320        | `S1=C(I)-4*(R1-1)` mapea a 1-4 pero el cálculo solo es correcto si `(C(I)-1)` es divisible por 4 al inicio.       | Reescrito como módulo limpio en `Card.from_index`. |
| 3325        | El comentario asume `R1=13` para As pero la rama 3375 está mal indentada respecto a la 3370 (cae fuera del `IF R1=12`); en algunos dialectos imprime ambos. | Tabla `Rank` enum elimina la ambigüedad. |
| 4500-4590   | La CPU sustituye las **primeras** `Z9` cartas de su mano sin mirar cuáles convienen tirar.                       | Política basada en lectura de cartas individuales. |
| 4810-4900   | El bloque tiene un `IF F1=0 THEN F1=1` defensivo que delata que el flujo `IF`/`THEN` no garantiza inicializar `F1`. | Estado de decisión modelado como `enum CpuAction`. |

## Bugs corregidos en la versión 2026

1. Shuffle sin sesgo (Fisher-Yates moderno vía `random.shuffle` con RNG
   inyectado).
2. Evaluador sin mutación cruzada entre manos.
3. Política de descarte que mira cartas concretas: conserva pares
   detectados, conserva proyectos de color/escalera abiertos y altas
   cartas individuales.
4. Manejo robusto de "check" sin reutilizar el valor mágico `0.5`.
5. Mensajes de error legibles en lugar de `"I HAVE FIVE CARDS, NOT N."`.

## Decisiones forzadas por la época preservadas

- **Modo cara a cara contra una sola IA**: se mantiene como modo
  principal.
- **Antes obligatorio y dos rondas de apuestas con check**: idéntico al
  original.
- **Personalidad farolera de la CPU**: se preserva con una política de
  decisión que mezcla fuerza de mano con un parámetro de bluff
  controlado por seed.
- **Mensaje "I CHEAT OCCASIONALLY"**: preservado como easter egg cuando
  el jugador intenta descartar más de 3 cartas.
