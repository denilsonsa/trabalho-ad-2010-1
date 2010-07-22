# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import heapq
import math
import matplotlib.pyplot as pyplot
import numpy
import random
import scipy.stats


######################################################################
# Funções úteis

def debug_print(string):
    """Função de impressão, para debug"""
    #print string
    pass

def exibir_legenda():
    """Exibe a legenda no gráfico"""
    l = pyplot.legend(loc="best", fancybox=True, shadow=True)

    # Fundo cinza
    l.get_frame().set_facecolor("0.90")

    # Tamanho do texto
    for t in l.get_texts():
        t.set_fontsize("x-small")


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

    def __init__(self, titulo=u"Estatísticas"):
        self.amostras = []
        self.intervalos = []
        self.soma_amostras = 0
        self.soma_quadrados = 0
        self.num_amostras = 0
        self.titulo = titulo

    def adicionar_amostra(self, amostra):
        self.amostras.append(amostra)
        self.soma_amostras += amostra
        self.soma_quadrados += amostra*amostra
        self.num_amostras += 1

    def adicionar_intervalo(self, intervalo):
        self.intervalos.append(intervalo)

    def plot(self, *args, **kwargs):
        """Desenha uma linha correspondente às amostras coletadas. Caso
        os intervalos de confiança tenham sido calculados, desenha
        também o tamanho dos intervalos."""

        if len(self.amostras) == 0:
            return

        x = numpy.arange(1, self.num_amostras+1)
        if len(self.amostras) != len(self.intervalos):
            plot = pyplot.plot(x, self.amostras, *args, **kwargs)
        else:
            pyplot.errorbar(x, self.amostras, yerr=self.intervalos, *args, **kwargs)

        #pyplot.title(titulo)
        #pyplot.show()

    def media(self):
        """Retorna a média das amostras"""
        if self.num_amostras == 0:
            return 0

        return self.soma_amostras / self.num_amostras

    def variancia(self):
        """Retorna a variância das amostras"""
        if self.num_amostras < 2:
            return 0

        #ref: http://en.wikipedia.org/wiki/Variance#Population_variance_and_sample_variance
        sq = self.soma_quadrados
        sa = self.soma_amostras
        n = self.num_amostras
        return (sq / (n - 1)) - ((sa * sa) / (n * (n - 1)))

    def intervalo_de_confianca(self):
        """Retorna metade do tamanho do intervalo de confiança, ou seja,
        o intervalo será definido pela média +- o valor retornado por
        esta função"""

        if self.num_amostras < 2:
            return 0

        # 1 - 95% = 5%
        # 5% / 2 = 2.5%
        # 1 - 2.5% = 97.5% = 0.975
        t_student_95 = scipy.stats.t.ppf(0.975, self.num_amostras-1)
        return t_student_95 * math.sqrt(self.variancia() / self.num_amostras)

    def precisao_suficiente(self):
        """Retorna True ou False, indicando se a largura do intervalo de
        confiança é menor que 10% da média das amostras."""

        if self.num_amostras < 2:
            return False

        return 2 * self.intervalo_de_confianca() < self.media() / 10.0


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
    """Classe que representa uma mensagem a ser enviada."""

    def __init__(self, rodada, num_quadros):
        self.rodada = rodada
        self.num_quadros = num_quadros


class Host(object):

    def __init__(self, hostname, distancia, chegada, num_quadros):
        """Recebe os parâmetros do host:
        hostname = Nome da máquina (ignorado pelo simulador)
        dist = Distância deste host ao hub (medida em metros)
        chegada = Processo de chegada das mensagens a ser enviadas
        num_quadros = Distribuição do número de quadros para cada mensagem"""

        self.hostname = hostname
        self.distancia = distancia
        self.chegada = chegada
        # Estes dois campos campos serão definidos mais abaixo
        #self.num_quadros = num_quadros
        #self.ativo = (chegada and num_quadros)

        if callable(num_quadros) or num_quadros is None:
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
                # (determinística) de quadros.
                # Cuidado! Não é tratado o caso do número de quadros ser
                # fracionário!
                self.num_quadros = Deterministica(num_quadros)

        # Um host é considerado ativo se ele gera tráfego. Ou seja, se
        # ele tem uma distribuição de chegada de mensagens e de número
        # de quadros de cada mensagem.
        self.ativo = callable(self.chegada) and callable(self.num_quadros)

    def reset(self):
        """Faz um "reset" no host, reiniciando todas as estatísticas e o
        estado do host. Este método deve ser chamado antes de começar a
        simulação."""

        # Fila de mensagens
        self.fila = []
        # Número do próximo quadro (dentro da mensagem atual) a ser enviado
        self.proximo_quadro = 0

        self.tentativas_de_transmissao = 0
        self.tempo_considerar_envio_quadro = -1
        self.tempo_comeco_envio_quadro = -1
        self.tempo_comeco_envio_mensagem = -1
        self.uso_do_meio = 0
        self.tempo_comeco_ocioso = -100000.0

        # Flag para indicar se o host está enviando algum quadro
        self.enviando = False
        # Flag para indicar se o host está esperando o tempo do binary backoff
        self.agendado = False
        self.contador_colisoes = 0

        self.tap_global = Estatisticas()
        self.tam_global = Estatisticas()
        self.ncm_global = Estatisticas()
        self.vazao_global = Estatisticas()

        self.tap_global_media = Estatisticas()
        self.tam_global_media = Estatisticas()
        self.ncm_global_media = Estatisticas()
        self.vazao_global_media = Estatisticas()

        self.reiniciar_estatisticas()

    def reiniciar_estatisticas(self):
        """Reinicia as estatísticas no início de uma rodada."""

        #self.tempo_meio_ocioso_total = 0
        #self.tempo_meio_ocupado_total = 0
        #self.tempo_mudanca_estado_meio = 0;

        self.tap_rodada = Estatisticas()
        self.tam_rodada = Estatisticas()
        self.ncm_rodada = Estatisticas()

        self.quadros_com_sucesso = 0

    def precisao_suficiente(self):
        """Indica se as estatísticas coletadas neste host já possuem a
        precisão desejada."""

        return (
            self.tap_global.precisao_suficiente() and
            self.tam_global.precisao_suficiente() and
            self.ncm_global.precisao_suficiente() and
            self.vazao_global.precisao_suficiente()
        )

    def finalizar_rodada(self, tempo_rodada):
        """Salva as estatísticas da rodada na estatística global."""

        self.tap_global.adicionar_amostra(self.tap_rodada.media())
        self.tap_global_media.adicionar_amostra(self.tap_global.media())
        self.tap_global_media.adicionar_intervalo(self.tap_global.intervalo_de_confianca())

        self.tam_global.adicionar_amostra(self.tam_rodada.media())
        self.tam_global_media.adicionar_amostra(self.tam_global.media())
        self.tam_global_media.adicionar_intervalo(self.tam_global.intervalo_de_confianca())

        self.ncm_global.adicionar_amostra(self.ncm_rodada.media())
        self.ncm_global_media.adicionar_amostra(self.ncm_global.media())
        self.ncm_global_media.adicionar_intervalo(self.ncm_global.intervalo_de_confianca())

        self.vazao_global.adicionar_amostra(1000000.0 * self.quadros_com_sucesso / tempo_rodada)
        self.vazao_global_media.adicionar_amostra(self.vazao_global.media())
        self.vazao_global_media.adicionar_intervalo(self.vazao_global.intervalo_de_confianca())

    def tentar_enviar(self, simulador):
        debug_print("tentar_enviar maquina=%s tentativas=%d tco=%f" % (self.hostname, self.tentativas_de_transmissao, self.tempo_comeco_ocioso))

        if len(self.fila) == 0: return # Nada a transmitir
        if self.enviando: return
        if self.agendado: return

        if self.uso_do_meio == 0: # Meio livre
            # Binary backoff
            k = self.tentativas_de_transmissao
            if k > 10: k = 10
            tempo_atraso = random.randint(0, (2 ** k) - 1) * simulador.tempo_fatia_backoff

            tempo_envio = max(simulador.tempo_agora + tempo_atraso, self.tempo_comeco_ocioso + simulador.tempo_minimo_ocioso)
            if self.tentativas_de_transmissao == 0:
                # Setar tempo de acesso na primeira tentativa somente
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

    def andar_fila(self, simulador):
        self.proximo_quadro += 1
        if self.proximo_quadro == self.fila[0].num_quadros:
            #estatisticas
            if self.fila[0].rodada == simulador.rodada_atual:
                self.ncm_rodada.adicionar_amostra(1.0 * self.contador_colisoes / self.fila[0].num_quadros)

            self.contador_colisoes = 0

            #mensagem enviada por completo; retira da fila
            self.proximo_quadro = 0
            self.fila.pop(0)


    def checar_jam(self, simulador):
        if self.uso_do_meio != 0 and self.enviando and not self.fim_de_envio.cancelado: #colisao
            debug_print("  *** COLISAO DETECTADA ***")

            self.contador_colisoes += 1

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
                self.andar_fila(simulador)
                #simulador.perdidos += 1
                #simulador.totais += 1

            #tentará enviar o quadro novamente no FimDeEnvio do jam

    def __getstate__(self):
        """Este método é chamado pelo módulo pickle. Este método remove
        as closures e funções lambda, permitindo que o pickle consiga
        salvar este objeto.

        Pickle é um módulo que permite salvar um objeto em um arquivo e
        carregá-lo novamente mais tarde. Neste simulador, é útil para
        poder estudar os dados coletados sem precisar reiniciar a
        simulação.

        Note que não será possível recomeçar a simulação a partir de um
        host carregado através do pickle."""

        d = self.__dict__.copy()
        d["chegada"] = None
        d["num_quadros"] = None
        return d


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

        # Gera o próximo evento
        simulador.eventos.adicionar(
            simulador.tempo_agora + self.maquina.chegada(),
            ChegouMensagem(simulador.rodada_atual, self.maquina)
        )

        fila_vazia = (len(self.maquina.fila) == 0)

        # Adiciona mensagem à fila de envio
        self.maquina.fila.append(
            Mensagem(self.rodada, self.num_quadros)
        )

        # A fila estava vazia quando esta mensagem chegou?
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
                self.maquina.tam_rodada.adicionar_amostra(self.maquina.tempo_comeco_envio_quadro - self.maquina.tempo_considerar_envio_mensagem)
                self.maquina.quadros_com_sucesso += 1

            #reiniciar estado de envio de quadro da máquina
            self.maquina.tentativas_de_transmissao = 0

            #incrementar proximo quadro a enviar
            self.maquina.andar_fila(simulador)

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

        if self.maquina is HUB:
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

        if self.maquina is HUB:
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

    def __init__(self,
            hosts,
            eventos_fase_transiente=50000,
            eventos_por_rodada=50000,
            titulo=u"",
            tempo_minimo_ocioso=9.6,  # Tempo em que o meio tem que ficar ocioso entre transmissões
            tempo_transmissao_quadro=800,  # 8000 bits/quadro / 10 Mbps = 800microseg/quadro
            tempo_propagacao=0.005,  # 5 microseg/km = 0.005 microseg/m
            tempo_reforco_jam=3.2,
            tempo_fatia_backoff=51.2
        ):
        """Recebe todos os parâmetros da simulação."""
        self.hosts = hosts
        self.eventos_fase_transiente = eventos_fase_transiente
        self.eventos_por_rodada = eventos_por_rodada
        self.titulo = titulo

        self.tempo_minimo_ocioso = tempo_minimo_ocioso
        self.tempo_transmissao_quadro = tempo_transmissao_quadro
        self.tempo_propagacao = tempo_propagacao
        self.tempo_reforco_jam = tempo_reforco_jam
        self.tempo_fatia_backoff = tempo_fatia_backoff

    def start(self):
        """Prepara o simulador, inicializando algumas variáveis e
        gerando os eventos iniciais"""

        self.utilizacao_global = Estatisticas()
        self.utilizacao_global_media = Estatisticas()

        self.utilizacao_total = Estatisticas()
        self.tempo_ocupado_total = 0

        self.eventos = HeapDeEventos()
        self.tempo_agora = 0

        for host in self.hosts:
            host.reset()
            if host.ativo:
                self.eventos.adicionar(
                    host.chegada(),
                    ChegouMensagem(0, host)
                )

    def run(self):
        """Executa o loop principal do simulador até conseguir coletar
        as estatísticas com a precisão desejada, e então desenha alguns
        gráficos."""

        # Neste simulador, a rodada zero é considerada a fase transiente
        print "Fase transiente..."
        self.rodada_atual = 0

        while True:
        #for bla in xrange(3):  # DEBUG: Roda só 2 rodadas para testar rapidamente

            # Condição de parada:
            # - não estou na fase transiente
            # - e todos os hosts chegaram à precisão desejada
            # - e a utilização do Ethernet chegou à precisão desejada
            if self.rodada_atual > 0 \
            and all(
                host.precisao_suficiente()
                for host in self.hosts if host.ativo
            ) and self.utilizacao_global_media.precisao_suficiente():
                break

            for host in self.hosts:
                host.reiniciar_estatisticas()

            self.tempo_ocupado_rodada = 0
            self.tempo_comeco_rodada = self.tempo_agora
            self.tempo_evento_anterior = self.tempo_agora

            if self.rodada_atual == 0:
                eventos_rodada = self.eventos_fase_transiente
            else:
                eventos_rodada = self.eventos_por_rodada

            # Executa uma rodada da simulação
            for iteracao in xrange(eventos_rodada):
                # Retirar evento da fila
                self.tempo_agora, evento = self.eventos.remover()

                # Atualizar estatistica de utilização
                # (coletada apenas para a primeira máquina)
                if self.hosts[0].enviando or self.hosts[0].uso_do_meio > 0:
                    self.tempo_ocupado_rodada += self.tempo_agora - self.tempo_evento_anterior
                    self.tempo_ocupado_total += self.tempo_agora - self.tempo_evento_anterior

                self.tempo_evento_anterior = self.tempo_agora

                # Processar evento
                evento.processar(self)

                # Coletar utilização ethernet (de vez em quando)
                if iteracao % 1000 == 0:
                    self.utilizacao_total.adicionar_amostra(self.tempo_ocupado_total / self.tempo_agora)

            # Adicionar amostras
            if self.rodada_atual > 0:
                self.utilizacao_global.adicionar_amostra(self.tempo_ocupado_rodada / (self.tempo_agora - self.tempo_comeco_rodada))
                self.utilizacao_global_media.adicionar_amostra(self.utilizacao_global.media())
                self.utilizacao_global_media.adicionar_intervalo(self.utilizacao_global.intervalo_de_confianca())

                for host in self.hosts:
                    host.finalizar_rodada(self.tempo_agora - self.tempo_comeco_rodada)

                print "Rodada %d" % self.rodada_atual
                print "- Media da utilizacao Ethernet = %f / IC +- %f" % (self.utilizacao_global.media(), self.utilizacao_global.intervalo_de_confianca())
                for i in range(4):
                    if self.hosts[i].chegada != None:
                        print "- Media do TAp(%d)   = %13f / IC +- %13f" % (i+1, self.hosts[i].tap_global.media(), self.hosts[i].tap_global.intervalo_de_confianca())
                        print "- Media do TAm(%d)   = %13f / IC +- %13f" % (i+1, self.hosts[i].tam_global.media(), self.hosts[i].tam_global.intervalo_de_confianca())
                        print "- Media do Ncm(%d)   = %13f / IC +- %13f" % (i+1, self.hosts[i].ncm_global.media(), self.hosts[i].ncm_global.intervalo_de_confianca())
                        print "- Media da Vazao(%d) = %13f / IC +- %13f" % (i+1, self.hosts[i].vazao_global.media(), self.hosts[i].vazao_global.intervalo_de_confianca())


            #print "Média TAp(1) da rodada %d = %f" % (self.rodada_atual, self.hosts[0].tap_rodada.media())

            self.rodada_atual += 1

    def exibir_graficos(self):
        """Exibe na tela os gráficos já gerados."""
        pyplot.show()

    def salvar_graficos(self, filename, dpi=300, size=(7.4, 10.0)):
        """Salva em disco os gráficos já gerados. Por padrão, salva a
        300 DPI no tamanho de uma folha A4 (já desconsiderando as
        margens)."""

        fig = pyplot.gcf()
        fig.set_size_inches(size)

        pyplot.savefig(filename, dpi=dpi)

    def gerar_graficos(self, layout="horizontal"):
        """Gera os 6 gráficos disponíveis, usando layout "horizontal"
        (para tela) ou "vertical" (para impressão)"""

        graficos = [
            # (pos_h, pos_v, função)
            # Onde pos_h é a posição do gráfico no layout horizontal,
            # e pos_v é a posição do gráfico no layout vertical.

            (1, 1, self.gerar_grafico_tap),
            (4, 2, self.gerar_grafico_tam),
            (2, 3, self.gerar_grafico_ncm),
            (5, 4, self.gerar_grafico_vazao),
            (3, 5, self.gerar_grafico_utilizacao),
            (6, 6, self.gerar_grafico_utilizacao_total),
        ]

        if layout == "horizontal":
            rows = 2
            cols = 3
            pos_index = 0
        elif layout == "vertical":
            rows = 3
            cols = 2
            pos_index = 1
        else:
            raise ValueError("Layout desconhecido: '%s'" % layout)

        # Fecha a figura atual (se existir) e cria uma nova
        pyplot.close()
        pyplot.figure()

        # Desenha os 6 gráficos
        for grafico in graficos:
            pyplot.subplot(rows, cols, grafico[pos_index])
            grafico[-1]()  # Chama a função (último elemento da tupla)

        pyplot.suptitle(self.titulo, fontsize="large", fontweight="bold")

    def gerar_grafico_tap(self):
        for host in self.hosts:
            if host.ativo:
                host.tap_global_media.plot(label=host.hostname)
        #exibir_legenda()
        pyplot.grid(True)
        pyplot.title(u"TAp (µs)\ntempo médio de acesso de um quadro", fontsize="small")
        pyplot.xlim([0, self.rodada_atual+1])
        pyplot.xticks(fontsize="x-small")
        pyplot.yticks(fontsize="x-small")

    def gerar_grafico_tam(self):
        for host in self.hosts:
            if host.ativo:
                host.tam_global_media.plot(label=host.hostname)
        #exibir_legenda()
        pyplot.grid(True)
        pyplot.title(u"TAm (µs)\ntempo médio de acesso de uma msg.", fontsize="small")
        pyplot.xlim([0, self.rodada_atual+1])
        pyplot.xticks(fontsize="x-small")
        pyplot.yticks(fontsize="x-small")

    def gerar_grafico_ncm(self):
        for host in self.hosts:
            if host.ativo:
                host.ncm_global_media.plot(label=host.hostname)
        #exibir_legenda()
        pyplot.grid(True)
        pyplot.title(u"NCm\nnúm. médio de colisões por quadro", fontsize="small")
        pyplot.xlim([0, self.rodada_atual+1])
        pyplot.xticks(fontsize="x-small")
        pyplot.yticks(fontsize="x-small")

    def gerar_grafico_vazao(self):
        for host in self.hosts:
            if host.ativo:
                host.vazao_global_media.plot(label=host.hostname)
        exibir_legenda()
        pyplot.grid(True)
        pyplot.title(u"Vazão média (quadros/segundo)", fontsize="small")
        pyplot.xlim([0, self.rodada_atual+1])
        pyplot.xticks(fontsize="x-small")
        pyplot.yticks(fontsize="x-small")

    def gerar_grafico_utilizacao(self):
        self.utilizacao_global_media.plot(label=u"média")
        self.utilizacao_global.plot(marker="x", color="#C04040", label=u"amostras")
        exibir_legenda()
        pyplot.grid(True)
        pyplot.title(u"Utilização do Ethernet (por rodada)", fontsize="small")
        pyplot.xlim([0, self.rodada_atual+1])
        pyplot.xticks(fontsize="x-small")
        pyplot.yticks(fontsize="x-small")

    def gerar_grafico_utilizacao_total(self):
        self.utilizacao_total.plot()
        pyplot.xscale("log")
        pyplot.axvline(self.eventos_fase_transiente/1000, color="red")
        pyplot.annotate(u"Fim da fase transiente",
            xy=(self.eventos_fase_transiente/1000, 0.0625),
            rotation="vertical", size="x-small", ha="right", va="bottom")
        pyplot.grid(True)
        # pyplot.grid(True, which="both") # which option has been added in matplotlib 1.0.0
        pyplot.title(u"Utilização do Ethernet (contínua)", fontsize="small")
        pyplot.xlabel(u"eventos / 1000", fontsize="small");
        pyplot.xticks(fontsize="x-small")
        pyplot.yticks(fontsize="x-small")
