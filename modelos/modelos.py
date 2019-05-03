from peewee import *
import datetime
from configuracao.config import Configuracao

path_db = Configuracao.config_path() + 'db/nbcliente.db'
db = SqliteDatabase(path_db)

class BaseModel(Model):
    class Meta:
        database = db

class Controle(BaseModel):

    ultimo_envio_bkp = DateTimeField()

    def busca_por_data(self, data):

        ctrl = None
        try:
            controle = Controle.get(Controle.envio_bkp_list=data)
        except DoesNotExist:
            ctrl = None

        return ctrl

class Servidor(BaseModel):

    nome = CharField(max_length=40)
    host = CharField(max_length=100)
    porta = IntegerField()
    qtd_conexoes = IntegerField()

    def dict_servidor(self):

        json = {
            'nome':nome,
            'host':host,
            'porta':porta,
            'qtd_conexoes':qtd_conexoes
        }


class Backup(BaseModel):

    nome = CharField(max_length=100)
    backup_auto = CharField(max_length=3)
    path_origem = CharField(max_length=100)
    path_destino = CharField(max_length=100)
    tipo = CharField(max_length=10)
    fonte = CharField(max_length=200)
    periodo = CharField(max_length=100)
    dia_semana = CharField(max_length=30)
    hora_execucao = DateTimeField()
    sc_backup = CharField()
    sc_pre_execucao = CharField()
    sc_pos_execucao = CharField()

    servidor = ForeignField(Servidor, backref='servidor')

    def dict_backup(self):
        bkp = {
            'nome':nome,
            'backup_auto':backup_auto,
            'path_origem':path_origem,
            'path_destino':path_destino,
            'tipo':tipo,
            'fonte':fonte,
            'periodo':periodo,
            'dia_semana':dia_semana,
            'hora_execucao':hora_execucao,
            'sc_backup':sc_backup,
            'sc_pre_execucao':sc_pre_execucao,
            'sc_pos_execucao':sc_pos_execucao
            }

        return bkp
