#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import simulador
reload(simulador)
from simulador import *


def main():
    # Pequeno teste, com valores quaisquer, escolhidos aleatoriamente
    maquinas = [
        Host(
            hostname = "maq1",
            distancia = 100,
            chegada = Exponencial(20),
            num_quadros = 10
        ),
        Host(
            hostname = "maq2",
            distancia = 80,
            chegada = Deterministica(20),
            num_quadros = 10
        ),
        Host(
            hostname = "maq3",
            distancia = 60,
            chegada = None,
            num_quadros = 10
        ),
        Host(
            hostname = "maq4",
            distancia = 40,
            chegada = None,
            num_quadros = 10
        ),
    ]
    simulador = Simulador(    
        hosts = maquinas
    )

    print "Hello suckers! Gonna start simulatin'"
    simulador.start()
    simulador.run()

if __name__ == "__main__":
    main()
