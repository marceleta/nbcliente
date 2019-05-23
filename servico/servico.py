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

    def adicionar(self, servidor, lista_arquivos):
        '''
        servidor -  configuracao do servidor remoto
        arquivos - lista de arquivos para download
        '''
        print('lista_arquivos: {}'.format(lista_arquivos))
        path_destino = self._config.get_backup_dir(servidor.nome)
        print('path_destino: {}'.format(path_destino))
        print('gestao_download')
        print('lista_arquivos size: {}'.format(len(lista_arquivos)))
        arquivos = lista_arquivos['conteudo']
        for arquivo in arquivos:
            download_ftp = Download_ftp(arquivo, path_destino, servidor)
            thread = Download_thread(download_ftp, arquivo['backup'])
            self._download_em_espera[arquivo['backup']] = thread

    def get_downloads_executando(self):
        '''
            Quantos downloads estao executando
        '''
        return len(self._download_em_andamento)


    def executa_download(self, nome_backup):

        print('download_em_espera: index: {}'.format(self._download_em_espera.keys()))
        thread = self._download_em_espera[nome_backup]
        self._download_em_andamento.append(thread)
        del self._download_em_espera[nome_backup]
        thread.start()


    def _remove_download_finalizado(self):
        while self._loop_gestao:
            if len(self._download_em_andamento) > 0:
                tamanho_lista = len(self._download_em_andamento)
                print('tamanho_lista em andamento: {}'.format(tamanho_lista))
                for index in range(tamanho_lista):
                    thread = self._download_em_andamento[index]
                    print('remove: is_alive: {}'.format(thread.is_alive()))
                    print('remove: is_executado: {}'.format(thread.is_executado()))
                    if thread.is_executado():
                        self._download_finalizados.append(thread)
                        del self._download_em_andamento[index]
            print('tamanho_em_espera: {}'.format(len(self._download_em_espera)))
            print('tamanho_finalizados: {}'.format(len(self._download_finalizados)))
            print('tamanho_em_andamento: {}'.format(len(self._download_em_andamento)))


            time.sleep(10)


    def _iniciar_servicos(self):
        self._loop_gestao = True

        monitor_finalizado = Thread(target=self._remove_download_finalizado, name='monitor_finalizados')
        monitor_finalizado.start()
        self._thread_gestao.append(monitor_finalizado)

    def get_msg_em_espera(self):
        dicionario = None
        keys = list(self._download_em_espera.keys())
        selecao = keys[:1]

        for keys in selecao:
            thread = self._download_em_espera[keys]
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
        print('remove_finalizado {}'.format(nome_backup))
        for thread in self._download_finalizados:
            if nome_backup == thread.name:
                self._download_finalizados.remove(thread)

        #tamanho_lista = len(self._download_finalizados)

        #for index in range(tamanho_lista):
        #    thread = self._download_finalizados[index]
        #    if thread.name == nome_backup:
        #        del self._download_finalizados[index]

    def is_executando(self):
        return self._loop_gestao

    def parar_servicos(self):
        self._loop_gestao = False

    def is_download(self):
        is_espera = False
        if len(self._download_em_espera) > 0 and len(self._download_em_andamento) > 0 and len(self._download_finalizados) > 0:
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
        self._download_ftp = download_ftp
        self._is_executado = False

    def run(self):
        self._download_ftp.iniciar()
        self._is_executado = True

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
        resultado = False
        print('host: {}'.format(self._config_servidor.host))
        print('porta: {}'.format(self._config_servidor.porta))
        print('usuario: {}'.format(self._config_servidor.usuario))
        print('senha: {}'.format(self._config_servidor.senha))
        print('path: {}'.format(self._arquivo['path']))
        try:
            time.sleep(120)
            print('try ftp')
            self._ftp = ftplib.FTP('')
            self._ftp.connect(self._config_servidor.host, self._config_servidor.porta)
            self._ftp.login(user=self._config_servidor.usuario, passwd=self._config_servidor.senha)
            destino = self._path_destino + '/' + self._arquivo['arquivo']
            print('retrbinary')
            self._ftp.retrbinary("RETR "+self._arquivo['arquivo'], open(destino, 'wb').write)
            print('final retrbinary')
            resultado = True
        except ftplib.all_errors as msg:
            print('except: {}'.format(msg))
            resultado = False


    def get_servidor(self):
        return self._servidor

    def get_arquivo(self):
        return self._arquivo
