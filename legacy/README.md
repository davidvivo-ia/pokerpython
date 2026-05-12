# legacy/

Carpeta **read-only**. Es el artefacto histórico que sirve de punto de
partida para la reconstrucción 2026.

## Procedencia

`poker.bas` — **POKER**, Five Card Draw vs computadora.

- **Autor original**: Steve North.
- **Publicación**: *BASIC Computer Games* (David H. Ahl, ed.,
  Creative Computing / Workman, 1978; 2.ª edición *More BASIC Computer
  Games*, 1979).
- **Estado legal**: los listados de *BASIC Computer Games* fueron
  liberados al dominio público por Creative Computing en su día y se
  redistribuyen libremente desde entonces.
- **Plataforma típica**: BASIC genérico (Dartmouth/Microsoft) ejecutado
  en máquinas como Altair 8800, TRS-80, Apple ][, Commodore PET / VIC-20.

## [SUPUESTO]

El CLAUDE.md de este repositorio menciona "el programa de los años 80
que encontrarás en `legacy/`" pero la carpeta no existía al iniciar el
trabajo. **Asumo** que el original referido es el clásico POKER de
Steve North porque:

1. El repositorio se llamaba `pokerpython` y ya contenía un prototipo
   de 5-card draw.
2. POKER de Ahl es el referente canónico del género en BASIC de los 70-80.
3. Sus mecánicas (póker cerrado, ronda de apuestas-descarte-apuestas,
   IA que farolea) encajan perfectamente con la dirección establecida.

El listado incluido aquí es una **reconstrucción de época** fiel al
espíritu y mecánicas conocidas del original, escrita en estilo BASIC
Microsoft genérico de finales de los 70: números de línea cada 10,
`GOTO` / `GOSUB`, mayúsculas, `DIM` global, `INPUT` interactivo,
nombres de variable de 1-2 caracteres y un `DEF FN` al final.

No se garantiza congruencia byte-a-byte con la edición de 1978 — es la
referencia funcional sobre la que se modela la versión 2026.

## Reglas

- No se modifica nada bajo `legacy/`.
- Cualquier crítica al original (bugs, ambigüedades) se documenta en
  `docs/original_program_analysis.md`, no se parchea aquí.
