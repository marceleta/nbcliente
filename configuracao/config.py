from backup.backup import Backup
import platform
import json
from modelos.modelos import Backup, Servidor, Controle

class Configuracao:

    def __init__(self):
        self.config_path()
        self._set_backup()
        self._verificar_banco()


    def _set_backup(self):

        path_backup = self._path + 'backup/backup_list.json'
        with open(path_backup) as backup_json:
            data = json.load(backup_json)
            b = data['backup']
            self._backup_list = []
            for i in b:
                self._backup = Backup(i)
                self._backup_list.append(self._backup)

    @staticmethod
    def config_path():
        if self.os_system() == 'Windows':
            self._path = 'c:/nbcliente/'
        else:
            self._path = '/home/marcelo/python/nbcliente/'

    @staticmethod
    def os_system():
        return platform.system()

    def get_backup(self):
        return self._backup_list

    def _verificar_banco(self):

        try:
            path_db = self.config_path() + 'db/nbcliente.db'
            arquivo = open(path_db)
            arquivo.close()
        except FileNotFoundError:
            Controle.create_table()
            Servidor.create_table()
            Backup.create_table()
