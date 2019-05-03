import json
from comunicacao.cliente import Cliente
from backup.backup import Backup, Backup_dict
from configuracao.config import Configuracao

config = Configuracao()
print(config.get_backup()[0].nome)




'''
ip = '127.0.0.1'
porta = 5000

data = {
    "comando":"bkp_list"
}

data_json = json.dumps(data)

cliente = Cliente(ip, porta)
cliente.enviar_mensagem(data_json)
msg = cliente.receber_mensagem()
msg_json = json.loads(msg)

b_dict = Backup_dict.get_dict(msg_json)
print(type(b_dict))
b_dict['comando'] = 'add_backup_list'
print(b_dict['comando'])
'''
'''
msg_json = json.loads(msg)

backup_1 = msg_json[0]
backup_2 = msg_json[1]

print(str(backup_1))
print(str(backup_2))


arquivo = open('backup_list.json', 'w')
arquivo.write(str(msg_json[0]))
arquivo.close()
'''
