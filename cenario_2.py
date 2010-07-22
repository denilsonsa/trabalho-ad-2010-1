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
            chegada = Exponencial(80 * 1000),
            num_quadros = 40
        ),
        Host(
            hostname = "maq2",
            distancia = 80,
            chegada = Exponencial(80 * 1000),
            num_quadros = 40
        ),
        Host(
            hostname = "maq3",
            distancia = 60,
            chegada = None,
            num_quadros = None
        ),
        Host(
            hostname = "maq4",
            distancia = 40,
            chegada = None,
            num_quadros = None
        ),
    ]
    simulador = Simulador(    
        hosts = maquinas,
        eventos_fase_transiente = 5000000,
        eventos_por_rodada = 400000,
        titulo = u"Cenário 2"
    )
    return simulador

def main():
    simulador = init()
    simulador.start()
    simulador.run()

    simulador.gerar_graficos(layout="vertical")
    simulador.salvar_graficos("cenario_2.png")

    simulador.gerar_graficos()
    simulador.exibir_graficos()

if __name__ == "__main__":
    main()
