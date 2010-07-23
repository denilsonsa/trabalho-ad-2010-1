#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import cPickle as pickle
import sys

import simulador
reload(simulador)
from simulador import *

#uma máquina sozinha enviando para a rede
def teste1():
    maquinas = [
        Host(
            hostname = "maq1",
            distancia = 100,
            chegada = Deterministica(40 * 1000),
            num_quadros = 40
        ),
        Host(
            hostname = "maq2",
            distancia = 80,
            chegada = None,
            num_quadros = None
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
        eventos_fase_transiente = 500000,
        eventos_por_rodada = 30000,
        titulo = u"Cenário de teste 1",
        numero_de_rodadas = 10
    )
    return simulador

#uma máquina enviando sozinha para a rede com tempo de chegada o dobro do teste1
def teste2():
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
            chegada = None,
            num_quadros = None
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
        eventos_fase_transiente = 500000,
        eventos_por_rodada = 30000,
        titulo = u"Cenário de teste 2",
        numero_de_rodadas = 10
    )
    return simulador

#duas máquinas enviando para rede, sem backoff
def teste3():
    maquinas = [
        Host(
            hostname = "maq1",
            distancia = 100,
            chegada = Deterministica(200 * 1000),
            num_quadros = 1
        ),
        Host(
            hostname = "maq2",
            distancia = 80,
            chegada = Deterministica(200 * 1000),
            num_quadros = 1
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
        eventos_fase_transiente = 1000,
        eventos_por_rodada = 1000,
        titulo = u"Cenário de teste 3",
        numero_de_rodadas = 10,
        ignorar_backoff = True
    )
    return simulador

#duas máquinas enviando para a rede, sem colisão
def teste4():
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
        eventos_fase_transiente = 500000,
        eventos_por_rodada = 30000,
        titulo = u"Cenário de teste 4",
        numero_de_rodadas = 10,
        ignorar_colisao = True
    )
    return simulador


#dez máquinas enviando para a rede, com utilização média de 0,5mbps cada
def teste5():
    maquinas = [
        Host(
            hostname = "maq1",
            distancia = 100,
            chegada = Deterministica(320 * 1000),
            num_quadros = 20
        ),
        Host(
            hostname = "maq2",
            distancia = 80,
            chegada = Deterministica(320 * 1000),
            num_quadros = 20
        ),
        Host(
            hostname = "maq3",
            distancia = 60,
            chegada = Exponencial(80 * 1000),
            num_quadros = 5
        ),
        Host(
            hostname = "maq4",
            distancia = 40,
            chegada = Exponencial(160 * 1000),
            num_quadros = 10
        ),
        Host(
            hostname = "maq5",
            distancia = 30,
            chegada = Deterministica(80 * 1000),
            num_quadros = 5
        ),
        Host(
            hostname = "maq6",
            distancia = 42,
            chegada = Deterministica(640 * 1000),
            num_quadros = 40
        ),
        Host(
            hostname = "maq7",
            distancia = 11,
            chegada = Exponencial(320 * 1000),
            num_quadros = 20
        ),
        Host(
            hostname = "maq8",
            distancia = 70,
            chegada = Exponencial(160 * 1000),
            num_quadros = 10
        ),
        Host(
            hostname = "maq9",
            distancia = 55,
            chegada = Deterministica(80 * 1000),
            num_quadros = 5
        ),
        Host(
            hostname = "maq10",
            distancia = 33,
            chegada = Exponencial(80 * 1000),
            num_quadros = 5
        ),
    ]
    simulador = Simulador(    
        hosts = maquinas,
        eventos_fase_transiente = 10000000,
        eventos_por_rodada = 800000,
        titulo = u"Cenário de teste 5"
    )
    return simulador

cenarios = {
    "1": teste1,
    "2": teste2,
    "3": teste3,
    "4": teste4,
    "5": teste5,
}


def print_help():
    print "Digite: %s <cenário>" % (sys.argv[0],)
    print "Cenários disponíveis: " + " ".join(sorted(cenarios.keys()))


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in cenarios:
        print_help()
        sys.exit(1)

    id = sys.argv[1]
    file_prefix = "cenario_teste_%s" % (id,)

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
    simulador.salvar_graficos(file_prefix + ".eps")
    simulador.salvar_graficos(file_prefix + ".svg")
    # Também é possível salvar em formatos .eps, .ps, .svg, .pdf

    # Exibindo os gráficos na tela
    simulador.gerar_graficos()
    simulador.exibir_graficos()

if __name__ == "__main__":
    main()
