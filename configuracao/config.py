from backup.backup import Backup
import platform, os
import json
from util.util import Log
from json_modelos.modelos import Servidor, Servidor_local, Backup


class Configuracao:

    def __init__(self):
        self.config_path()
        self._set_servidores()
        self._set_backup_dir()
        self._set_servidor()


    def _set_servidores(self):
        path = self.config_path() + 'json_modelos/servidores.json'
        self._lista_servidores = []
        if os.path.exists(path):
            arquivo = open(path)
            servidores = json.load(arquivo)
            keys = servidores.keys()
            for k in keys:
                dict_server = servidores[k]
                serv = Servidor(dict_server)
                self._lista_servidores.append(serv)
        else:
            self._lista_servidores = None        

        Log.info('leitura do arquivo: servidores.json')

    def _set_servidor(self):
        path = self.config_path() + 'json_modelos/config_servidor.json'
        with open(path) as servidor:
            _json = json.load(servidor)
            s = _json['servidor_local']
            self._servidor = Servidor_local(s)

        Log.info('leitura do arquivo: config_servidores.json')


    def _set_backup_dir(self):
        path = self.config_path() +'configuracao/backup_dir.json'
        with open(path) as backup_dir:
            self._backup_dir = json.load(backup_dir)

        Log.info('leitura do arquivo: backup_dir.json')
        

    def salvar_servidores(self, servidores):
        resposta = False
        path = config_path() + 'json_modelos/servidores.json'

        try:
            arquivo = open(path, 'w')
            arquivo.write(servidores)
            arquivo.close()
            resposta = True
            Log.info('escrita no arquivo servidores.json')
        except FileNotFoundError:
            Log.error('erro ao escrever no arquivo servidores.json, FileNotFoundError')
            resposta = False        

        return resposta

    def get_servidor(self):
        return self._servidor

    def config_path(self):
        if platform.system() == 'Windows':
            self._path = 'c:/nbcliente/'
        else:
            self._path = '/home/marcelo/nbcliente/'

        return self._path

    @staticmethod
    def os_system():
        return platform.system()

    def get_servidores(self):
        return self._lista_servidores

    def get_backup_dir(self, nome_servidor):
        return self._backup_dir[nome_servidor]

    def get_backup_dir_path(self, nome_servidor):
        return self.get_backup_dir[nome_servidor]
