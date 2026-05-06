"""Juego de Poker de 5 cartas (Five Card Draw) en la terminal.

Modo: 1 jugador humano vs 1 CPU.
Reglas: cada jugador recibe 5 cartas, hay una ronda de apuestas,
luego cada jugador puede descartar hasta 3 cartas, otra ronda de
apuestas y se muestra al ganador.
"""

import random
from collections import Counter
from itertools import combinations

PALOS = {"P": "Picas", "C": "Corazones", "D": "Diamantes", "T": "Treboles"}
SIMBOLOS = {"P": "♠", "C": "♥", "D": "♦", "T": "♣"}
VALORES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
    "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14,
}
ORDEN_VALORES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

NOMBRES_MANO = {
    9: "Escalera Real",
    8: "Escalera de Color",
    7: "Poker",
    6: "Full House",
    5: "Color",
    4: "Escalera",
    3: "Trio",
    2: "Doble Pareja",
    1: "Pareja",
    0: "Carta Alta",
}


class Carta:
    def __init__(self, valor, palo):
        self.valor = valor
        self.palo = palo

    @property
    def num(self):
        return VALORES[self.valor]

    def __repr__(self):
        return f"{self.valor}{SIMBOLOS[self.palo]}"


class Mazo:
    def __init__(self):
        self.cartas = [Carta(v, p) for v in ORDEN_VALORES for p in PALOS]
        random.shuffle(self.cartas)

    def repartir(self, n=1):
        return [self.cartas.pop() for _ in range(n)]


def evaluar_mano(cartas):
    """Devuelve una tupla (rango, desempates) para comparar manos."""
    nums = sorted([c.num for c in cartas], reverse=True)
    palos = [c.palo for c in cartas]
    cuenta = Counter(nums)
    grupos = sorted(cuenta.items(), key=lambda x: (-x[1], -x[0]))
    repeticiones = [g[1] for g in grupos]
    valores = [g[0] for g in grupos]

    es_color = len(set(palos)) == 1
    nums_unicos = sorted(set(nums))
    es_escalera = len(nums_unicos) == 5 and nums_unicos[-1] - nums_unicos[0] == 4
    if set(nums) == {14, 2, 3, 4, 5}:
        es_escalera = True
        nums = [5, 4, 3, 2, 1]

    if es_color and es_escalera and max(nums) == 14 and min(nums) == 10:
        return (9, nums)
    if es_color and es_escalera:
        return (8, nums)
    if repeticiones == [4, 1]:
        return (7, valores)
    if repeticiones == [3, 2]:
        return (6, valores)
    if es_color:
        return (5, nums)
    if es_escalera:
        return (4, nums)
    if repeticiones == [3, 1, 1]:
        return (3, valores)
    if repeticiones == [2, 2, 1]:
        return (2, valores)
    if repeticiones == [2, 1, 1, 1]:
        return (1, valores)
    return (0, nums)


def nombre_mano(cartas):
    rango, _ = evaluar_mano(cartas)
    return NOMBRES_MANO[rango]


def render_carta(carta=None, oculta=False):
    """Devuelve una lista de 7 lineas con la carta dibujada en ASCII."""
    if oculta:
        return [
            "┌─────────┐",
            "│▚▚▚▚▚▚▚▚▚│",
            "│▚▚▚▚▚▚▚▚▚│",
            "│▚▚▚▚▚▚▚▚▚│",
            "│▚▚▚▚▚▚▚▚▚│",
            "│▚▚▚▚▚▚▚▚▚│",
            "└─────────┘",
        ]
    v = carta.valor
    s = SIMBOLOS[carta.palo]
    izq = v.ljust(2)
    der = v.rjust(2)
    return [
        "┌─────────┐",
        f"│{izq}       │",
        "│         │",
        f"│    {s}    │",
        "│         │",
        f"│       {der}│",
        "└─────────┘",
    ]


def mostrar_mano(cartas, oculta=False, indices=False):
    filas = [render_carta(c, oculta=oculta) for c in cartas]
    lineas = ["  ".join(fila[i] for fila in filas) for i in range(7)]
    salida = "\n".join(lineas)
    if indices and not oculta:
        etiquetas = "  ".join(f"    ({i+1})    " for i in range(len(cartas)))
        salida += "\n" + etiquetas
    return salida


def pedir_apuesta(jugador, fichas, apuesta_actual, ya_apostado):
    print(f"\n{jugador['nombre']} - Fichas: {jugador['fichas']} - Bote: {fichas}")
    print(f"Apuesta a igualar: {apuesta_actual} (ya aportaste {ya_apostado})")
    while True:
        opcion = input("Accion ([P]asar/igualar, [S]ubir, [R]etirarse): ").strip().lower()
        if opcion in ("p", ""):
            por_pagar = apuesta_actual - ya_apostado
            if por_pagar > jugador["fichas"]:
                por_pagar = jugador["fichas"]
            return ("igualar", por_pagar)
        if opcion == "s":
            try:
                cantidad = int(input("Cantidad a subir (sobre la apuesta actual): "))
            except ValueError:
                print("Numero invalido.")
                continue
            if cantidad <= 0:
                print("Debe ser positivo.")
                continue
            por_pagar = apuesta_actual - ya_apostado + cantidad
            if por_pagar > jugador["fichas"]:
                print("No tienes suficientes fichas.")
                continue
            return ("subir", por_pagar, cantidad)
        if opcion == "r":
            return ("retirarse", 0)
        print("Opcion no valida.")


def cpu_decision(mano, apuesta_actual, ya_apostado, fichas, agresividad=0.3):
    rango, _ = evaluar_mano(mano)
    por_pagar = apuesta_actual - ya_apostado
    if rango >= 3:
        if random.random() < 0.6 and fichas > por_pagar + 10:
            return ("subir", por_pagar + 10, 10)
        return ("igualar", min(por_pagar, fichas))
    if rango >= 1:
        if por_pagar > fichas // 3 and random.random() < 0.3:
            return ("retirarse", 0)
        return ("igualar", min(por_pagar, fichas))
    if por_pagar == 0:
        if random.random() < agresividad:
            return ("subir", 5, 5)
        return ("igualar", 0)
    if random.random() < 0.2:
        return ("igualar", min(por_pagar, fichas))
    return ("retirarse", 0)


def ronda_apuestas(humano, cpu, bote, mano_humano, mano_cpu, ciega=2):
    apuestas = {"humano": 0, "cpu": 0}
    apuesta_actual = ciega
    apuestas["humano"] = min(ciega, humano["fichas"])
    humano["fichas"] -= apuestas["humano"]
    bote += apuestas["humano"]
    print(f"\n(Ciega obligatoria de {ciega} fichas para {humano['nombre']})")

    turno = "cpu"
    pasados = {"humano": False, "cpu": False}

    while True:
        jugador = humano if turno == "humano" else cpu
        otro = "cpu" if turno == "humano" else "humano"

        if turno == "humano":
            accion = pedir_apuesta(
                {"nombre": humano["nombre"], "fichas": humano["fichas"]},
                bote, apuesta_actual, apuestas["humano"],
            )
        else:
            accion = cpu_decision(mano_cpu, apuesta_actual, apuestas["cpu"], cpu["fichas"])
            print(f"\nCPU decide: {accion[0]}")

        tipo = accion[0]
        if tipo == "retirarse":
            return bote, otro, apuestas
        if tipo == "igualar":
            pago = accion[1]
            jugador["fichas"] -= pago
            apuestas[turno] += pago
            bote += pago
            pasados[turno] = True
            if pasados["humano"] and pasados["cpu"] and apuestas["humano"] == apuestas["cpu"]:
                return bote, None, apuestas
        elif tipo == "subir":
            pago, subida = accion[1], accion[2]
            jugador["fichas"] -= pago
            apuestas[turno] += pago
            bote += pago
            apuesta_actual += subida
            pasados = {"humano": False, "cpu": False}
            pasados[turno] = True
            print(f"{jugador['nombre']} sube {subida}. Apuesta actual: {apuesta_actual}")

        turno = otro
        if humano["fichas"] == 0 and cpu["fichas"] == 0:
            return bote, None, apuestas


def descarte_humano(mano, mazo):
    print("\nTu mano:")
    print(mostrar_mano(mano, indices=True))
    print("\nIndices de cartas a descartar (1-5), separados por espacio. Enter para no descartar.")
    while True:
        entrada = input("> ").strip()
        if not entrada:
            return mano
        try:
            idx = sorted({int(x) - 1 for x in entrada.split()}, reverse=True)
        except ValueError:
            print("Entrada invalida.")
            continue
        if any(i < 0 or i >= 5 for i in idx):
            print("Indices fuera de rango.")
            continue
        if len(idx) > 3:
            print("Maximo 3 cartas.")
            continue
        for i in idx:
            mano.pop(i)
        mano.extend(mazo.repartir(len(idx)))
        return mano


def descarte_cpu(mano, mazo):
    rango, _ = evaluar_mano(mano)
    if rango >= 4:
        return mano
    cuenta = Counter([c.num for c in mano])
    a_quedar = []
    descartadas = []
    for c in mano:
        if cuenta[c.num] >= 2 or c.num >= 13:
            a_quedar.append(c)
        else:
            descartadas.append(c)
    descartar = descartadas[:3]
    nueva = [c for c in mano if c not in descartar]
    nueva.extend(mazo.repartir(len(descartar)))
    print(f"\nCPU descarta {len(descartar)} carta(s).")
    return nueva


def jugar_ronda(humano, cpu):
    print("\n" + "=" * 50)
    print(f"  Nueva mano - {humano['nombre']}: {humano['fichas']}  |  CPU: {cpu['fichas']}")
    print("=" * 50)

    mazo = Mazo()
    mano_humano = mazo.repartir(5)
    mano_cpu = mazo.repartir(5)
    bote = 0

    print("\nMano CPU:")
    print(mostrar_mano(mano_cpu, oculta=True))
    print("\nTu mano:")
    print(mostrar_mano(mano_humano))

    bote, ganador, _ = ronda_apuestas(humano, cpu, bote, mano_humano, mano_cpu)
    if ganador:
        print(f"\n{(humano if ganador == 'humano' else cpu)['nombre']} gana el bote de {bote} fichas (rival se retiro).")
        (humano if ganador == "humano" else cpu)["fichas"] += bote
        return

    print("\n--- Fase de descarte ---")
    mano_humano = descarte_humano(mano_humano, mazo)
    mano_cpu = descarte_cpu(mano_cpu, mazo)

    print("\nTu nueva mano:")
    print(mostrar_mano(mano_humano))

    print("\n--- Segunda ronda de apuestas ---")
    bote, ganador, _ = ronda_apuestas(humano, cpu, bote, mano_humano, mano_cpu)
    if ganador:
        print(f"\n{(humano if ganador == 'humano' else cpu)['nombre']} gana el bote de {bote} fichas (rival se retiro).")
        (humano if ganador == "humano" else cpu)["fichas"] += bote
        return

    print("\n--- Showdown ---")
    print(f"\nMano CPU ({nombre_mano(mano_cpu)}):")
    print(mostrar_mano(mano_cpu))
    print(f"\nTu mano ({nombre_mano(mano_humano)}):")
    print(mostrar_mano(mano_humano))

    eval_h = evaluar_mano(mano_humano)
    eval_c = evaluar_mano(mano_cpu)
    if eval_h > eval_c:
        print(f"\n{humano['nombre']} gana {bote} fichas!")
        humano["fichas"] += bote
    elif eval_c > eval_h:
        print(f"\nLa CPU gana {bote} fichas.")
        cpu["fichas"] += bote
    else:
        print("\nEmpate. Bote dividido.")
        humano["fichas"] += bote // 2
        cpu["fichas"] += bote - bote // 2


def main():
    print("=" * 50)
    print("   POKER - Five Card Draw")
    print("=" * 50)
    nombre = input("Tu nombre: ").strip() or "Jugador"
    humano = {"nombre": nombre, "fichas": 100}
    cpu = {"nombre": "CPU", "fichas": 100}

    while humano["fichas"] > 0 and cpu["fichas"] > 0:
        try:
            jugar_ronda(humano, cpu)
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break
        seguir = input("\nOtra mano? (s/n): ").strip().lower()
        if seguir == "n":
            break

    print("\n" + "=" * 50)
    print(f"Final - {humano['nombre']}: {humano['fichas']}  |  CPU: {cpu['fichas']}")
    if humano["fichas"] > cpu["fichas"]:
        print("Felicidades, ganaste la partida!")
    elif cpu["fichas"] > humano["fichas"]:
        print("La CPU gano la partida.")
    else:
        print("Partida empatada.")


if __name__ == "__main__":
    main()
