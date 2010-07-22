#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import cPickle as pickle
import sys

import simulador
reload(simulador)
from simulador import *


def cenario1():
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
            chegada = Deterministica(80 * 1000),
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
        eventos_fase_transiente = 2500000,
        eventos_por_rodada = 500000,
        titulo = u"Cenário 1"
    )
    return simulador


def cenario2():
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
        eventos_fase_transiente = 10**7,
        eventos_por_rodada = 500000,
        titulo = u"Cenário 2"
    )
    return simulador


def cenario3():
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
        eventos_por_rodada = 500000,
        titulo = u"Cenário 3"
    )
    return simulador


def cenario4():
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
            chegada = Exponencial(16 * 1000),
            num_quadros = 1
        ),
        Host(
            hostname = "maq3",
            distancia = 60,
            chegada = Exponencial(16 * 1000),
            num_quadros = 1
        ),
        Host(
            hostname = "maq4",
            distancia = 40,
            chegada = Exponencial(16 * 1000),
            num_quadros = 1
        ),
    ]
    simulador = Simulador(    
        hosts = maquinas,
        eventos_fase_transiente = 2500000,
        eventos_por_rodada = 500000,
        titulo = u"Cenário 4"
    )
    return simulador


cenarios = {
    "1": cenario1,
    "2": cenario2,
    "3": cenario3,
    "4": cenario4,
}


def print_help():
    print "Digite: %s <cenário>" % (sys.argv[0],)
    print "Cenários disponíveis: " + " ".join(sorted(cenarios.keys()))


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in cenarios:
        print_help()
        sys.exit(1)

    id = sys.argv[1]
    file_prefix = "cenario_%s" % (id,)

    simulador = cenarios[id]()
    simulador.start()
    simulador.run()

    # Salvando os resultados num arquivo
    pickle.dump(simulador, file(file_prefix + ".pickle","wb"), protocol=2)
    # Depois, é possível recarregar os resultados usando:
    #   simulador = pickle.load(file("cenario_1.pickle","rb"))
    # Depois de carregado, é possível acessar normalmente todos os
    # membros do objeto simulador, e inclusive gerar novos gráficos.
    # Só não é possível continuar/recomeçar a simulação.

    # Salvando os gráficos num arquivo
    simulador.gerar_graficos(layout="vertical")
    simulador.salvar_graficos(file_prefix + ".png")
    # Também é possível salvar em formatos .eps, .ps, .svg, .pdf

    # Exibindo os gráficos na tela
    simulador.gerar_graficos()
    simulador.exibir_graficos()

if __name__ == "__main__":
    main()
