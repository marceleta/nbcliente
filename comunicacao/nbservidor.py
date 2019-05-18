# -*- coding: utf-8 -*-
import socket
import json
import time
from threading import Thread

class ConexaoThread(Thread):

    def __init__(self, servidor, mensagem):
        Thread.__init__(self, name=servidor.nome)
        self._servidor = servidor
        self._conexao = Conexao(servidor.host, servidor.porta, mensagem)
        self._resposta = None
        self._conteudo = None
        self._is_conectado = False

    def run(self):
        if self._conexao.is_conectado():
            self._is_conectado = True
            self._conexao.enviar_mensagem()
            self._processar_mensagem(self._conexao.receber_mensagem())
            self._conexao.fechar_conexao()

    def is_comunicacao(self):
        return self._is_conectado

    def _processar_mensagem(self, mensagem):
        _json = json.loads(mensagem)
        self._resposta = _json['resposta']
        del _json['resposta']
        self._conteudo = _json



    def get_resposta(self):
        print('resposta: {}'.format(self._resposta))
        return self._resposta

    def get_conteudo(self):
        print('conteudo {}'.format(self._conteudo))
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

    def receber_mensagem(self):
        msg = self._client_socket.recv(4096)
        return msg.decode('utf-8')

    def fechar_conexao(self):
        self._client_socket.close()
