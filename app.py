import json
import time
from json_modelos.modelos import Servidor, Conversor
from comunicacao.nbservidor import ConexaoThread

comando = {
    'comando':'nada'
}
mensagem = json.dumps(comando)
thread1 = ConexaoThread('localhost', 5000, mensagem)
comando['comando'] = 'mensagem2'
mensagem = json.dumps(comando)
thread2 = ConexaoThread('localhost', 5000, mensagem)

lista_thread = [thread1, thread2]
for thread in lista_thread:
    thread.start()
loop = True
contagem = 0
while loop:

    if not thread1.is_alive():
        loop = False
        print('mensagem: {}'.format(thread1.get_mensagem()))

    if not thread2.is_alive():
        loop = False
        print('mensagem: {}'.format(thread2.get_mensagem()))

    time.sleep(3)

    print(contagem)
    contagem = contagem + 1

    if contagem == 3:
        loop = False




'''
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
'''
