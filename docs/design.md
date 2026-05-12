# Sistema de diseño — *Punto 81*

## Concepto

> Un casino clandestino de 1981 visto a través de un terminal vectorial:
> tipografía monoespaciada nítida, pocos colores muy precisos, brillo de
> fósforo apenas insinuado.

Fusión moderna-retro: estructura Textual contemporánea con afecto
visual por las pantallas P3/P4 de los terminales de la época.
Sin scanlines abusivas, sin emojis. El guiño retro está en la paleta,
las cartas dibujadas en ASCII enmarcado y un titular que late.

## Paleta

| Token       | Hex        | Rol semántico                            |
|-------------|------------|-------------------------------------------|
| `--bg`      | `#0B0F0A`  | Fondo principal: verde tan oscuro que pasa por negro. |
| `--surface` | `#0F1410`  | Superficies elevadas (panel, modal).      |
| `--muted`   | `#3E5147`  | Bordes y separadores.                     |
| `--ink`     | `#C9D7CC`  | Texto principal.                          |
| `--accent`  | `#E8C547`  | Acento principal: fichas, foco, totales.  |
| `--primary` | `#5FB85F`  | Verde fósforo: acciones positivas, CTA.   |
| `--success` | `#7DDE7C`  | Mano ganadora.                            |
| `--warning` | `#E59F46`  | Apuestas dudosas, advertencias.           |
| `--error`   | `#D9534F`  | Mano perdedora, fold, errores.            |
| `--card-red`| `#E25C5C`  | Palos rojos (corazones, diamantes).       |
| `--card-blk`| `#DCE5DE`  | Palos negros (picas, tréboles).           |

Contraste verificado WCAG AA sobre `--bg` para `--ink` (10.4:1) y
`--accent` (10.1:1).

## Tipografía

- **UI**: tipografía mono del sistema. Textual respeta `font-family` a
  través del terminal del usuario; recomendamos *JetBrains Mono* o
  *Iosevka Term* (no se empaqueta — es responsabilidad del terminal).
- **Display**: el título `PUNTO 81` se compone con `pyfiglet`-like ASCII
  hecho a mano, en `assets/title.txt`.
- **Tamaños**: el TUI usa una unidad — la celda del terminal. No hay
  px. La densidad se gestiona con espaciado.

## Espaciado

Sistema de 1 celda mono ≈ 1 unidad. Margen vertical entre bloques: 1.
Padding interno de paneles: 1 horizontal, 1 vertical. Separación
entre cartas: 2 columnas.

## Iconografía

Sin glifos Nerd Font (no asumibles en todos los terminales). Solo:

- Palos como caracteres Unicode `♠ ♥ ♦ ♣`.
- Fichas como bloques `■` con color `--accent`.
- Estados de turno con flecha `▶`.
- Selección de descarte con `▣` / `□`.

## Cartas — anatomía

Cada carta ocupa 11 × 7 celdas con marco redondo:

```
╭─────────╮
│A        │
│         │
│    ♠    │
│         │
│        A│
╰─────────╯
```

- Anverso: rango en esquinas, palo grande centrado, color rojo/negro
  según palo.
- Reverso: patrón uniforme `╳` sobre `--surface`, marco `--muted`.
- Estado seleccionado para descarte: borde `--accent` y un `▣` debajo.

## Estados clave

| Estado       | Composición                                                                  |
|--------------|------------------------------------------------------------------------------|
| **Splash**   | Logo ASCII centrado, parpadeo lento de un `_` cursor, pulsar tecla para entrar. |
| **Mesa**     | Mano CPU arriba (oculta), bote y stacks en el centro, mano humana abajo.     |
| **Apuesta**  | Modal in-place sobre la zona de jugador: input + chips visuales.             |
| **Descarte** | Mano humana con índices `[1]..[5]`; espacio = togglear; enter = confirmar.   |
| **Showdown** | Ambas manos descubiertas; resultado en banner; bote viaja al ganador.        |
| **Game Over**| Recuento final, opción de revancha o salida.                                 |
| **Vacío**    | Si no hay partida guardada: invitación clara a empezar.                      |
| **Error**    | Toast bajo, color `--error`, autodismiss 3s.                                 |

## Accesibilidad

- Navegación completa por teclado documentada en `README`.
- Daltonismo: los palos rojos nunca son la única señal — siempre hay
  glifo `♥`/`♦`.
- Modo alto contraste: variante `tcss/highcontrast.tcss` activada con
  `--theme=hc` o tecla `C`.
- No depender solo de color para ganador/perdedor: hay etiqueta textual
  ("GANAS" / "PIERDES") y posición.
- Animaciones desactivables con `--no-animations` para terminales
  lentos / accesibilidad vestibular.

## Toque distintivo memorable

**El bote palpita.** Cuando el bote crece tras una subida, el número
acumulado parpadea una vez en `--accent` y se anima desde el monto
anterior al nuevo (interpolación en 200 ms). Mientras una mano está en
juego, el contador del bote tiene un latido sutil de 1.2 s
(`opacity 1.0 → 0.85 → 1.0`). Es el único elemento animado salvo el
cursor: queda como ancla visual.

## Bindings de teclado

| Tecla        | Acción                                |
|--------------|---------------------------------------|
| `Enter`      | Confirmar acción / continuar          |
| `Espacio`    | Togglear selección de descarte        |
| `1`..`5`     | Seleccionar carta por índice          |
| `b`          | Apostar (open input)                  |
| `c`          | Pasar (check)                         |
| `f`          | Retirarse (fold)                      |
| `r`          | Subir (raise)                         |
| `q`          | Salir                                 |
| `?`          | Ayuda                                 |
| `Ctrl+s`     | Guardar partida                       |
| `Ctrl+l`     | Cargar partida                        |
| `C`          | Alternar modo alto contraste          |

## Audio

Opcional, off por defecto. Si está disponible `numpy` y el SO permite
audio, se generan blips estilo PC-speaker en eventos clave (apuesta,
reparto, victoria). El usuario activa con `--sound`. En v1.0 esto se
deja como stub documentado y se mueve a v1.1 si el entorno no
coopera (ver `TODO.md`).
