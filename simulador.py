# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import numpy
import random
import heapq
import sys

import matplotlib.pyplot as pyplot
import math

######################################################################
# Função de impressão, para debug
def debug_print(string):
    #print string
    pass

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
        if len(self.amostras) == 0: return

        if len(self.amostras) != len(self.intervalos):
            plot = pyplot.plot(self.amostras)
        else:
            x = numpy.arange(1, self.num_amostras+1)
            pyplot.errorbar(x, self.amostras, yerr=self.intervalos)

        #pyplot.title(titulo)
        #pyplot.legend(plot, "best", titulo)
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
        if self.num_amostras < 2:
            return 0

        t_student_95 = 1.645
        return 2 * t_student_95 * math.sqrt(self.variancia() / self.num_amostras)

    def precisao_suficiente(self):
        if self.num_amostras < 2:
            return False

        return self.intervalo_de_confianca() < 0.1 * self.media()
        


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

    def __init__(self, rodada, num_quadros):
        self.rodada = rodada
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
        self.distancia = distancia
        self.chegada = chegada
        #self.num_quadros = num_quadros
        self.fila = [] #fila de mensagens
        self.proximo_quadro = 0
        self.tentativas_de_transmissao = 0
        self.tempo_considerar_envio_quadro = -1
        self.tempo_comeco_envio_quadro = -1
        self.tempo_comeco_envio_mensagem = -1
        self.uso_do_meio = 0
        self.tempo_comeco_ocioso = -10000
        self.enviando = False
        self.agendado = False

        self.tap_global = Estatisticas()
        self.tam_global = Estatisticas()
        self.ncm_global = Estatisticas()
        self.vazao_global = Estatisticas()

        self.tap_global_media = Estatisticas()
        self.tam_global_media = Estatisticas()
        self.ncm_global_media = Estatisticas()
        self.vazao_global_media = Estatisticas()

        self.reiniciar_estatisticas()

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


    def precisao_suficiente(self):
        return self.tap_global.precisao_suficiente() and self.tam_global.precisao_suficiente() and self.ncm_global.precisao_suficiente() and self.vazao_global.precisao_suficiente()


    def reiniciar_estatisticas(self):
        #self.tempo_meio_ocioso_total = 0
        #self.tempo_meio_ocupado_total = 0
        #self.tempo_mudanca_estado_meio = 0;

        self.tap_rodada = Estatisticas()
        self.tam_rodada = Estatisticas()
        self.ncm_rodada = Estatisticas()
        self.vazao_rodada = Estatisticas()


    def finalizar_rodada(self):
        self.tap_global.adicionar_amostra(self.tap_rodada.media())
        print "media %s tap = %d" % (self.hostname, self.tap_rodada.media())
        self.tap_global_media.adicionar_amostra(self.tap_global.media())
        self.tap_global_media.adicionar_intervalo(self.tap_global.intervalo_de_confianca())

        self.tam_global.adicionar_amostra(self.tam_rodada.media())
        self.tam_global_media.adicionar_amostra(self.tam_global.media())
        self.tam_global_media.adicionar_intervalo(self.tam_global.intervalo_de_confianca())

        self.ncm_global.adicionar_amostra(self.ncm_rodada.media())
        self.ncm_global_media.adicionar_amostra(self.ncm_global.media())
        self.ncm_global_media.adicionar_intervalo(self.ncm_global.intervalo_de_confianca())

        self.vazao_global.adicionar_amostra(self.vazao_rodada.media())
        self.vazao_global_media.adicionar_amostra(self.vazao_global.media())
        self.vazao_global_media.adicionar_intervalo(self.vazao_global.intervalo_de_confianca())


    def tentar_enviar(self, simulador):
        debug_print("tentar_enviar maquina=%s tentativas=%d tco=%f" % (self.hostname, self.tentativas_de_transmissao, self.tempo_comeco_ocioso))

        if len(self.fila) == 0: return #nada a transmitir
        if self.enviando: return
        if self.agendado: return

        if self.uso_do_meio == 0: #meio livre
            #binary backoff
            k = self.tentativas_de_transmissao
            if k > 10: k = 10
            tempo_atraso = random.randint(0, (2 ** k) - 1) * simulador.tempo_fatia_backoff

            tempo_envio = max(simulador.tempo_agora + tempo_atraso, self.tempo_comeco_ocioso + simulador.tempo_minimo_ocioso)
            if self.tentativas_de_transmissao == 0:
                #setar tempo de acesso na primeira tentativa somente
                self.tempo_considerar_envio_quadro = tempo_envio

                if self.proximo_quadro == 0:
                    self.tempo_considerar_envio_mensagem = tempo_envio

            debug_print("              agendei para t=%f" % (tempo_envio))

            simulador.eventos.adicionar(
                tempo_envio,
                InicioDeEnvio(self)
            )
            self.agendado = True
        else:
            if self.tentativas_de_transmissao == 0:
                #setar tempo de acesso na primeira tentativa somente
                self.tempo_considerar_envio_quadro = simulador.tempo_agora

            #evento de ComecoDeEnvio será tratado no FimDeRecebimento

    def andar_fila(self):
        self.proximo_quadro += 1
        if self.proximo_quadro == self.fila[0].num_quadros:
            #mensagem enviada por completo; retira da fila
            self.proximo_quadro = 0
            self.fila.pop(0)


    def checar_jam(self, simulador):
        if self.uso_do_meio != 0 and self.enviando and not self.fim_de_envio.cancelado: #colisao
            debug_print("  *** COLISAO DETECTADA ***")

            #cancelar FimDeEnvio do quadro
            self.fim_de_envio.cancelado = True
            
            #agendar FimDeEnvio do Jam
            simulador.eventos.adicionar(
                simulador.tempo_agora + simulador.tempo_reforco_jam,
                FimDeEnvio(self.fim_de_envio.rodada, maquina = self, sou_jam = True)
            )

            #verificar quantidade de tentativas de transmissao
            if self.tentativas_de_transmissao == 16:
                #descartar quadro
                self.andar_fila()
                #simulador.perdidos += 1
                #simulador.totais += 1
            
            #tentará enviar o quadro novamente no FimDeEnvio do jam


class Hub(object):
    """Classe que representa um Hub, só serve pra ter um nome e ajudar no Debug"""

    def __init__(self):
        self.hostname = "Hub"


# valor especial que representa o hub no campo "maquina" dos eventos
HUB = Hub() 


######################################################################
# Eventos

class Evento(object):
    """Classe abstrata que representa um evento."""

    def processar(self, simulador):
        raise NotImplementedError()    

        
class ChegouMensagem(Evento):
    """Classe que representa uma chegada de mensagem da camada superior."""

    def __init__(self, rodada, maquina):
        self.rodada = rodada
        self.maquina = maquina
        self.num_quadros = maquina.num_quadros()
        
    def processar(self, simulador):
        debug_print("- Evento: ChegouMensagem com %d quadros em t=%f na maquina=%s" % (
            self.num_quadros, simulador.tempo_agora, self.maquina.hostname ))

        #adiciona na estatistica (TEMP)
        #simulador.tempo_chegada.adicionar_amostra(simulador.tempo_agora)
        #simulador.tempo_chegada.adicionar_intervalo(simulador.tempo_chegada.intervalo_de_confianca())

        #gera próximo evento
        simulador.eventos.adicionar(
            simulador.tempo_agora + self.maquina.chegada(),
            ChegouMensagem(simulador.rodada_atual, self.maquina)
        )

        fila_vazia = (len(self.maquina.fila) == 0)

        #adiciona mensagem à fila de envio
        self.maquina.fila.append(
            Mensagem(self.rodada, self.num_quadros)
        )

        if fila_vazia:
            self.maquina.tentar_enviar(simulador)


class InicioDeEnvio(Evento):
    """ """
    
    def __init__(self, maquina):
        self.maquina = maquina

    def processar(self, simulador):
        debug_print("- Evento: InicioDeEnvio em t=%f maquina=%s quadro=%d" % (
            simulador.tempo_agora, self.maquina.hostname, self.maquina.proximo_quadro ))

        #verifica mensagem na fila de envio
        #(ela só será removida de fato no FimDeEnvio com sucesso)
        mensagem = self.maquina.fila[0]
        
        #gera evento de FimDeEnvio e o salva
        fim_de_envio = FimDeEnvio(mensagem.rodada, self.maquina)
        simulador.eventos.adicionar(
            simulador.tempo_agora + simulador.tempo_transmissao_quadro,
            fim_de_envio
        )
        self.maquina.fim_de_envio = fim_de_envio

        #gera evento de InicioDeRecebimento no hub
        simulador.eventos.adicionar(
            simulador.tempo_agora + (self.maquina.distancia * simulador.tempo_propagacao),
            InicioDeRecebimento(mensagem.rodada, HUB, self.maquina)
        )

        #atualiza estado da máquina
        self.maquina.tentativas_de_transmissao += 1
        self.maquina.tempo_comeco_envio_quadro = simulador.tempo_agora
        self.maquina.enviando = True
        self.maquina.agendado = False

        self.maquina.checar_jam(simulador)


class FimDeEnvio(Evento):
    """ """

    def __init__(self, rodada, maquina, sou_jam = False):
        self.rodada = rodada
        self.maquina = maquina
        self.cancelado = False
        self.sou_jam = sou_jam

    def processar(self, simulador):
        if self.cancelado: return

        if self.sou_jam:
            debug_print("- Evento: FimDeEnvio (Jam) em t=%f na maquina=%s" % (
                simulador.tempo_agora, self.maquina.hostname ))
        else:
            debug_print("- Evento: FimDeEnvio (Quadro) em t=%f na maquina=%s" % (
                simulador.tempo_agora, self.maquina.hostname ))

        #gera evento de FimDeRecebimento no hub
        simulador.eventos.adicionar(
            simulador.tempo_agora + (self.maquina.distancia * simulador.tempo_propagacao),
            FimDeRecebimento(self.rodada, HUB, self.maquina)
        )

        if not self.sou_jam:
            #debug_print("     TAp = %f" % (self.maquina.tempo_comeco_envio_quadro - self.maquina.tempo_considerar_envio_quadro))

            #coleta estatisticas (se rodada valida)
            if self.rodada == simulador.rodada_atual:
                self.maquina.tap_rodada.adicionar_amostra(self.maquina.tempo_comeco_envio_quadro - self.maquina.tempo_considerar_envio_quadro)
                #if self.rodada >0: print "adicionando amostra %d (media=%d)" % ((self.maquina.tempo_comeco_envio_quadro - self.maquina.tempo_considerar_envio_quadro), self.maquina.tap_rodada.media())

            #reiniciar estado de envio de quadro da máquina
            self.maquina.tentativas_de_transmissao = 0
            
            #incrementar proximo quadro a enviar
            self.maquina.andar_fila()

            #simulador.totais += 1
            

        #tentar enviar próximo quadro (agendar para daqui a 9.6us)
        self.maquina.enviando = False
        self.maquina.tempo_comeco_ocioso = simulador.tempo_agora
        self.maquina.tentar_enviar(simulador)


class InicioDeRecebimento(Evento):
    """ """

    def __init__(self, rodada, maquina, maquina_origem):
        self.rodada = rodada
        self.maquina = maquina
        self.maquina_origem = maquina_origem

    def processar(self, simulador):
        debug_print("- Evento: InicioDeRecebimento em t=%f na maquina=%s, origem=%s" % (
            simulador.tempo_agora, self.maquina.hostname, self.maquina_origem.hostname ))

        if self.maquina == HUB:
            for maquina in simulador.hosts:
                #gera evento de InicioDeRecebimento nas maquinas
                simulador.eventos.adicionar(
                    simulador.tempo_agora + (maquina.distancia * simulador.tempo_propagacao),
                    InicioDeRecebimento(self.rodada, maquina, self.maquina_origem)
                )
        else:
            #coletar tempo ocioso
            #self.maquina.tempo_meio_ocioso_total += (simulador.tempo_agora - self.maquina.tempo_mudanca_estado_meio)
            #self.maquina.tempo_mudanca_estado_meio = simulador.tempo_agora

            if self.maquina != self.maquina_origem:
                self.maquina.uso_do_meio += 1
                self.maquina.checar_jam(simulador)

            debug_print("            uso do meio agora = %d" % self.maquina.uso_do_meio)
        

class FimDeRecebimento(Evento):
    """ """

    def __init__(self, rodada, maquina, maquina_origem):
        self.rodada = rodada
        self.maquina = maquina
        self.maquina_origem = maquina_origem

    def processar(self, simulador):
        debug_print("- Evento: FimDeRecebimento em t=%f na maquina=%s, origem = %s" % (
            simulador.tempo_agora, self.maquina.hostname, self.maquina_origem.hostname ))

        if self.maquina == HUB:
            for maquina in simulador.hosts:
                #gera evento de FimDeRecebimento nas maquinas
                simulador.eventos.adicionar(
                    simulador.tempo_agora + (maquina.distancia * simulador.tempo_propagacao),
                    FimDeRecebimento(self.rodada, maquina, self.maquina_origem)
                )
        else:
            #coletar tempo ocupado
            #self.maquina.tempo_meio_ocupado_total += (simulador.tempo_agora - self.maquina.tempo_mudanca_estado_meio)
            #self.maquina.tempo_mudanca_estado_meio = simulador.tempo_agora

            if self.maquina != self.maquina_origem:
                self.maquina.uso_do_meio -= 1
                if self.maquina.uso_do_meio == 0:
                    self.maquina.tempo_comeco_ocioso = simulador.tempo_agora

            debug_print("            uso do meio agora = %d" % self.maquina.uso_do_meio)

            self.maquina.tentar_enviar(simulador)

######################################################################

class Simulador(object):
    """Classe principal que encapsula um simulador."""

    def __init__(self, hosts, tempo_minimo_ocioso, tempo_transmissao_quadro,
                              tempo_propagacao, tempo_reforco_jam, tempo_fatia_backoff,
                              eventos_fase_transiente=50000, eventos_por_rodada=50000):
        """Parâmetros:
        hosts = Lista de máquinas conectadas ao hub."""
        self.hosts = hosts
        self.tempo_minimo_ocioso = tempo_minimo_ocioso
        self.tempo_transmissao_quadro = tempo_transmissao_quadro
        self.tempo_propagacao = tempo_propagacao
        self.tempo_reforco_jam = tempo_reforco_jam
        self.tempo_fatia_backoff = tempo_fatia_backoff

        self.eventos_fase_transiente = eventos_fase_transiente
        self.eventos_por_rodada = eventos_por_rodada

        self.eventos = HeapDeEventos()
        self.tempo_agora = 0

    def start(self):
        """Inicializa o simulador, gerando os eventos iniciais"""
        for maquina in self.hosts:
            if callable(maquina.chegada):
                self.eventos.adicionar(
                    maquina.chegada(),
                    ChegouMensagem(0, maquina)
                )

    def run(self):
        self.utilizacao_global = Estatisticas()
        self.utilizacao_global_media = Estatisticas()

        self.tempo_ocupado_total = 0
        self.tempo_comeco_rodada = self.tempo_agora
        self.tempo_ultimo = self.tempo_agora

        self.rodada_atual = 0

        #while True:
        for bla in xrange(20):
            #condição de parada
            if self.rodada_atual > 0:
                precisao_suficiente = True
                for host in self.hosts:
                    if host.chegada != None:
                        precisao_suficiente = precisao_suficiente and host.precisao_suficiente()

                if precisao_suficiente:
                    break

            if self.rodada_atual == 0:
                eventos_rodada = self.eventos_fase_transiente
            else:
                eventos_rodada = self.eventos_por_rodada

            for host in self.hosts:
                host.reiniciar_estatisticas()

            """Executa uma rodada da simulação"""
            for iteracao in xrange(eventos_rodada):
                #retirar evento da fila
                self.tempo_agora, evento = self.eventos.remover()

                #atualizar estatistica de utilizaçao
                if self.hosts[0].enviando or self.hosts[0].uso_do_meio > 0:
                    self.tempo_ocupado_total += self.tempo_agora - self.tempo_ultimo

                self.tempo_ultimo = self.tempo_agora

                #processar evento
                evento.processar(self)

                #coletar utilizacao ethernet
                if self.tempo_agora > self.tempo_comeco_rodada:
                    self.utilizacao_rodada = self.tempo_ocupado_total / (self.tempo_agora - self.tempo_comeco_rodada)


            #adicionar amostras
            if self.rodada_atual > 0:
                self.utilizacao_global.adicionar_amostra(self.utilizacao_rodada)
                self.utilizacao_global_media.adicionar_amostra(self.utilizacao_global.media())
                self.utilizacao_global_media.adicionar_intervalo(self.utilizacao_global.intervalo_de_confianca())

                for host in self.hosts:
                    host.finalizar_rodada()
                
                print "Rodada %d" % self.rodada_atual
                print "- Media da utilizacao Ethernet = %f / IC = %f" % (self.utilizacao_global.media(), self.utilizacao_global.intervalo_de_confianca())
                for i in range(4):
                    if self.hosts[i].chegada != None:
                        print "- Media do TAp(%d) = %f / IC = %f" % (i+1, self.hosts[i].tap_global.media(), self.hosts[i].tap_global.intervalo_de_confianca())


            #print "Média TAp(1) da rodada %d = %f" % (self.rodada_atual, self.hosts[0].tap_rodada.media())

            self.rodada_atual += 1
            
        #plotar estatisticas
        self.utilizacao_global_media.plot()