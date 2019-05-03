from peewee import *
import datetime
from configuracao.config import Configuracao
from modelos.modelos import Controle
from util.util import DataConv

class ControleApp:

    def __init__(self):
        self._controle = Controle()



    def _verf_envio_bkp_list(self):
        data_hoje = DataConv.data_hoje()
        ctrl_data = self._controle.busca_por_data(data_hoje)

        if ctrl != None:
            
