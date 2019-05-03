import socket


class Cliente:
    
    def __init__(self, host, porta):
        self._host = host
        self._porta = porta
        addr = (self._host, self._porta)
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.connect(addr)


    def enviar_mensagem(self, mensagem):
        msg_encode =  mensagem.encode()
        self._client_socket.sendall(msg_encode)

    def receber_mensagem(self):
        msg = self._client_socket.recv(1024)

        return msg.decode()

    def fechar_conexao(self):
        self._client_socket.close()
