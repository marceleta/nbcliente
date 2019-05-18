#! -*- coding: utf-8 -*-
from peewee import *
import datetime
import time
from threading import Thread
from configuracao.config import Configuracao
from comunicacao.nbservidor import ConexaoThread
from db.modelos import Persistir
from util.util import DataConv
from servico.servico import Gestao_download

class ControleApp:

    TIPO_ERRO = 'erro'
    TIPO_SUCESSO = 'sucesso'

    def __init__(self):
        self._config = Configuracao()
        self._gestao_d = Gestao_download()
        self._loop_controle = True
        self._thread_conexao_servidores = {}
        self._thread_controle = {}
        self._iniciar_threads()


    def _iniciar_threads(self):
        self._loop_controle = True

        self._verificacao_servidores = 'verificacao_servidores'
        verf_conex_serv = Thread(target=self._monitor_conexao_servidores, name=self._verificacao_servidores)
        verf_conex_serv.start()
        self._thread_controle[self._verificacao_servidores] = verf_conex_serv

        self._verifica_bkps_prontos = 'verifica_bkps_prontos'
        verifica_bkps_prontos = Thread(target=self._verificar_bkps_prontos, name=self._verifica_bkps_prontos)
        verifica_bkps_prontos.start()
        self._thread_controle[self._verifica_bkps_prontos] = verifica_bkps_prontos

        self._verifica_download_concluido = 'monitor_bkps_finalizados'
        monitor_download_concluido = Thread(target=self._monitor_download_concluido, name=self._verifica_download_concluido)
        monitor_download_concluido.start()
        self._thread_controle[self._verifica_download_concluido] = monitor_download_concluido

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
        comando = data_json['comando']
        del data_json['comando']
        print('comando: {}'.format(comando))

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
        thread = ConexaoThread(servidor, mensagem)
        thread.start()
        self._thread_conexao_servidores[servidor.nome] = thread


    def _verificar_bkps_prontos(self):
        lista_servidores = self._config.get_servidores()
        while self._loop_controle:
            print('lista_servidores: {}'.format(lista_servidores))
            for servidor in lista_servidores:
                tratamento = Tratamento_Servidor(servidor)
                print('servidor: {} is_execucao: {}'.format(servidor.nome, tratamento.is_execucao()))
                if tratamento.is_execucao():
                    mensagem = {'comando':'list_bkps_prontos'}
                    print('enviar_mensagem')
                    self._enviar_mensagem_servidor(servidor, mensagem)

            time.sleep(60)

    def _monitor_conexao_servidores(self):
        while self._loop_controle:
            lista_conexoes = list(self._thread_conexao_servidores.keys())
            print('lista_conexoes: {}'.format(lista_conexoes))
            for key in lista_conexoes:
                thread = self._thread_conexao_servidores[key]
                print('servidor: {}'.format(key))
                print('thread.is_alive() {}'.format(thread.is_alive()))
                if not thread.is_alive():
                    print('thread.is_alive(): {}'.format(thread.is_alive()))
                    print('thread.is_comunicacao(): {}'.format(thread.is_comunicacao()))
                    if thread.is_comunicacao():
                        self._tratamento_resposta(thread.get_resposta(), thread.get_conteudo(), thread.get_servidor())
                        print('registrar comunicacao bem sucedida')
                    else:
                        print('registrar erro comunicacao')
                    del self._thread_conexao_servidores[key]

            time.sleep(60)

    def _tratamento_resposta(self, resposta, conteudo, servidor):

        if resposta == 'ok':
            Persistir.config_enviadas(servidor.nome, resposta)
        elif resposta == 'lst_bkps_prontos':
            self._abertura_ftp_servidor(servidor, conteudo)
        elif resposta == 'salvar_bkps_ok':
            Persistir.config_enviadas(servidor.nome, resposta)
        elif resposta == 'ftp_pronto_download':
            self._gestao_d.executa_download(resposta)

    def _abertura_ftp_servidor(self, servidor, conteudo):
        self._gestao_d.adicionar(servidor, conteudo)
        lista_resposta = self._gestao_d.get_msg_em_espera()
        for resposta in lista_resposta:
            print('abertuta_ftp_servidor:resposta: {}'.format(resposta))
            self._enviar_mensagem_servidor(servidor, resposta)

    def _monitor_download_concluido(self):

        while self._loop_controle:
            for mensagem in self._gestao_d.get_msg_finalizados():
                self._enviar_mensagem_servidor(mensagem['servidor'], mensagem['comando'])

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
                print('diario')
                self._execucao_diaria(backups)
            elif backups.periodo == 'semanal':
                print('semanal')
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
        print('str_to_time: {}'.format(DataConv.str_to_time(backups.hora_execucao)))
        print('DataConv.hora_agora() {}'.format(DataConv.hora_agora()))
        return DataConv.hora_agora() >= DataConv.str_to_time(backups.hora_execucao)
