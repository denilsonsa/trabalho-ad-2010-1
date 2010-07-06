#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et


from simulador import *


def main():
    # Pequeno teste, com valores quaisquer, escolhidos aleatoriamente
    maquinas = [
        Host(
            hostname = "maq1",
            dist = 100,
            chegada = Exponencial(20),
            numquadros = 10
        ),
        Host(
            hostname = "maq2",
            dist = 80,
            chegada = Deterministica(20),
            numquadros = 10
        ),
        Host(
            hostname = "maq3",
            dist = 60,
            chegada = Offline(),
            numquadros = 10
        ),
        Host(
            hostname = "maq4",
            dist = 40,
            chegada = Offline(),
            numquadros = 10
        ),
    ]
    hub = Hub(
        hosts = maquinas
    )
    simulador = Simulador(
        # hub = hub
    )
    print "Hello!"


if __name__ == "__main__":
    main()
