# ADR-0001 — Capa de presentación

- **Fecha**: 2026-05-12
- **Estado**: Aceptada

## Contexto

El programa original es BASIC interactivo de los 70: solo `PRINT` /
`INPUT` sobre teletipo. No usa caracteres semigráficos posicionados ni
modo gráfico real. Las cartas se imprimen como texto (`"ACE OF
SPADES"`).

La regla de decisión del CLAUDE.md asigna directamente este perfil al
*default*: **TUI con Textual**. No hay razón para escalar a `pygame-ce`
(no hay sprites, scrolling, ni colisión), ni para degradar a CLI puro
(es un juego, no una utilidad).

## Opciones consideradas

1. **CLI con Typer + Rich** — más simple, menos espacio para diseño.
2. **TUI con Textual** ✓ — pantalla completa, CSS propio, animaciones,
   accesibilidad por teclado.
3. **Gráfico con pygame-ce** — sobreingeniería para un 5-card draw.
4. **Web (FastAPI + HTMX)** — fuera de stack obligatorio.

## Decisión

**Textual**. Permite cumplir el objetivo de "presentación memorable"
con CSS dedicado (`assets/tcss/`), respeta el espíritu textual del
original y se integra con el resto del stack (typer, rich) para el
modo demo y los mensajes fuera de mesa.

## Consecuencias

- Necesitamos test snapshots para regresiones visuales (Textual los
  soporta de fábrica).
- El render de cartas vive en widgets reutilizables, no en el dominio.
- Para el modo `--demo` se usa el driver "headless" de Textual y se
  graba la sesión a SVG si el usuario lo pide.
