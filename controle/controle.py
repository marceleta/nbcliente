from peewee import *
import datetime
from configuracao.config import Configuracao
from modelos.modelos import Controle
from util.util import DataConv

class ControleApp:

    def __init__(self):
        self._config = Configuracao()

    def set_data(self, data):
        self._data = data
        self._decode_data(self._data)

    def _decode_data(self, data):
        if data:
            self._mensagem = data.decode('utf-8')

    def is_data(self):
        is_data = True
        if not self._data:
            is_data = False

        return is_data

    def processar_mensagem(self):
        data_json = json.loads(self._data.decode('utf-8'))
        comando = data_json['comando']
        del data_json['comando']
        print('comando: {}'.format(comando))

        if comando == 'lst_bkps_update':
            self._atualizar_lst_bkps(data_json)

        else:
            print('comando nao encontrado')

    def _atualizar_lst_bkps(self, data_json):
        self._config.salvar_servidores()
        self._resposta = 'ok'

    def _converter_para_classe(self, )

    def enviar_resposta(self):
        return self._resposta.encode('utf-8')
