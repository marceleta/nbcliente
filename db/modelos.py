from peewee import *
import datetime
from util.util import Log
from configuracao.config import Configuracao
from util.util import Log

config = Configuracao()
path = config.config_path() + 'db/dbcliente.db'
db = SqliteDatabase(path)

class Persistir:

    @staticmethod
    def transacoes(nome_servidor, status, descricao):
        config = Transacoes()
        config.data_envio = datetime.datetime.now()
        config.nome_servidor = nome_servidor
        config.descricao = descricao
        config.status = status
        config.save()
        Log.info('transacao salva')

    @staticmethod
    def criar_db():
        try:
            arquivo = open(path)
            arquivo.close()
        except FileNotFoundError:
            Transacoes.create_table()
            Log.info('criando banco de dados')


class BaseModel(Model):
    class Meta:
        database = db

class Transacoes(BaseModel):

    data_envio = DateTimeField()
    nome_servidor = CharField(max_length=50)
    status = CharField(max_length=10)
    descricao = CharField(max_length=200)
