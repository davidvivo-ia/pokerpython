# ADR-0005 — Persistencia local

- **Fecha**: 2026-05-12
- **Estado**: Aceptada

## Contexto

El original no persiste nada — al cerrar BASIC, se pierde la partida.
Una versión 2026 necesita poder reanudar al menos la partida en curso
y recordar el stack del jugador.

## Opciones consideradas

1. **SQLite** — sobreingeniería para guardar 200 bytes de estado.
2. **JSON sobre XDG_DATA_HOME** ✓ — simple, inspeccionable, portable.
3. **No persistir** — pérdida de calidad de experiencia.
4. **TOML** — válido pero menos natural para anidación.

## Decisión

Persistencia en `${XDG_DATA_HOME:-$HOME/.local/share}/punto81/save.json`.
Validación con pydantic. Una sola partida guardada a la vez en v1.0
(rotación implícita); en v1.1 considerar slots.

## Consecuencias

- El SO Windows usa `%LOCALAPPDATA%\punto81\save.json` — la utilidad
  `platformdirs` lo resuelve sin código condicional.
- Si el JSON es corrupto, la partida arranca desde cero y se logea
  con `structlog`.
- Migraciones de versión: el JSON lleva un campo `schema_version`.
