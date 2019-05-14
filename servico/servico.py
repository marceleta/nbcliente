

class Download_ftp:

    def __init__(self, arquivo, servidor):
        self._servidor = servidor
        self._arquivo = arquivo

    def msg_ftp_servidor(self):
        '''
        Mensagem para enviar ao servidor para abrir FTP
        '''
        comando = {'comando':'iniciar_ftp'}
        comando[self._arquivo['backup']] = ['path':self._arquivo['path'], 'nome':self._arquivo['nome']]

        resposta = json.dumps(comando)
