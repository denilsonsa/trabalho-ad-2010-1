# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import numpy
import random
import heapq
import sys

import matplotlib.pyplot as pyplot

######################################################################
# Estruturas auxiliares: Heap de eventos e coleta de estatísticas

class HeapDeEventos(list):
    """Implementação de uma fila com prioridades."""

    def adicionar(self, tempo, evento):
        heapq.heappush(self, (tempo, evento))

    def remover(self):
        """Retorna uma tupla (tempo, evento)"""
        return heapq.heappop(self)


class Estatisticas(object):
    """Coletor de amostras para geração e plotagem de estatísticas"""
    
    def __init__(self):
        self.amostras = []
        self.intervalos = []
        self.soma_amostras = 0
        self.soma_quadrados = 0
        self.num_amostras = 0

    def adicionar_amostra(self, amostra):
        self.amostras.append(amostra)
        self.soma_amostras += amostra
        self.soma_quadrados += amostra*amostra
        self.num_amostras += 1

    def adicionar_intervalo(self, intervalo):
        self.intervalos.append(intervalo)

    def plot(self, titulo = "Estatisticas"):
        if len(self.amostras) != len(self.intervalos):
            pyplot.plot(self.amostras)
        else:
            x = arange(1, self.num_amostras+1)
            pyplot.errorbar(x, self.amostras, yerr=self.intervalos)

        pyplot.title(titulo)
        pyplot.show()
        
    def media(self):
        if self.num_amostras == 0:
            return 0

        return self.soma_amostras / self.num_amostras

    def variancia(self):
        if self.num_amostras < 2:
            return 0

        #ref: http://en.wikipedia.org/wiki/Variance#Population_variance_and_sample_variance
        sq = self.soma_quadrados
        sa = self.soma_amostras
        n = self.num_amostras
        return (sq / (n - 1)) - ((sa * sa) / (n * (n - 1)))

    def intervalo_de_confianca(self):
        t_student_95 = 1.645
        return 2 * t_student_95 * sqrt(self.variancia() / self.num_amostras)
        


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

    def __init__(self, cor, num_quadros):
        self.cor = cor
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
        self.uso_do_meio = 0
        self.tempo_comeco_ocioso = -10000

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


    def tentar_enviar(self, simulador):
        if self.uso_do_meio == 0:
            simulador.eventos.adicionar(
                max(simulador.tempo_agora, self.tempo_comeco_ocioso + simulador.tempo_minimo_ocioso),
                InicioDeEnvio(self)
            )
        #else: será tratado no FimDeRecebimento



######################################################################
# Eventos

class Evento(object):
    """Classe abstrata que represente um evento."""

    def processar(self, simulador):
        raise NotImplementedError()    

        
class ChegouMensagem(Evento):
    """Classe que representa uma chegada de mensagem da camada superior."""

    def __init__(self, cor, maquina):
        self.cor = cor
        self.maquina = maquina
        self.num_quadros = maquina.num_quadros()
        

    def processar(self, simulador):
        print "- Evento: ChegouMensagem com %d quadros em t=%f na maquina=%s" % (
            self.num_quadros, simulador.tempo_agora, self.maquina.hostname )

        #adiciona na estatistica (TEMP)
        simulador.tempo_chegada.adicionar_amostra(simulador.tempo_agora)
        simulador.tempo_chegada.adicionar_intervalo(simulador.tempo_chegada.intervalo_de_confianca())

        #gera próximo evento
        simulador.eventos.adicionar(
            simulador.tempo_agora + self.maquina.chegada(),
            ChegouMensagem(self.cor, self.maquina)
        )

        fila_vazia = (len(self.maquina.fila) == 0)

        #adiciona mensagem à fila de envio
        self.maquina.fila.append(
            Mensagem(self.cor, self.num_quadros)
        )

        if fila_vazia:
            self.maquina.tentar_enviar(simulador)

class InicioDeEnvio(Evento):
    """ """
    
    def __init__(self, maquina):
        self.maquina = maquina

    def processar(self, simulador):
        print "- Evento: InicioDeEnvio :D t=%f maquina=%s" % (
            simulador.tempo_agora, self.maquina.hostname )
        

######################################################################

class Simulador(object):
    """Classe principal que encapsula um simulador."""

    def __init__(self, hosts, tempo_minimo_ocioso):
        """Parâmetros:
        hosts = Lista de máquinas conectadas ao hub."""
        self.hosts = hosts
        self.tempo_minimo_ocioso = tempo_minimo_ocioso
        self.eventos = HeapDeEventos()
        self.tempo_agora = 0

    def start(self, rodada):
        """Inicializa o simulador, gerando os eventos iniciais"""
        self.rodada_atual = rodada

        for maquina in self.hosts:
            if callable(maquina.chegada):
                self.eventos.adicionar(
                    maquina.chegada(),
                    ChegouMensagem(self.rodada_atual, maquina)
                )

    def run(self):
        self.tempo_chegada = Estatisticas()

        """Executa uma rodada da simulação"""
        for iteracao in xrange(100): #*** TODO: COLOCAR UM CRITERIO DE PARADA DECENTE
            #retirar evento da fila
            self.tempo_agora, evento = self.eventos.remover()

            #processar evento
            evento.processar(self)

        print "Média dos tempos = %f" % self.tempo_chegada.media()
        print "IC dos tempos = %f" % self.tempo_chegada.intervalo_de_confianca()
        self.tempo_chegada.plot()
            
