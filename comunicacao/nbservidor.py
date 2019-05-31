# -*- coding: utf-8 -*-
import socket
import json
import time
from util.util import Log
from threading import Thread

class ConexaoThread(Thread):

    def __init__(self, servidor, mensagem):
        Thread.__init__(self, name=servidor.nome)
        self._servidor = servidor
        self._conexao = Conexao(servidor.host, servidor.porta, mensagem)
        self._resposta = None
        self._conteudo = None
        self._is_comunicacao = False        

    def run(self):
        if self._conexao.is_conectado():
            self._conexao.enviar_mensagem()
            self._processar_mensagem(self._conexao.receber_mensagem())
            self._conexao.fechar_conexao()
            self._is_comunicacao = True
            

    def is_comunicacao(self):
        return self._is_comunicacao

    def _processar_mensagem(self, mensagem):
        _json = json.loads(mensagem)
        self._resposta = _json['resposta']
        del _json['resposta']
        if self._resposta == 'ok':
            self._conteudo = None
        else:
            self._conteudo = _json

    def get_resposta(self):
        return self._resposta

    def get_conteudo(self):
        return self._conteudo

    def get_servidor(self):
        return self._servidor


class Conexao:

    def __init__(self, host, porta, mensagem):
        self._host = host
        self._porta = porta
        self._mensagem = mensagem
        self._addr = (self._host, self._porta)
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def is_conectado(self):
        try:
            self._client_socket.connect(self._addr)
            resposta = True
        except socket.error:
            resposta = False

        return resposta

    def enviar_mensagem(self):
        msg_encode =  json.dumps(self._mensagem).encode('utf-8')
        self._client_socket.sendall(msg_encode)
        Log.info('pacote enviado, host:{}'.format(self._host))


    def receber_mensagem(self):
        msg = self._client_socket.recv(4096)
        Log.info('mensagem recebida, host: {}'.format(self._host))
        return msg.decode('utf-8')

    def fechar_conexao(self):
        self._client_socket.close()
