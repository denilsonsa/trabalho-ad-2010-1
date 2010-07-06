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
            dist = 100,
            chegada = Exponencial(20),
            num_quadros = 10
        ),
        Host(
            hostname = "maq2",
            dist = 80,
            chegada = Deterministica(20),
            num_quadros = 10
        ),
        Host(
            hostname = "maq3",
            dist = 60,
            chegada = None,
            num_quadros = 10
        ),
        Host(
            hostname = "maq4",
            dist = 40,
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
