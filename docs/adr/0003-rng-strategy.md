# ADR-0003 — Estrategia de aleatoriedad

- **Fecha**: 2026-05-12
- **Estado**: Aceptada

## Contexto

El original usa `RND(1)` global, lo que hace imposible reproducir
partidas. Un juego moderno necesita:

1. Reproducibilidad por seed para tests, demo y bug reports.
2. Calidad estadística suficiente — el shuffle no debe sesgar.
3. Aislamiento: el dominio no puede llamar a `random.random()` a nivel
   global o se rompe la testabilidad.

## Opciones consideradas

1. **`random.Random` global con seed opcional** — fácil pero rompe la
   pureza del dominio y dificulta tests paralelos.
2. **`Rng` Protocol inyectado por construcción** ✓ — explicito, puro,
   testeable, permite `SeededRng` y `SystemRng` intercambiables.
3. **`numpy.random.Generator`** — calidad superior pero añade dependencia
   pesada para un uso trivial.
4. **`secrets`** — innecesariamente fuerte; impide reproducibilidad.

## Decisión

Definir `Rng` como `Protocol` en `domain/ports/rng.py` con dos métodos
(`randint(a, b)`, `shuffle(seq)`). Implementaciones en
`infrastructure/rng/`:

- `SeededRng(seed: int)` — wrapper sobre `random.Random(seed)`.
- `SystemRng()` — wrapper sobre `random.SystemRandom()`.

El CLI expone `--seed`. El modo `--demo` siempre usa `seed=42`.

## Consecuencias

- Toda función de dominio que necesita azar lo recibe por parámetro.
- Los tests pueden crear `SeededRng(seed)` y verificar manos
  específicas.
- Si en v1.1 se cambia el RNG (p. ej. para multijugador online), solo
  hay que añadir una implementación más.
