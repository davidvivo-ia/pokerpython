# Punto 81

Reconstrucción 2026 del programa **POKER** de Steve North publicado en
*BASIC Computer Games* (David H. Ahl, 1978): un *5-card draw* contra la
computadora, jugado dentro de una TUI Textual con paleta de fósforo y
cartas dibujadas en ASCII.

> El nombre — *Punto 81* — guiña al año en el que esos listados de
> BASIC ya circulaban por hogares con TRS-80, Apple ][ y Commodore PET.
> En el repo original éramos `pokerpython`; en pantalla somos `PUNTO 81`.

## Estado

v1.0.0 — Jugable de principio a fin, TUI con sistema de diseño propio,
modo `--demo` determinista, persistencia local.

## Instalación

Requiere Python 3.13+ y [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo>
cd pokerpython
uv sync
uv run punto81
```

## Uso

```bash
# Modo TUI normal (default)
uv run punto81

# Partida determinista con seed conocida
uv run punto81 --seed 42

# Demo automática (sin intervención humana, para grabar GIF o CI)
uv run punto81 --demo --seed 42

# Sin TUI (fallback en terminales restringidos)
uv run punto81 --no-tui
```

## Cómo se juega

Versión cara a cara contra la CPU. Ambos empezáis con **$200**.

1. **Ante**: cada mano cuesta $5 a cada uno.
2. Se reparten **5 cartas** a cada jugador.
3. **Primera ronda de apuestas** — la CPU abre.
4. **Descarte**: hasta **3 cartas** de tu mano.
5. **Segunda ronda de apuestas** — la abres tú; `Espacio` para pasar
   (*check*), `b` para apostar, `f` para retirarte.
6. **Showdown**: la mejor mano se lleva el bote.

Quien se quede a cero pierde la partida.

## Atajos de teclado

| Tecla     | Acción                                |
|-----------|----------------------------------------|
| `Enter`   | Confirmar / continuar                  |
| `Espacio` | Toggle descarte / pasar                |
| `1`..`5`  | Seleccionar carta                      |
| `b`       | Apostar                                |
| `c`       | Pasar (check)                          |
| `f`       | Retirarse (fold)                       |
| `r`       | Subir (raise)                          |
| `q`       | Salir                                  |
| `?`       | Ayuda                                  |
| `Ctrl+s`  | Guardar partida                        |
| `Ctrl+l`  | Cargar partida                         |
| `C`       | Modo alto contraste                    |

## Verificación

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src
uv run pytest --cov=src --cov-report=term-missing
uv run punto81 --demo --seed 42
```

## Documentación

- [Análisis del original](docs/original_program_analysis.md)
- [Arquitectura](docs/architecture.md)
- [Sistema de diseño](docs/design.md)
- [ADRs](docs/adr/)
- [Postmortem](docs/postmortem.md)
- [CHANGELOG](CHANGELOG.md)
- [TODO v1.1](TODO.md)

## Licencia

MIT. El listado bajo `legacy/` es una reconstrucción del POKER de Steve
North; los listados de *BASIC Computer Games* fueron liberados al
dominio público por Creative Computing.
