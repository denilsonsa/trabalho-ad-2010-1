# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import numpy
import random
import heapq
import sys


class HeapDeEventos(list):
    """Implementação de uma fila com prioridades."""

    def adicionar(self, tempo, evento):
        heapq.heappush(self, (tempo, evento))

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
    return lambda: valor

def Geometrica(probabilidade):
    """Gerador de distribuição geométrica."""
    return lambda: numpy.random.geometric(probabilidade)


######################################################################
# Coisas que encapsulam a interface do Host

class Mensagem(object):
    """ """

    def __init__(self, num_quadros):
        self.num_quadros = num_quadros
    

class Host(object):
    """ """

    def __init__(self, hostname, distancia, chegada, num_quadros):
        """Parâmetros:
        hostname = Nome da máquina (ignorado pelo simulador)
        dist = Distância deste host ao hub (medida em metros)
        chegada = Processo de chegada das mensagens a ser enviadas
        num_quadros = Distribuição do número de quadros para cada mensagem"""

        self.hostname = hostname
        self.distancia = distancia #TODO: converter esta distância em tempo!
        self.chegada = chegada
        #self.num_quadros = num_quadros
        self.fila = [] #fila de mensagens
        self.proximo_quadro = -1
        self.tentativas_de_tramissao = -1
        self.tempo_comeco_envio_quadro = -1
        self.tempo_comeco_envio_mensagem = -1

        # XXX: Cuidado! Não é tratado o caso do número de quadros ser
        # fracionário!
        if callable(num_quadros):
            # Se o tipo de distribuição foi definido explicitamente:
            self.num_quadros = num_quadros
        else:
            # Caso contrário, auto-detectar o tipo de distribuição através
            # do número passado
            if num_quadros < 1:
                # O número passado é uma probabilidade
                self.num_quadros = Geometrica(num_quadros)
            else:
                # O número passado é uma quantidade constante
                # (determinística) de quadros
                self.num_quadros = Deterministica(num_quadros)

    def tentar_enviar(self):
        print "Nem sequer tentei enviar... :D"



######################################################################
# Eventos

class Evento(object):
    """Classe abstrata que represente um evento."""

    def processar(self, simulador):
        raise NotImplementedError()    

        
class ChegouMensagemParaSerEnviada(Evento):
    """Classe que representa uma chegada de mensagem da camada superior."""

    def __init__(self, maquina):
        self.maquina = maquina
        self.num_quadros = maquina.num_quadros()
        

    def processar(self, simulador):
        print "Processando ChegadaDeMensagemParaSerEnviada em t=%f na maquina=%s" % (
            simulador.tempo_agora, self.maquina.hostname )

        #gera próximo evento
        simulador.eventos.adicionar(
            simulador.tempo_agora + self.maquina.chegada(),
            ChegouMensagemParaSerEnviada(self.maquina)
        )

        fila_vazia = (len(self.maquina.fila) == 0)

        #adiciona mensagem à fila de envio
        self.maquina.fila.append(
            Mensagem(self.num_quadros)
        )

        if fila_vazia:
            self.maquina.tentar_enviar()


######################################################################

class Simulador(object):
    """Classe principal que encapsula um simulador."""

    def __init__(self, hosts):
        """Parâmetros:
        hosts = Lista de máquinas conectadas ao hub."""
        self.hosts = hosts
        self.eventos = HeapDeEventos()
        self.tempo_agora = 0

    def start(self):
        """Inicializa o simulador, gerando os eventos iniciais"""
        for maquina in self.hosts:
            if callable(maquina.chegada):
                self.eventos.adicionar(
                    maquina.chegada(),
                    ChegouMensagemParaSerEnviada(maquina)
                )

    def run(self):
        """Executa uma rodada da simulação"""
        for iteracao in xrange(100): #*** TODO: COLOCAR UM CRITERIO DE PARADA DECENTE
            #retirar evento da fila
            self.tempo_agora, evento = self.eventos.remover()

            #processar evento
            evento.processar(self)
            
