import ftplib
from configuracao.config import Configuracao
from threading import Thread
import time
import json
from util.util import Log

class Gestao_download:

    def __init__(self):
        self._loop_gestao = True
        self._thread_gestao = []
        self._download_em_espera = []
        self._download_em_andamento = []
        self._download_finalizados = []
        self._iniciar_servicos()
        self._config = Configuracao()

    def adicionar(self, servidor, lista_arquivos):
        print('servidor: {}'.format(servidor))
        print('lista_arquivos: {}'.format(lista_arquivos))
        '''
        servidor -  configuracao do servidor remoto
        arquivos - lista de arquivos para download
        '''
        path_destino = self._config.get_backup_dir(servidor.nome)
        arquivos = lista_arquivos['conteudo']
        for arquivo in arquivos:
            download_ftp = Download_ftp(arquivo, path_destino, servidor)
            thread = Download_thread(download_ftp, arquivo['backup'])
            self._download_em_espera.append(thread)

        Log.info('Gestao download bkps adicionados, servidor: {}'.format(servidor.nome))
        

    def get_downloads_executando(self):
        '''
            Quantos downloads estao executando
        '''
        return len(self._download_em_andamento)


    def executa_download(self):

        thread_download = Thread(target=self.executa_thread_download, name='executa_downloads')
        thread_download.start()
        

    def executa_thread_download(self):
        print("executa_thread_download")
        print('len download_em_espera: {}'.format(len(self._download_em_espera)))
        print('len download_em_andamento: {}'.format(len(self._download_em_andamento)))

        loop = (len(self._download_em_espera) > 0)

        while loop:
            time.sleep(30)
            if len(self._download_em_andamento) == 0:
                thread = self._download_em_espera.pop()
                self._download_em_andamento.append(thread)
                thread.start()
                Log.info('iniciando thread {}'.format(thread.name))
            loop = (len(self._download_em_espera) > 0)
                      



    def _remove_download_finalizado(self):
        while self._loop_gestao:
            if len(self._download_em_andamento) > 0:
                tamanho_lista = len(self._download_em_andamento)
                for index in range(tamanho_lista):
                    thread = self._download_em_andamento[index]
                    if thread.is_executado():
                        self._download_finalizados.append(thread)
                        del self._download_em_andamento[index]
            
            time.sleep(10)


    def _iniciar_servicos(self):
        self._loop_gestao = True

        monitor_finalizado = Thread(target=self._remove_download_finalizado, name='monitor_finalizados')
        monitor_finalizado.start()
        self._thread_gestao.append(monitor_finalizado)
        Log.info('iniciando thread: monitor finalizados')

    def get_msg_em_espera(self):
        dicionario = None
        for thread in self._download_em_espera:
            dicionario = {
                'servidor':thread.get_download_ftp().get_servidor(),
                'mensagem':thread.get_download_ftp().msg_abrir_ftp()
            }

        return dicionario

    def get_msg_finalizados(self):
        lista_msg = []

        for thread in self._download_finalizados:
            download_ftp = thread.get_download_ftp()
            mensagem = {
                'servidor': download_ftp.get_servidor(),
                'comando':download_ftp.msg_fechar_ftp()
            }

            lista_msg.append(mensagem)

        return lista_msg

    def remove_finalizado(self, nome_backup):
        for thread in self._download_finalizados:
            if nome_backup == thread.name:
                self._download_finalizados.remove(thread)

    def is_executando(self):
        return self._loop_gestao

    def parar_servicos(self):
        self._loop_gestao = False

    def is_download(self):
        is_espera = False
        if len(self._download_em_espera) > 0 or len(self._download_em_andamento) > 0 or len(self._download_finalizados) > 0:
            is_espera = True

        return is_espera


    def is_servidos_exec(self):
        resposta = False
        for thread in self._thread_gestao:
            resposta = thread.is_alive()

        return resposta



class Download_thread(Thread):

    def __init__(self, download_ftp, nome):
        Thread.__init__(self, name=nome)
        self._nome = nome
        self._download_ftp = download_ftp
        self._is_executado = False

    def run(self):
        self._download_ftp.iniciar()
        self._is_executado = True
        Log.info('[download_thread] iniciando thread: {}'.format(self._nome))

    def get_download_ftp(self):
        return self._download_ftp

    def is_executado(self):
        return self._is_executado



class Download_ftp:

    def __init__(self, arquivo, path_destino, servidor):
        '''
            arquivo - dicionario com as informacoes dos arquivos para download
            servidor - objeto com as informacoes para conexao com servidor
        '''
        self._servidor = servidor
        self._config_servidor = servidor.obj_ftp
        self._arquivo = arquivo
        self._config = Configuracao()
        self._path_destino = path_destino

    def msg_abrir_ftp(self):
        '''
        Mensagem para enviar ao servidor para abrir FTP
        '''
        comando = {'comando':'iniciar_ftp',
                    'backup':{
                        'path':self._arquivo['path'],
                        'arquivo':self._arquivo['arquivo'],
                        'nome':self._arquivo['backup']
                    }
        }
        return comando

    def msg_fechar_ftp(self):

        comando = {'comando':'fechar_ftp'}
        comando['nome'] = self._arquivo['backup']
        comando['id_arquivo'] = self._arquivo['id']

        return comando


    def iniciar(self):
        print('FTP iniciado:')
        print('self._config_servidor.host: {}'.format(self._config_servidor.host))
        print('self._config_servidor.porta: {}'.format(self._config_servidor.porta))
        resultado = False
        try:
            time.sleep(5)
            self._ftp = ftplib.FTP('')
            self._ftp.connect(self._config_servidor.host, self._config_servidor.porta)
            self._ftp.login(user=self._config_servidor.usuario, passwd=self._config_servidor.senha)
            destino = self._path_destino + '/' + self._arquivo['arquivo']
            self._ftp.retrbinary("RETR "+self._arquivo['arquivo'], open(destino, 'wb').write)
            resultado = True
        except ftplib.all_errors as msg:
            print('FTP erro: {}'.format(msg))
            Log.info('[download_ftp] erro ftp: {}'.format(msg))
            resultado = False

    def get_servidor(self):
        return self._servidor

    def get_arquivo(self):
        return self._arquivo
