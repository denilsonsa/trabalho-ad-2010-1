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
        tempo_minimo_ocioso = 9.6,
        tempo_transmissao_quadro = 800, #8000 bits/quadro / 10 Mbps = 800microseg/quadro
        tempo_reforco_jam = 3.2,
        tempo_fatia_backoff = 51.2,
        tempo_propagacao = 0.005, #5 microseg/km = 0.005 microseg/m
        eventos_fase_transiente = 5000000,
        eventos_por_rodada = 250000,
        titulo = u"Cenário 2"
    )

    simulador.start()
    simulador.run()
    simulador.gerar_graficos()

if __name__ == "__main__":
    main()
