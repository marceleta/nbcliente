from backup.backup import Backup
from json_modelos.modelos import Servidor
import platform, os
import json


class Configuracao:

    def __init__(self):
        self.config_path()
        self._set_servidores()


    def _set_servidores(self):
        path = self.config_path() + 'json_modelos/servidores.json'
        self._lista_servidores = []
        if os.path.exists(path):
            arquivo = open(path, 'r')
            servidores = json.load(arquivo)
            keys = servidores.keys()
            for k in keys:
                dict_server = servidores[k]
                serv = Servidor(dict_server)
                self._lista_servidores.append(serv)

        else:
            self._lista_servidores = None

        return self._lista_servidores

        '''
        try:
            arquivo = open(path, 'r')
            servidores = json.loads(arquivo)
            keys = servidores.keys()
            for k in keys:
                dict_server = servidores[k]
                serv = Servidor(dict_server)
                self._lista_servidores.append(serv)
        except FileNotFound:
            self._lista_servidores = None
        '''

    def salvar_servidores(self, servidores):
        resposta = False
        path = config_path() + '/json_modelos/servidores.json'

        try:
            arquivo = open(path, 'w')
            arquivo.write(servidores)
            arquivo.close()
            resposta = True
        except FileNotFound:
            resposta = False

        return resposta



    def config_path(self):
        if platform.system() == 'Windows':
            self._path = 'c:/nbcliente/'
        else:
            self._path = '/home/marcelo/python/nbcliente/'

        return self._path

    @staticmethod
    def os_system():
        return platform.system()

    def get_servidores(self):
        return self._lista_servidores
'''
    def _verificar_banco(self):

        try:
            path_db = self.config_path() + 'db/nbcliente.db'
            arquivo = open(path_db)
            arquivo.close()
        except FileNotFoundError:
            Servidor.create_table()
            Backup.create_table()
'''
