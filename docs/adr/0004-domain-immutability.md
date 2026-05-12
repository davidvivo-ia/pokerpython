# ADR-0004 — Inmutabilidad del modelo de dominio

- **Fecha**: 2026-05-12
- **Estado**: Aceptada

## Contexto

El original muta `B()`, `C()`, `P`, `M`, `N` libremente. En 2026 esto
es una fuente garantizada de bugs: estado oculto, aliasing, dificultad
para testar transiciones.

## Opciones consideradas

1. **Clases mutables con setters** — familiar pero contraindicado.
2. **`@dataclass(frozen=True, slots=True)` + métodos `apply_*`** ✓ —
   inmutable, tipado, eficiente en memoria, comparable.
3. **`pydantic.BaseModel` para todo** — fuerza validación que el
   dominio no necesita (los IO ya validan en la frontera).
4. **`attrs`** — equivalente funcional al 2 sin diferencia práctica.

## Decisión

Toda entidad de dominio es `@dataclass(frozen=True, slots=True)`. Las
transiciones son métodos puros que devuelven una nueva instancia. Los
modelos con IO (configuración, save files) usan `pydantic.BaseModel`
en `infrastructure/`.

## Consecuencias

- El compilador (mypy strict) detecta intentos de mutación.
- Los tests no necesitan `deepcopy` defensivo.
- Hay que escribir helpers `with_replaced(...)` cuando se cambian
  campos individuales. Aceptable.
