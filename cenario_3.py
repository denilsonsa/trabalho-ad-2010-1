#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import simulador
reload(simulador)
from simulador import *


def init():
    maquinas = [
        Host(
            hostname = "maq1",
            distancia = 100,
            chegada = Deterministica(80 * 1000),
            num_quadros = 40
        ),
        Host(
            hostname = "maq2",
            distancia = 80,
            chegada = Deterministica(16 * 1000),
            num_quadros = 1
        ),
        Host(
            hostname = "maq3",
            distancia = 60,
            chegada = Deterministica(16 * 1000),
            num_quadros = 1
        ),
        Host(
            hostname = "maq4",
            distancia = 40,
            chegada = Deterministica(16 * 1000),
            num_quadros = 1
        ),
    ]
    simulador = Simulador(    
        hosts = maquinas,
        eventos_fase_transiente = 250000,
        eventos_por_rodada = 400000,
        titulo = u"Cenário 3"
    )
    return simulador

def main():
    simulador = init()
    simulador.start()
    simulador.run()

    simulador.gerar_graficos(layout="vertical")
    simulador.salvar_graficos("cenario_3.png")

    simulador.gerar_graficos()
    simulador.exibir_graficos()

if __name__ == "__main__":
    main()
