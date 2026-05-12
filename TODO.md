# TODO — v1.1 y más allá

Pendientes priorizados que no caben en v1.0 pero quedan a tiro:

## Alta

1. **Slots múltiples de partida guardada** y selector visual en splash.
2. **Estadísticas históricas**: manos jugadas, balance neto, mano máxima
   conseguida — persistidas junto al save.
3. **Audio sintetizado opcional** (PC-speaker blips con numpy). En v1.0
   queda como stub off por defecto.

## Media

4. **Multi-mesa**: posibilidad de hasta 4 oponentes con personalidades
   distintas (tight / loose / aggressive).
5. **Tema claro** además de los dos oscuros existentes (default, alto
   contraste).
6. **Export de partida a SVG** desde Textual `--export` para crear gifs
   reproducibles.

## Limitaciones conocidas v1.0

- El modo audio está stubbed (no toca alguna nota). Documentado en
  ADR y CHANGELOG.
- Snapshot tests de Textual están en *best effort*: cubren las tres
  pantallas principales pero no todos los estados.
- Solo un slot de partida guardada (rotación implícita).
