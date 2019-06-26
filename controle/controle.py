#! -*- coding: utf-8 -*-
from peewee import *
import datetime
import time
from threading import Thread
from configuracao.config import Configuracao
from comunicacao.nbservidor import ConexaoThread
from db.modelos import Persistir
from util.util import DataConv, Log
from servico.servico import Gestao_download

class ControleApp:

    TIPO_ERRO = 'erro'
    TIPO_SUCESSO = 'sucesso'

    def __init__(self):
        self._config = Configuracao()
        self._gestao_d = Gestao_download()
        self._loop_controle = True
        self._thread_conexao_servidores = []
        self._thread_controle = {}
        self._iniciar_threads()


    def _iniciar_threads(self):
        self._loop_controle = True

        self._verificacao_servidores = 'verificacao_servidores'
        verf_conex_serv = Thread(target=self._monitor_conexao_servidores, name=self._verificacao_servidores)
        verf_conex_serv.start()
        self._thread_controle[self._verificacao_servidores] = verf_conex_serv
        Log.info('Iniciando Thread: {}'.format(self._verificacao_servidores))

        self._verifica_bkps_prontos = 'verifica_bkps_prontos'
        verifica_bkps_prontos = Thread(target=self._verificar_bkps_prontos, name=self._verifica_bkps_prontos)
        verifica_bkps_prontos.start()
        self._thread_controle[self._verifica_bkps_prontos] = verifica_bkps_prontos
        Log.info('Iniciando Thread: {}'.format(self._verifica_bkps_prontos))

        self._verifica_download_concluido = 'monitor_bkps_finalizados'
        monitor_download_concluido = Thread(target=self._monitor_download_concluido, name=self._verifica_download_concluido)
        monitor_download_concluido.start()
        self._thread_controle[self._verifica_download_concluido] = monitor_download_concluido
        Log.info('Iniciando Thread:{}'.format(self._verifica_download_concluido))

        self._monitor_download_finalizado = 'monitor_download_finalizados'
        monitor_download_finalizados = Thread(target=self._fecha_ftp_servidor, name=self._monitor_download_finalizado)
        monitor_download_finalizados.start()
        self._thread_controle[self._monitor_download_finalizado] = monitor_download_finalizados
        Log.info('Iniciando Thread: {}'.format(self._monitor_download_finalizado))

        self._monitor_download_andamento = 'monitor_download_andamento'
        monitor_download_andamento = Thread(target=self._monitor_execucao_download, name=self._monitor_download_andamento)
        monitor_download_andamento.start()
        self._thread_controle[self._monitor_download_andamento] = monitor_download_andamento
        Log.info('Iniciando Thread: {}'.format(self._monitor_download_andamento))

    def _reiniciar_threads(self):
        Log.info('reiniciando thread')
        self._loop_controle = False
        time.sleep(60)
        self._iniciar_threads()

    def set_data(self, data):
        self._data = data
        self._decode_data(self._data)

    def _decode_data(self, data):
        if data:
            self._mensagem = data.decode('utf-8')

    def is_data(self):
        is_data = True
        if not self._data:
            is_data = False

        return is_data

    def processar_mensagem(self):
        data_json = json.loads(self._data.decode('utf-8'))
        print('data_json: {}'.format(data_json))
        comando = data_json['comando']
        del data_json['comando']

        if comando == 'lst_bkps_update':
            self._atualizar_lst_bkps(data_json)
            self._atualizar_servidores(data_json)
        else:
            print('comando nao encontrado')

    def _atualizar_lst_bkps(self, data_json):

        if self._config.salvar_servidores(data_json):
                self._resposta = self._criar_resposta(TIPO_SUCESSO, 'sucesso')
        else:
            self._resposta = self._criar_resposta(TIPO_ERRO, 'erro')

    def _atualizar_servidores(self, data_json):
        keys = data_json.keys()
        for key in keys:
            str_servidor = data_json[key]
            servidor = Servidor(str_servidor)
            mensagem = {
            'comando':'update_lst_bkp',
            'backups':servidor.backups
            }
        
            self._enviar_mensagem_servidor(servidor, mensagem)


    def _enviar_mensagem_servidor(self, servidor, mensagem):
        print('---enviar_mensagem----')
        print('servidor: {}'.format(servidor.nome))
        print('mensagem: {}'.format(mensagem))
        thread = ConexaoThread(servidor, mensagem)
        thread.start()
        self._thread_conexao_servidores.append(thread)
        Log.info('enviando mensagem')


    def _verificar_bkps_prontos(self):
        lista_servidores = self._config.get_servidores()
        while self._loop_controle:
            for servidor in lista_servidores:
                tratamento = Tratamento_Servidor(servidor)
                if tratamento.is_execucao() and not self._gestao_d.is_download() and not self.gestao_d.is_em_espera():
                    mensagem = {'comando':'list_bkps_prontos'}
                    self._enviar_mensagem_servidor(servidor, mensagem)

            Log.info('verificação de backups prontos')
            time.sleep(600)

    def _monitor_conexao_servidores(self):
        while self._loop_controle:
            range_lista = len(self._thread_conexao_servidores)
            for thread in self._thread_conexao_servidores:
                if thread.is_comunicacao():
                    self._tratamento_resposta(thread.get_resposta(), thread.get_conteudo(), thread.get_servidor())
                    self._thread_conexao_servidores.remove(thread)
            time.sleep(10)


    def _tratamento_resposta(self, resposta, conteudo, servidor):
        print('---_tratamento_resposta---')
        print('conteudo: {}'.format(conteudo))
        print('servidor: {}'.format(servidor.nome))
        if resposta == 'ok' and resposta == 'ftp_rodando':
            Persistir.transacoes(servidor.nome, resposta, conteudo)
        elif resposta == 'lst_bkps_prontos':
            self._adicionar_download_fila(servidor, conteudo)
        elif resposta == 'salvar_bkps_ok':
            Persistir.transacoes(servidor.nome, resposta)
        elif resposta == 'ftp_pronto_download':
            print('ftp_pronto_download')
            Log.info('ftp pronto para download, servidor {}'.format(servidor.nome))
            self._gestao_d.executa_download(conteudo['conteudo'])


    def _fecha_ftp_servidor(self):
        lista_finalizados = self._gestao_d.get_msg_finalizados()
        for mensagem in lista_finalizados:            
            servidor = mensagem['servidor']
            Log.info('fechando ftp, servidor {}'.format(servidor))
            del mensagem['servidor']
            self._enviar_mensagem_servidor(servidor, mensagem)
            self._gestao_d.remove_finalizado(mensagem['nome'])

    def _monitor_execucao_download(self):
        while self._loop_controle:
            if self._gestao_d.get_downloads_executando() == 0:
                comando = self._gestao_d.get_msg_em_espera()
                if comando != None:
                    servidor = comando['servidor']
                    mensagem = comando['mensagem']
                    self._enviar_mensagem_servidor(servidor, mensagem)
            time.sleep(60)



    def _adicionar_download_fila(self, servidor, conteudo):
        self._gestao_d.adicionar(servidor, conteudo)

    def _monitor_download_concluido(self):
        while self._loop_controle:
            for mensagem in self._gestao_d.get_msg_finalizados():
                self._enviar_mensagem_servidor(mensagem['servidor'], mensagem['comando'])
                self._gestao_d.remove_finalizado(mensagem['comando']['nome'])


            time.sleep(60)

    def _byte_to_json(self):

        return json.loads(self._data.decode('utf-8'))

    def _criar_resposta(self, tipo, mensagem):
        dict = {
            tipo:mensagem
        }

        return json.dumps(dict)

    def enviar_resposta(self):
        return self._resposta.encode('utf-8')


class Tratamento_Servidor:

    def __init__(self, servidor):
        self._servidor = servidor
        self._is_execucao = False
        self._selecionar_tratamento()


    def _selecionar_tratamento(self):
        lista_bkps = self._servidor.obj_backups

        for backups in lista_bkps:
            if backups.periodo == 'diario':
                self._execucao_diaria(backups)
            elif backups.periodo == 'semanal':
                self._execucao_semanal(backups)


    def _execucao_diaria(self, backups):
        if self._is_hora_execucao(backups):
            self._is_execucao = True

    def _execucao_semanal(self, backups):
        if backups.dia_semana == DataConv.hoje_dia_semana() and self._is_hora_execucao(backups):
            self._is_execucao = True

    def is_execucao(self):
        return self._is_execucao

    def _is_hora_execucao(self, backups):
        return DataConv.hora_agora() >= DataConv.str_to_time(backups.hora_execucao)
