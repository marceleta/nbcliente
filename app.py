import json
from json_modelos.modelos import Servidor, Conversor

arquivo = open('json_modelos/servidores.json')
srv_json = json.load(arquivo)

modelo = {
    'nome':'servidor1',
    'descricao':'descricao1',
    'host':'host',
    'porta':'5000',
    'backups':[]
}

keys = srv_json.keys()
s1 = Servidor(srv_json['servidor1'])
s2 = Servidor(srv_json['servidor2'])


lista = [s1, s2]
c = Conversor.modelo_json(lista)
print(c['servidor1'])
