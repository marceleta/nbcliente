import ftplib
from config import Configuracao
from threading import Thread
import time

class Gestao_download:

    def __init__(self):
        self._loop_gestao = True
        self._thread_gestao = []
        self._download_em_espera = {}
        self._download_em_andamento = []
        self._download_finalizados = []
        self._iniciar_servicos()

    def adicionar(self, servidor, arquivos):
        lista_arquivos = arquivos['arquivos']
        for arquivo in lista_arquivos:
            download_ftp = Download_ftp(arquivo, servidor)
            thread = Download_thread(download_ftp, arquivo['backup'])
            self._download_em_espera[arquivo['backup']] = thread

    def _monitor_downloads_executando(self):
        '''
            monitora que nao mais que nao dois downloads ao mesmo tempo
        '''
        while self._loop_gestao:
            sel._numero_execucoes = 0
            keys = self._download_em_andamento.keys()
            for key in keys:
                thread = self._download_em_andamento[key]
                if thread.is_alive():
                    self._numero_execucoes += 1

            time.sleep(60)

    def executa_download(self, nome_backup):
        thread = self._download_em_espera[nome_backup]
        thread.start()
        self._download_em_andamento.append(thread)

    def _remove_download_finalizado(self):
        while self._loop_gestao:
            if len(self._download_em_andamento) > 0:
                tamanho_lista = len(self._download_em_andamento)
                for index in tamanho_lista:
                    thread = self._download_em_andamento[index]
                    if not thread.is_alive():
                        self._download_finalizados.append(thread)
                        del self._download_em_andamento[index]


    def _iniciar_servicos(self):
        self._loop_gestao = True
        monitor_executando = Thread(target=self._monitor_downloads_executando, name='monitor_executando')
        monitor_executando.start()
        self._thread_gestao.append(monitor_executando)
        monitor_espera = Thread(target=self._monitor_download_espera, name='monitor_espera')
        monitor_espera.start()
        self._thread_gestao.append(monitor_espera)
        monitor_finalizado = Thread(target=self._remove_download_finalizado, name='monitor_finalizados')
        monitor_finalizado.start()
        self._thread_gestao.append(monitor_finalizado)


    def get_msg_em_espera(self):
        lista_espera  = []
        contador = 0
        keys = list(self._download_em_espera.keys())
        while len(self._download_em_andamento) < 2 and len(lista_espera) < 2:
            thread = self._download_em_espera[keys[contador]]
            lista_espera.append(thread.get_download_ftp().msg_abrir_ftp())
            contador += 1

        return lista_espera


    def get_msg_finalizados(self):
        lista_msg = []

        for thread in self._download_finalizados:
            config_ftp = thread.get_download_ftp()
            mensagem = {
                'servidor':config_ftp.get_servidor(),
                'comando':config.msg_fechar_ftp()
            }
            lista_msg.append(mensagem)

        return lista_msg

    def is_executando(self):
        return self._loop_gestao

    def parar_servicos(self):
        self._loop_gestao = False

    def is_servidos_exec(self):
        resposta = False
        for thread in self._thread_gestao:
            resposta = thread.is_alive()

        return resposta



class Download_thread(Thread):

    def __init__(self, download_ftp, nome):
        Thread.__init__(self, name=nome)
        self._download_ftp = download_ftp

    def run(self):
        self._download_tp.iniciar()

    def get_download_ftp(self):
        return self._download_ftp

class Download_ftp:

    def __init__(self, arquivo, servidor):
        '''
            arquivo - dicionario com as informacoes dos arquivos para download
            servidor - objeto com as informacoes para conexao com servidor
        '''
        self._servidor = servidor
        self._arquivo = arquivo
        self._config = Configuracao()
        self._config_ftp()


    def msg_abrir_ftp(self):
        '''
        Mensagem para enviar ao servidor para abrir FTP
        '''
        comando = {'comando':'iniciar_ftp'}
        comando[self._arquivo['backup']] = ['path':self._arquivo['path'], 'nome':self._arquivo['nome']]

        return json.dumps(comando)

    def msg_fechar_ftp(self):

        comando = {'comando':'fechar_ftp'}
        comando['nome'] = self._arquivo['backup']

        return json.dumps(comando)

    def _config_ftp(self):
        self._ftp = ftplib.FTP(host=self._servidor.host, user=self._servidor.obj_ftp.usuario,
                                passwd=self._servidor.obj_ftp.senha)
        self._ftp.cwd(self._arquivo['path'])
        self._path_destino = self._config.get_backup_dir(self._servidor.name) + '/' + self._arquivo['nome']

    def iniciar(self):
        resultado = False
        try:
            self._ftp.retrbinary("RETR "+self._arquivo['nome'], open(self._path_destino, 'wb').write)
            resultado = True
        except:
            resultado = False


    def get_servidor(self):
        return self._servidor

    def get_arquivo(self):
        return self._arquivo
