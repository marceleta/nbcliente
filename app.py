import json
import time
from json_modelos.modelos import Servidor, Conversor
from comunicacao.nbservidor import ConexaoThread
from configuracao.config import Configuracao


c = Configuracao()

servidores = c.get_servidores()

servidor = servidores[0]
dict_mensagem = {
    'comando':'update_list_bkps'
}
dict_mensagem['backup'] = servidor.backups
mensagem = json.dumps(dict_mensagem)
print(mensagem)
