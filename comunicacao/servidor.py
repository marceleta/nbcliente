import socket
import selectors
import logging
import time
import threading
from controle.controle import ControleApp
import sys
#filename='nbackup.log', filemode='a',
#logging.basicConfig(filename='nbackup.log', filemode='a',level=logging.INFO, format='[%(asctime)s %(message)s]')

class Server():

    def __init__(self, host, porta, qtd_conecoes):
        self._host = host
        self._porta = porta
        self._qtd_conecoes = qtd_conecoes


    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def porta(self):
        return self._porta

    @porta.setter
    def porta(self, value):
        self._porta = value

    @property
    def qtd_conecoes(self):
        return self._qtd_conecoes

    @qtd_conecoes.setter
    def qtd_conecoes(self, value):
        self._qtd_conecoes = value

class SelectorServer:

    def __init__(self, host, port, listen):
        self.main_socket = socket.socket()
        self.main_socket.bind((host, port))
        self.main_socket.listen(100)
        self.main_socket.setblocking(False)


        self.selector = selectors.DefaultSelector()
        self.selector.register(fileobj=self.main_socket,
                                events=selectors.EVENT_READ,
                                data=self.on_accept)

        self.current_peers = {}
        self._controle = ControleApp()
        self._server_on_running = True


    def on_accept(self, sock, mask):
        conn, addr = self.main_socket.accept()
        #logging.info('accepted connection from {0}'.format(addr))
        conn.setblocking(False)

        self.current_peers[conn.fileno()] = conn.getpeername()
        self.selector.register(fileobj=conn, events=selectors.EVENT_READ,
                                data=self.on_read)

    def on_read(self, conn, mask):
        try:
            data = conn.recv(1024)
            self._controle.set_data(data)

            if self._controle.is_data():
                self._controle.processar_mensagem()
                #logging.info('recebi dados de: {}'.format(conn.getpeername()))
                conn.send(self._controle.enviar_resposta())
                if self._controle.get_running():
                    self._set_is_running(False)
            else:
                self.close_connection(conn)

        except ConnectionResetError:
            self.close_connection(conn)


    def _set_is_running(self, is_running):
        self._server_on_running = is_running
        self.selector.close()
        sys.exit()

    def close_connection(self, conn):

        peername = self.current_peers[conn.fileno()]
        #logging.info('closing connection to {0}'.format(peername))
        del self.current_peers[conn.fileno()]
        self.selector.unregister(conn)
        conn.close()

    def serve_forever(self):
        last_report_time = time.time()
        #logging.info('Iniciando servidor')
        while self._server_on_running:

            events = self.selector.select(timeout=0.2)

            for key, mask in events:
                handler = key.data
                handler(key.fileobj, mask)


            cur_time = time.time()

            if cur_time - last_report_time > 1:
                #logging.info('Running report...')
                #logging.info('Num active peers = {0}'.format(
                #                len(self.current_peers)))
                last_report_time = cur_time


    def run_server(self):
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.start()
