# -*- coding: utf-8 -*-
import socket
import json
import time
from threading import Thread

class ConexaoThread(Thread):

    def __init__(self, host, porta, mensagem, nome_thread=None):
        Thread.__init__(self, name=nome_thread)
        self._conexao = Conexao(host, porta, mensagem)
        self._resposta = None

    def run(self):
        if self._conexao.is_conectado():
            self._conexao.enviar_mensagem()
            self._resposta = self._conexao.receber_mensagem()
            self._conexao.fechar_conexao()

    def get_mensagem(self):
        return self._resposta


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
        msg_encode =  self._mensagem.encode()
        self._client_socket.sendall(msg_encode)

    def receber_mensagem(self):
        msg = self._client_socket.recv(1024)
        return msg.decode()

    def fechar_conexao(self):
        self._client_socket.close()
