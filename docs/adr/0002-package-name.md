# ADR-0002 — Nombre del paquete

- **Fecha**: 2026-05-12
- **Estado**: Aceptada

## Contexto

El repositorio se llama `pokerpython`, que es descriptivo pero
genérico. El paquete Python necesita un identificador corto, válido
como módulo, y con cierta personalidad para el branding de la TUI.

## Opciones consideradas

1. `pokerpython` — demasiado genérico, no le da carácter al producto.
2. `pyker` — juego de palabras evidente pero ya usado en PyPI.
3. `punto81` — eco al año del original (1978-1981) y al juego "Punto
   y banca"; corto, distintivo, registrable, válido como módulo.
4. `casino78` — informativo pero fechado y poco evocador.

## Decisión

**`punto81`**. El comando, el paquete y el branding usan el mismo
identificador. El repo se queda como `pokerpython` por compatibilidad.

## Consecuencias

- `pyproject.toml` declara `name = "punto81"` y `script = "punto81 =
  punto81.__main__:app"`.
- La TUI se titula `PUNTO 81` con el separador visible.
- README explica la procedencia del nombre.
