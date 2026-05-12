# Arquitectura

## Capas y dependencias

`punto81` (nombre interno del paquete; ver ADR-0002) implementa una
arquitectura en capas a la Clean Architecture, con dirección estricta
de dependencias de fuera hacia dentro.

```
+----------------------------------------------------------------------+
|                        PRESENTATION (Textual TUI)                    |
|                                                                      |
|   screens/   widgets/   tcss/   keymaps   ┌─ presenters ──────────┐  |
|                                            │ map domain -> view    │  |
|                                            └───────────────────────┘  |
+--------------------------+-------------------------------------------+
                           |  depends on
                           v
+----------------------------------------------------------------------+
|                          APPLICATION                                 |
|                                                                      |
|   use_cases/                  + GameSession orchestrator             |
|     start_hand               + DemoScript                            |
|     place_bet                                                        |
|     draw_cards                                                       |
|     showdown                                                         |
+--------------------------+-------------------------------------------+
                           |  depends on
                           v
+----------------------------------------------------------------------+
|                            DOMAIN  (pure)                            |
|                                                                      |
|   models/        rules/             policies/                        |
|     Card           HandEvaluator      CpuBettingPolicy               |
|     Suit, Rank     ShowdownResolver   CpuDrawPolicy                  |
|     Hand           BettingRules                                      |
|     Deck                                                             |
|     Bankroll                                                         |
|     Pot                                                              |
+----------------------------------------------------------------------+
                           ^
                           |  implements ports
+--------------------------+-------------------------------------------+
|                        INFRASTRUCTURE                                |
|                                                                      |
|   rng/          persistence/         clock/                          |
|     SystemRng     JsonSaveStore        SystemClock                   |
|     SeededRng                                                        |
+----------------------------------------------------------------------+
```

### Reglas

1. `domain` no importa nada fuera de la biblioteca estándar y de sí
   mismo. Todo lo que parezca un IO se modela como **puerto** (un
   `Protocol`).
2. `application` puede importar `domain` y los puertos. Nunca a
   `presentation` ni a `infrastructure` concretos — solo a sus
   `Protocol`s.
3. `infrastructure` provee implementaciones concretas de los puertos
   definidos en `domain` y `application`.
4. `presentation` consume `application`. Nunca toca dominio directamente
   excepto para tipos de valor (rangos, palos, montos).

## Puertos y adaptadores

| Puerto (Protocol)        | Definido en              | Implementaciones                  |
|--------------------------|--------------------------|-----------------------------------|
| `Rng`                    | `domain.ports.rng`       | `SeededRng`, `SystemRng`          |
| `SaveStore`              | `application.ports`      | `JsonSaveStore`, `InMemorySaveStore` |
| `Clock`                  | `application.ports`      | `SystemClock`, `FrozenClock`      |

## Flujo de una mano

```
TUI                 GameSession              Domain
 │                       │                      │
 │ user: "play hand"     │                      │
 ├──────────────────────▶│                      │
 │                       │ new Deck(rng)        │
 │                       ├─────────────────────▶│
 │                       │ deal 5+5             │
 │                       ├─────────────────────▶│
 │                       │ HandState (immut.)   │
 │                       │◀─────────────────────┤
 │ render hands          │                      │
 │◀──────────────────────┤                      │
 │ user: place_bet(X)    │                      │
 ├──────────────────────▶│                      │
 │                       │ BettingRules.apply  │
 │                       ├─────────────────────▶│
 │                       │ new HandState        │
 │                       │◀─────────────────────┤
 │                       │ CpuPolicy.respond    │
 │                       ├─────────────────────▶│
 │                       │ CpuAction            │
 │                       │◀─────────────────────┤
 │ render bet            │                      │
 │◀──────────────────────┤                      │
 │ (draw, 2nd bet, ...)  │                      │
 │                       │ ShowdownResolver     │
 │                       ├─────────────────────▶│
 │                       │ Outcome              │
 │                       │◀─────────────────────┤
 │ render result         │                      │
 │◀──────────────────────┤                      │
```

Toda transición de estado del dominio devuelve **una nueva instancia
inmutable**. La sesión guarda la historia para reproducibilidad y para
el modo `--demo`.

## Modelo de inmutabilidad

`@dataclass(frozen=True, slots=True)` para todas las entidades y value
objects. Las transiciones devuelven `Self` nuevos via métodos `with_*`
o `apply_*`. No hay setters.

## Estrategia de testing

| Capa             | Estilo               | Cobertura objetivo |
|------------------|----------------------|--------------------|
| `domain`         | Unit + Hypothesis    | >= 90% (>=80% gate)|
| `application`    | Integration          | >= 80%             |
| `infrastructure` | Contract tests       | >= 70%             |
| `presentation`   | Snapshot + smoke     | best effort        |

`HandEvaluator` se testea con propiedades de hypothesis (cualquier
mano de 5 cartas distintas devuelve un `HandRank` válido; la relación
de orden es total y transitiva). El modo `--demo` actúa como test E2E.

## Determinismo

Toda fuente de azar pasa por un puerto `Rng`. El CLI acepta `--seed`
para fijarlo. El modo `--demo` usa `seed=42` por defecto y un script
de acciones predefinidas, lo que permite grabar GIFs o ejecutar como
parte de CI.
