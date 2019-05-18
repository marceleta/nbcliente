from peewee import *
import datetime
from configuracao.config import Configuracao

config = Configuracao()
path = config.config_path() + 'db/dbcliente.db'
db = SqliteDatabase(path)

class Persistir:

    @staticmethod
    def config_enviadas(nome_servidor, status):
        config = Config_enviadas()
        config.data_envio = datetime.datetime.now()
        config.nome_servidor = nome_servidor
        config.status = status
        config.save()

class BaseModel(Model):
    class Meta:
        database = db

class Config_enviadas(BaseModel):

    data_envio = DateTimeField()
    nome_servidor = CharField(max_length=50)
    status = CharField(max_length=10)
