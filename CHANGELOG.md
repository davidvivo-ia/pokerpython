# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/) y
versionado [SemVer](https://semver.org/).

## [Unreleased]

## [1.0.0] — 2026-05-12 *(WIP)*

Reconstrucción 2026 de POKER (Steve North, 1978) como TUI Textual.

### Preservado del original

- 5-card draw cabeza a cabeza humano vs CPU.
- Stack inicial de $200 por jugador y ante de $5.
- Estructura de mano: reparto → apuesta 1 → descarte → apuesta 2 →
  showdown.
- IA con farol probabilístico que abre la primera ronda.
- Mensaje *easter egg* "I cheat occasionally, but you can't." cuando el
  jugador intenta descartar más de 3 cartas.

### Modernizado

- BASIC con GOTO → Python 3.13 con Clean Architecture en capas.
- `RND(1)` global → puerto `Rng` inyectado (`SeededRng`, `SystemRng`).
- Variables de una letra (`M`, `N`, `P`, `V1`...) → entidades inmutables
  (`Bankroll`, `Pot`, `HandRank`, ...).
- Evaluador de manos `IF`-anidados → tabla ordenada con tipos enum.
- Política de descarte basada solo en rango global → lectura de cartas
  individuales (conserva pares, proyecto de color, escalera abierta).
- Texto plano → TUI Textual con paleta WCAG AA y cartas ASCII.

### Añadido

- Modo `--seed <int>` para reproducir partidas exactas.
- Modo `--demo` determinista (seed 42, script de acciones predefinido)
  para grabar GIFs y servir como test E2E.
- Persistencia local en `${XDG_DATA_HOME}/punto81/save.json`.
- Modo alto contraste y opción `--no-animations`.
- Atajos de teclado completos documentados.

### Licencias creativas tomadas

- Renombrado del binario y la TUI a `PUNTO 81` (ver ADR-0002). El
  repositorio sigue siendo `pokerpython`.
- "Pasar" se introduce con tecla dedicada en vez del literal `.5` del
  original (ver `docs/original_program_analysis.md` §1100).
- La CPU no "hace trampa" en la mecánica — el guiño queda preservado
  como mensaje cuando el jugador comete una infracción de reglas.

### Bugs corregidos

- Shuffle libre de sesgo (Fisher-Yates moderno).
- Evaluación de manos sin intercambio mutuo de buffers entre humano y CPU.
- Política de descarte que lee cartas individuales y no solo el rango
  global.
- Inicialización defensiva del estado de la CPU en la 2.ª ronda
  (`F1=0 THEN F1=1` ya no existe).
