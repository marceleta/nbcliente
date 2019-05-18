import ftplib
from configuracao.config import Configuracao
from threading import Thread
import time
import json

class Gestao_download:

    def __init__(self):
        self._loop_gestao = True
        self._thread_gestao = []
        self._download_em_espera = {}
        self._download_em_andamento = []
        self._download_finalizados = []
        self._iniciar_servicos()
        self._config = Configuracao()

    def adicionar(self, servidor, arquivos):
        path_destino = self._config.get_backup_dir(servidor.nome)
        print('path_destino: {}'.format(path_destino))
        print('gestao_download')
        lista_arquivos = arquivos['conteudo']
        print('lista_arquivos size: {}'.format(len(lista_arquivos)))
        for arquivo in lista_arquivos:
            download_ftp = Download_ftp(arquivo, path_destino, servidor)
            thread = Download_thread(download_ftp, arquivo['backup'])
            self._download_em_espera[arquivo['backup']] = thread

    def _monitor_downloads_executando(self):
        '''
            monitora que nao mais que nao dois downloads ao mesmo tempo
        '''
        while self._loop_gestao:
            self._numero_execucoes = 0
            for thread in self._download_em_andamento:
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
        self._download_ftp.iniciar()

    def get_download_ftp(self):
        return self._download_ftp



class Download_ftp:

    def __init__(self, arquivo, path_destino, config_servidor):
        '''
            arquivo - dicionario com as informacoes dos arquivos para download
            servidor - objeto com as informacoes para conexao com servidor
        '''
        self._config_servidor = config_servidor
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
        #comando[self._arquivo['backup']] = {
        #                        'path':self._arquivo['path'],
        #                        'nome':self._arquivo['nome']
        #                        }


        return comando

    def msg_fechar_ftp(self):

        comando = {'comando':'fechar_ftp'}
        comando['nome'] = self._arquivo['backup']

        return json.dumps(comando)


    def iniciar(self):
        resultado = False
        print('host: {}'.format(self._config_servidor.host))
        print('porta: {}'.format(self._config_servidor.porta))
        print('usuario: {}'.format(self._config_servidor.usuario))
        print('senha: {}'.format(self._config_servidor.senha))
        print('path: {}'.format(self._arquivo['path']))
        try:
            print('try ftp')
            self._ftp = ftplib.FTP('')
            self._ftp.connect(self._config_servidor.host, self._config_servidor.porta)
            self._ftp.login(user=self._config_servidor.usuario, passwd=self._config_servidor.senha)
            resposta = self._ftp.retrlines('LIST')
            print(resposta)
            #path_destino = self._config.get_backup_dir(self._config_servidor.name) + '/' + self._arquivo['arquivo']
            destino = self._path_destino + '/' + self._arquivo['arquivo']
            self._ftp.retrbinary("RETR "+self._arquivo['arquivo'], open(destino, 'wb').write)

            resultado = True
        except ftplib.all_errors as msg:
            print('except: {}'.format(msg))
            resultado = False


    def get_servidor(self):
        return self._servidor

    def get_arquivo(self):
        return self._arquivo
