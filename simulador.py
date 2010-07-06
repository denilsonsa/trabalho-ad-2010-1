# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import numpy
import random
import heapq
import sys


class HeapDeEventos(list):
    """Implementação de uma fila com prioridades."""

    def adicionar(self, tempo, evento):
        heapq.heappush(self, ())

    def remover(self):
        """Retorna uma tupla (tempo, evento)"""
        return heapq.heappop(self)


######################################################################
# As funções a seguir são usadas na definição dos parâmetros de cada 
# Host, na inicialização do simulador.

def Exponencial(intervalo):
    """Gerador de tempo exponencial com média igual a 'intervalo'."""
    return lambda: random.expovariate(1.0/intervalo)

def Deterministica(valor):
    """Gerador deterministico de tempos ou número de quadros."""
    return lambda: intervalo

def Geometrica(probabilidade):
    """Gerador de distribuição geométrica."""
    return lambda: numpy.random.geometric(probabilidade)

def Offline():
    """Retorna sempre -1, que deve ser ignorado pelo simulador."""
    # TODO: Talvez seja uma boa idéia subir uma exceção em vez de
    # retornar -1. Ou então retornar None.
    return lambda: -1


######################################################################
# Equipamentos "virtuais" simulados

class Host(object):
    """ """

    def __init__(self, hostname, dist, chegada, numquadros):
        """Parâmetros:
        hostname = Nome da máquina (ignorado pelo simulador)
        dist = Distância deste host ao hub (medida em metros)
        chegada = Processo de chegada das mensagens a ser enviadas
        numquadros = Distribuição do número de quadros para cada mensagem"""

        self.hostname = hostname
        self.dist = dist #TODO: converter esta distância em tempo!
        self.chegada = chegada
        #self.numquadros = numquadros

        # XXX: Cuidado! Não é tratado o caso do número de quadros ser
        # fracionário!
        if callable(numquadros):
            # Se o tipo de distribuição foi definido explicitamente:
            self.numquadros = numquadros
        else:
            # Caso contrário, auto-detectar o tipo de distribuição através
            # do número passado
            if numquadros < 1:
                # O número passado é uma probabilidade
                self.numquadros = Geometrica(numquadros)
            else:
                # O número passado é uma quantidade constante
                # (determinística) de quadros
                self.numquadros = Deterministica(numquadros)



class Hub(object):
    """Hub que interconecta diferentes hosts. Sua única função é repetir o
    sinal para todas as máquinas (inclusive para aquela que enviou o
    sinal).
    
    Para funcionar, o simulador precisa ter um, e apenas um, hub."""

    def __init__(self, hosts):
        """Parâmetros:
        hosts = Lista de máquinas conectadas ao hub."""
        self.hosts = hosts


######################################################################
# Eventos

class NomeDoEventoAqui(object):
    pass


######################################################################

class Simulador(object):
    """Classe principal que encapsula um simulador."""

    def __init__(self):
        self.eventos = HeapDeEventos()
        self.tempo_agora = 0
